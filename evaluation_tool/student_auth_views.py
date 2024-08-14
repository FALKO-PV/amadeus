from django.contrib import messages
from evaluation_tool.models import NWFGEvaluation, NWFGEvaluationPart, NWFGSingleEvaluation, NWFGEvaluationAcronym
from django.shortcuts import render, redirect
from .scripts.get_subject_color import get_subject_color
from .scripts.pool_creation import create_items_for_new_single_evaluation
from django.http import HttpResponse
from collections import Counter
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_control
import re

def show_error_page(request, hint_text):
    context = {}
    context["hint_text"] = hint_text
    return render(request, 'evaluation_tool/pages/error-page.html', context)

def redirect_user_for_new_auth(request, evaluation_id):
    # The student should then also be informed that he has already entered the wrong acronym three times.
    messages.success(request, 'Du hast bereits zum dritten Mal ein Muster eingegeben, das es nicht gibt.<br><b>Jetzt kannst du ein neues Muster auswählen, um an der Evaluation teilzunehmen</b>. Falls du dich doch wieder an dein Muster erinnerst, klicke auf „Zurück zur Startseite“!')

    return redirect("new-auth-student-page", evaluation_id=evaluation_id)
    # return render(request, 'evaluation_tool/pages/new-auth-student-page.html', context)


def get_current_pool_statistics(nwfg_evaluation_id):
    """
    This method will calculate how often each of the three pools have been linked to a student in one NWFG Evaluation.
    return might look like that: {'1': '7', '2': '7', '3': '6'}
    nwfg_evaluation_parts: all 9 NWFGEvaluationPart(s)
    :param nwfg_evaluation_parts: dict
    :return: pool_stats: dict
    """
    pool_stats = dict()  # check which pool (1-3) occurs how often
    acronym_pool_map = dict()

    nwfg_evaluation_acronyms = NWFGEvaluationAcronym.objects.filter(nwfg_evaluation_id=nwfg_evaluation_id)
    
    for nwfg_evaluation_acronym in nwfg_evaluation_acronyms:
        acronym_pool_map[nwfg_evaluation_acronym.acronym] = nwfg_evaluation_acronym.pool

    pool_stats = dict(Counter(acronym_pool_map.values()))
    pool_stats = {str(k): v for k, v in pool_stats.items()}

    if not ("1" in pool_stats):
        pool_stats["1"] = 0
    if not ("2" in pool_stats):
        pool_stats["2"] = 0
    if not ("3" in pool_stats):
        pool_stats["3"] = 0

    return pool_stats


@cache_control(no_cache=True, must_revalidate=True)
def get_auth_student_page(request, evaluation_id):
    """
    This method is used to present the page for re-selecting a pattern in case the student has already participated in a Befragungsrunde of the NWFG evaluation.

    :param request: django specific
    :param evaluation_id: UUID
    :return: render, redirect or HttpResponse at error
    """
    context = {}
    try:
        class_evaluation = NWFGEvaluation.objects.get(
            nwfg_evaluation_id=evaluation_id)
        context["subject_color"] = get_subject_color(class_evaluation.subject)
        context["class_evaluation_id"] = class_evaluation.pk

        evaluation_completed = class_evaluation.completed

        nwfg_evaluation_parts = NWFGEvaluationPart.objects.filter(
            nwfg_evaluation=evaluation_id)
        
        if len(nwfg_evaluation_parts) == 0:
            return show_error_page(request, "Es ist noch nicht möglich, an einer Evaluation teilzunehmen.")
        
        if evaluation_completed:
            return show_error_page(request, "Diese Evaluation ist nicht mehr verfügbar.")

    except ObjectDoesNotExist:
        return show_error_page(request, "Diese Evaluation gitb es nicht.")

    if request.method == "GET":
        return render(request, 'evaluation_tool/pages/auth-student-page.html', context)

    if request.method == "POST":
        input_acronym = request.POST.get("acronym")
        redirect_to_form = bool(request.POST.get("redirect-to-question-page-bool"))

        # check if entered acronym is valid
        if bool(re.match(r'\b[1-6]{5}\b', input_acronym)) and len(input_acronym) == 5:
            acronym_is_valid = True
        else:
            acronym_is_valid = False
            # This error should actually be prevented by the front-end, since there are only six images per question.
            context["error_text"] = "Das von dir gewählte Muster gibt es nicht!"
            return render(request, 'evaluation_tool/pages/auth-student-page.html', context)

        # check if acronym has been used before in the whole evaluation with the given nwfg-code
        used_acronyms = [acronym_object.acronym for acronym_object in NWFGEvaluationAcronym.objects.filter(nwfg_evaluation=evaluation_id)]
        similar_acronyms = []

        # change input acronym to valid acronym if there's exactly one acronym in the database with at least three similar characters(=selected images)
        if not(input_acronym in used_acronyms):
            for acronym in used_acronyms:
                n_similar_images = 0
                for i in range(0, len(input_acronym)):
                    if acronym[i] == input_acronym[i]:
                        n_similar_images += 1
                    if i == len(input_acronym) - 1:
                        if n_similar_images >= 3:
                            similar_acronyms.append(acronym)
            if len(similar_acronyms) == 1:
                input_acronym = similar_acronyms[0]
                
        if not (input_acronym in used_acronyms):
            context["error_text"] = "Das von dir gewählte Muster wurde nicht gefunden." \
                                    " Gib bitte dein Muster ein, das du bei deiner ersten Anmeldung erstellt hast. Falls du dich nicht mehr an dein Muster erinnern kannst, wende dich an deine Lehrkraft."
            return render(request, 'evaluation_tool/pages/auth-student-page.html', context)

        # check if there is an evaluation (one of 9) in which the student can participate in at the moment
        # (might be stopped by teacher)
        try:
            # to determine which survey is currently available, we need to check which one is not yet completed.
            # An evaluation is completed as soon as it is finished or the next one of the nine has been started.
            current_nwfg_evaluation_part = NWFGEvaluationPart.objects.get(
                nwfg_evaluation=evaluation_id, completed=False)
            evaluation_part_is_available = True

        except ObjectDoesNotExist:
            evaluation_part_is_available = False
            context["error_text"] = "Es gibt derzeit keine Befragungsrunde, an der du teilnehmen kannst."
            return render(request, 'evaluation_tool/pages/auth-student-page.html', context)

        # If all conditions (acronym not yet assigned, acronym valid and that a Befragungsrunde is currently available)
        # are fulfilled, a new single evaluation and items can be created or the user can be forwarded to his evaluation
        # page to continue answering the questions.
        if input_acronym in used_acronyms and acronym_is_valid and evaluation_part_is_available:
            # Check if student is already registered for current "befragungsrunde", then forward it
            try:
                nwfg_evaluation_acronym = NWFGEvaluationAcronym.objects.get(nwfg_evaluation=class_evaluation, acronym=input_acronym)
                existing_single_evaluation_with_input_acronym_in_current_nwfg_evaluation_part = NWFGSingleEvaluation.objects.get(
                    nwfg_evaluation_part=current_nwfg_evaluation_part, acronym=nwfg_evaluation_acronym)

                context["input_acronym"] = input_acronym
                context["nwfg_single_evaluation_id"] = existing_single_evaluation_with_input_acronym_in_current_nwfg_evaluation_part.pk
                if redirect_to_form:
                    return redirect("evaluation-form-page", evaluation_id=evaluation_id,
                                    single_evaluation_id=existing_single_evaluation_with_input_acronym_in_current_nwfg_evaluation_part.pk)
                
                # We would like to provide the template with the information whether the acronym has been newly selected or not (register vs. login process)
                context["acronym_registration"] = False
                return render(request, 'evaluation_tool/pages/show-pattern-page.html', context)

            except ObjectDoesNotExist:
                # If the student is not registered for the current  "befragungsrunde" we need to create a new
                # NWFGSingleEvaluation. Because input_acronym is in used_acronyms, we know that the participant already
                # took part in the given NWFGEvaluation (consisting of nine "Befragungsrunden")
                # First, we need to check which pool that user has been linked to before.
                nwfg_evaluation_acronym = NWFGEvaluationAcronym.objects.get(
                    nwfg_evaluation_id=class_evaluation, acronym=input_acronym
                )

                new_nwfg_single_evaluation = NWFGSingleEvaluation.objects.create(
                    acronym=nwfg_evaluation_acronym,
                    nwfg_evaluation_part=current_nwfg_evaluation_part
                )

                create_items_for_new_single_evaluation(
                    is_nwfg=True,
                    nwfg_evaluation_acronym=nwfg_evaluation_acronym,
                    single_evaluation=new_nwfg_single_evaluation,
                    evaluation_part=current_nwfg_evaluation_part,
                    class_evaluation=class_evaluation
                )
                context["input_acronym"] = input_acronym
                context["nwfg_single_evaluation_id"] = new_nwfg_single_evaluation.pk

                if redirect_to_form:
                    return redirect(
                        "evaluation-form-page",
                        evaluation_id=evaluation_id,
                        single_evaluation_id=new_nwfg_single_evaluation.pk
                    )

                return render(request, 'evaluation_tool/pages/show-pattern-page.html', context)


# Source for decorator: https://stackoverflow.com/questions/6923027/disable-browser-back-button-after-logout 
@cache_control(no_cache=True, must_revalidate=True)
def get_new_auth_student_page(request, evaluation_id):
    """
    This method is used to present the page for selecting a pattern in case the student hasn't yet participated in a Befragungsrunde of the NWFG evaluation.

    :param request: django specific
    :param evaluation_id: UUID
    :return: render, redirect or HttpResponse at error
    """
    context = {}
    try:
        class_evaluation = NWFGEvaluation.objects.get(
            nwfg_evaluation_id=evaluation_id)
        context["subject_color"] = get_subject_color(class_evaluation.subject)
        context["class_evaluation_id"] = class_evaluation.pk
        context["nwfg_code"] = class_evaluation.nwfg_code

        evaluation_completed = class_evaluation.completed

        nwfg_evaluation_parts = NWFGEvaluationPart.objects.filter(nwfg_evaluation=evaluation_id)
        
        if len(nwfg_evaluation_parts) != 0:
            return show_error_page(request, "Es ist nicht möglich, nachträglich ein Muster zu registrieren.")

        if evaluation_completed:
            return show_error_page(request, "Diese Evaluation ist nicht mehr verfügbar.")

    except ObjectDoesNotExist:
        return show_error_page(request, "Diese Evaluation gibt es nicht.")

    if request.method == "GET":
        return render(request, 'evaluation_tool/pages/new-auth-student-page.html', context)

    if request.method == "POST":
        input_acronym = request.POST.get("acronym")

        # check if entered acronym is valid
        if bool(re.match(r'\b[1-6]{5}\b', input_acronym)) and len(input_acronym) == 5:
            acronym_is_valid = True
        else:
            acronym_is_valid = False
            # This error should actually be prevented by the front-end, since there are only six images per question.
            context["error_text"] = "Das von dir gewählte Muster gibt es nicht!"

        # check if acronym has been used before in the whole evaluation with the given nwfg-code
        used_acronyms = [acronym_object.acronym for acronym_object in NWFGEvaluationAcronym.objects.filter(nwfg_evaluation=evaluation_id)]
        if input_acronym in used_acronyms:
            context["error_text"] = "Das von dir ausgewählte Muster wurde bereits von jemand anderem ausgewählt. Bitte wähle ein anderes Muster aus."


        if not (input_acronym in used_acronyms) and acronym_is_valid:
            # Check which pool has the lowest amount of students
            pool_stats = get_current_pool_statistics(class_evaluation.pk)

            if len(pool_stats) > 0:
                pool_with_lowest_amount_of_participants = min(
                    pool_stats, key=pool_stats.get)
            else:
                pool_with_lowest_amount_of_participants = 1
            
            new_nwfg_evaluation_acronym = NWFGEvaluationAcronym.objects.create(acronym=input_acronym, pool=pool_with_lowest_amount_of_participants, nwfg_evaluation=class_evaluation)
            
            # We would like to provide the template with the information whether the acronym has been newly selected or not (register vs. login process)
            context["acronym_registration"] = True
            context["input_acronym"] = input_acronym
            context["school_type"] = class_evaluation.school_type

            return render(request, 'evaluation_tool/pages/show-pattern-page.html', context)

        return render(request, 'evaluation_tool/pages/new-auth-student-page.html', context)
