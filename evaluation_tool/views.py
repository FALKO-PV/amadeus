import os
from evaluation_tool.scripts.email_handler import send_mail_finished_class_evaluation, \
    send_mail_finished_nwfg_evaluation, send_mail_new_class_evaluation, send_mail_new_nwfg_evaluation, \
    send_mail_new_nwfg_evaluation_round
from evaluation_tool.scripts.pool_creation import create_items_for_new_single_evaluation
from .scripts.create_qr_code_as_svg_string import create_qr_code_as_svg_string
from evaluation_tool.models import ClassEvaluation, Item, NWFGEvaluation, NWFGEvaluationPart, NWFGItem, \
    NWFGSingleEvaluation, SingleEvaluation, NWFGEvaluationAcronym
from .scripts.validate_email import validate_email
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from .forms import ItemsForm, NewEvaluationForm, DownloadForm
from .scripts.get_subject_color import get_subject_color
from .scripts.time_range_is_valid import time_range_is_valid
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from evaluation_tool.scripts.data_analysis import DataAnalyzer
from evaluation_tool.scripts.pdf_writer import PdfWriter
from evaluation_tool.scripts.data_exporter import ExcelExporter, create_excel_export, full_data_export
from six.moves.urllib.parse import urlparse
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.db import transaction
from dotenv import load_dotenv
import json
import datetime
import io
import logging
import time
import re

logger = logging.getLogger('main')

# load environment variables
load_dotenv("../.env")

def get_start_page(request):
    return render(request, 'evaluation_tool/pages/start-page.html')


def show_error_page(request, hint_text):
    context = {}
    context["hint_text"] = hint_text
    logger.error(hint_text)
    return render(request, 'evaluation_tool/pages/error-page.html', context)


def page_not_found_view_404(request, exception):
    relative_path = urlparse(request.build_absolute_uri()).path
    logger.error("404 not found! " + relative_path)
    return show_error_page(request, "Unbekannter Pfad " + relative_path)


def get_create_evaluation_page(request):
    """
    This method processes requests to the page that is used to let teachers create a new evaluation. 
    For a POST-request, the method checks whether all entries are valid and for a GET-request, the empty input form is send to the client.
    :param request: django specific
    :return: render, redirect at error
    """
    context = {"start_evaluation_immediately": True}

    if request.method == "POST":
        nwfg_pattern = r"^(ENG|GER|LAT|MAT|MUS|REL)\d{12}$"
        subject_mapping = {
          "ENG": "Englisch",
          "GER": "Deutsch",
          "LAT": "Latein",
          "MAT": "Mathematik",
          "MUS": "Musik",
          "REL": "Evangelische Religion"
        }

        form = NewEvaluationForm(request.POST)
        error_text = ""

        is_for_nwfg_study = form["is_for_nwfg_study"].value()
        nwfg_code = form["nwfg_code"].value()
        context["start_evaluation_immediately"] = form["start_evaluation_immediately"].value()

        context["is_for_nwfg_study"] = is_for_nwfg_study
        context["nwfg_code"] = nwfg_code

        # Validate E-Mail
        email = form["email"].value()
        validate_email_tuple = validate_email(email)
        valid_email = validate_email_tuple[0]
        error_text_email_validation = validate_email_tuple[1]
        if valid_email:
            context["email"] = email
        else:
            error_text = error_text_email_validation

        # Teacher's name
        teacher_name = form["teacher_name"].value()
        if len(teacher_name) <= 200:
            valid_teacher_name = True
            context["teacher_name"] = teacher_name
        else:
            error_text = "Bitte geben Sie einen gültigen Namen der Lehrkraft ein (maximal 200 Zeichen)!"
            logger.warning(f"{teacher_name} kein gültiger Name")
            valid_teacher_name = False

        # Validate subject
        subject = form["subject"].value()
        if (subject == "Allgemeine Lehrevaluation" and not is_for_nwfg_study) or subject == "Deutsch" or \
                subject == "Englisch" or subject == "Evangelische Religion" or subject == "Latein" or \
                subject == "Mathematik" or subject == "Musik":
            valid_subject = True
            context["subject"] = subject
        else:
            error_text = "Bitte geben Sie ein gültiges Unterrichtsfach ein!"
            valid_subject = False

        # Validate context of use
        context_of_use = form["context_of_use"].value()
        if context_of_use in ["US", "UA", "P", "T", "S"]:
            valid_context_of_use = True
            context["context_of_use"] = context_of_use
        else:
            error_text = "Bitte geben Sie einen gültigen Nutzungskontext an!"
            valid_context_of_use = False        

        # Validate data processing consent
        data_consent_checked = form["allow_data_processing"].value()

        if data_consent_checked == False:
            error_text = "Bitte stimmen Sie der Einwilligungserklärung zur Datenverarbeitung zu."
            logger.warning("Der Einwilligungserklärung wurde nicht zugestimmt.")
            valid_consent = False
        else:
            valid_consent = True

        if is_for_nwfg_study:  # Block for NWFG Study
            if not(NWFGEvaluation.objects.filter(nwfg_code=nwfg_code).exists()) and re.match(nwfg_pattern, nwfg_code):
                if subject_mapping[nwfg_code[:3]] == subject:
                   valid_nwfg_code = True
                else:
                    valid_nwfg_code = False
                    error_text = "Der von Ihnen eingegebene NWFG-Code passt nicht zu dem Unterrichtsfach, das von Ihnen ausgewählt wurde!"
            else:
                valid_nwfg_code = False
                error_text = "Der von Ihnen eingegebene NWFG-Code passt nicht zu dem Unterrichtsfach, das von Ihnen ausgewählt wurde!"

            if valid_nwfg_code and valid_email and valid_teacher_name and valid_subject and valid_subject and valid_consent:

                if form.is_valid():

                    nwfg_evaluation = NWFGEvaluation.objects.create(
                        nwfg_code=nwfg_code,
                        teacher_name=teacher_name,
                        email=email,
                        subject=subject,
                    )

                    send_mail_new_nwfg_evaluation(
                        class_evaluation=nwfg_evaluation.pk,
                        status_code=nwfg_evaluation.status_url_token,
                        subject=nwfg_evaluation.subject,
                        to_email_address=nwfg_evaluation.email,
                    )

                    messages.success(request, email)

                    print("Successfully created NWFG Evaluation with PK", nwfg_evaluation.pk)
                    logger.info(f"NWFG Evaluation mit ID {nwfg_evaluation.pk} angelegt.")
                    return redirect("evaluation/" + str(nwfg_evaluation.nwfg_evaluation_id) + "/share")

                else:
                    logger.warning("CAPTCHA beim Anlegen einer NWFG Evaluation nicht gelöst.")
                    error_text = "Die eingegebenen Zeichen der CAPTCHA-Sicherheitsprüfung sind nicht korrekt!"

        else:  # Block for non NWFG study
            valid_time_range, start_evaluation_immediately, evaluation_start, evaluation_end = time_range_is_valid(
                form["start_evaluation_immediately"].value(), form["evaluation_start"].value(),
                form["evaluation_end"].value()
            )
            if not valid_time_range:
                logger.warning("Keine gültige Zeitspanne angegeben beim Erstellen einer ClassEvaluation.")
                error_text = "Bitte geben Sie einen gültigen Zeitraum an, in dem die Umfrage für die Schüler:innen " \
                             "verfügbar sein soll. Dieser Zeitraum darf nicht in der Vergangenheit liegen und muss " \
                             "zwischen 24 Stunden und 30 Tagen lang sein!"

            if valid_email and valid_teacher_name and valid_subject and valid_context_of_use and valid_time_range and valid_consent:

                if form.is_valid():
                    evaluation = ClassEvaluation.objects.create(
                        evaluation_start=evaluation_start,
                        evaluation_end=evaluation_end,
                        start_evaluation_immediately=start_evaluation_immediately,
                        teacher_name=teacher_name,
                        email=email,
                        subject=subject,
                        context_of_use=context_of_use
                    )

                    send_mail_new_class_evaluation(
                        class_evaluation=evaluation.pk,
                        to_email_address=evaluation.email,
                        status_code=str(evaluation.status_url_token),
                        evaluation_end=evaluation.evaluation_end,
                        subject=evaluation.subject,
                    )

                    messages.success(request, email)

                    print("Successfully created Evaluation with PK",
                          evaluation.class_evaluation_id
                          )
                    logger.info(
                        f"ClassEvaluation mit ID {evaluation.class_evaluation_id} im Fach {evaluation.subject} angelegt.")
                    return redirect("evaluation/" + str(evaluation.class_evaluation_id) + "/share")
                else:
                    logger.warning("CAPTCHA bei Erstellung ClassEvaluation nicht gelöst.")
                    error_text = "Die eingegebenen Zeichen der CAPTCHA-Sicherheitsprüfung sind nicht korrekt!"

        context["error_text"] = error_text

    form = NewEvaluationForm()
    context['form'] = form
    return render(request, 'evaluation_tool/pages/create-evaluation-page.html', context)


def get_datenschutzhinweise_page(request):
    return render(request, 'evaluation_tool/pages/datenschutzhinweise.html')


def get_impressum_page(request):
    return render(request, 'evaluation_tool/pages/impressum.html')

def get_evaluation(evaluation_id):
    try:
        return ClassEvaluation.objects.get(class_evaluation_id=evaluation_id)
    except ObjectDoesNotExist:
        try:
            return NWFGEvaluation.objects.get(nwfg_evaluation_id=evaluation_id)
        except ObjectDoesNotExist:
            return None

def get_share_page(request, evaluation_id):
    """
    This method is used to show the QR code to students so that they can participate in an evaluation.
    The QR code is transferred to the client as an SVG string. The evaluation_id (primary key) of the evaluation is part of the URL.
    The QR code should then be displayed for participating in the evaluation with this evaluation_id.

    :param request: django specific
    :param evaluation_id: UUID of evaluation
    :return: render object, HttpResponse at error
    """
    if request.method == "GET":
        evaluation = get_evaluation(evaluation_id)

        if evaluation is None:
            logger.warning(f"Ungültige Evaluations ID aufgerufen! {evaluation_id}")
            return show_error_page(request, "Diese Evaluation gibt es nicht.")

        if evaluation.completed or (hasattr(evaluation, 'evaluation_end') and evaluation.evaluation_end < datetime.datetime.now()) or evaluation.deleted:
            logger.warning(f"Nicht mehr verfügbare Evaluation aufgerufen! {evaluation.pk}")
            return show_error_page(request, "Diese Evaluation ist nicht mehr verfügbar.")

        qr_code_url = os.getenv("WEBSITE_URL") + "evaluation/" + evaluation_id
        qr_code_svg_string = create_qr_code_as_svg_string(qr_code_url)

        context = {
            "qr_code_svg_string": qr_code_svg_string,
            "share_url": qr_code_url,
            "class_evaluation_id": evaluation_id,
            "subject_color": get_subject_color(getattr(evaluation, 'subject', None))
        }

        return render(request, 'evaluation_tool/pages/share-page.html', context)


def get_start_evaluation(request, evaluation_id):
    """
    This method is used to process requests on the evaluation participation page.
    So this is the page a student will get to if she/he has scanned the QR code.
    For evaluations with NWFG code, there is the possibility to participate with a new acronym or with an acronym that has already been used in a previous "Befragungsrunde".

    :param request: django specific
    :param evaluation_id: UUID of evaluation
    :return: render object or redirect, HttpResponse at Error
    """
    context = {}
    evaluation = get_evaluation(evaluation_id)

    if evaluation is None:
        logger.warning(f"Ungültige Evaluations ID aufgerufen! {evaluation_id}")
        return show_error_page(request, "Diese Evaluation gibt es nicht.")

    is_nwfg_evaluation = isinstance(evaluation, NWFGEvaluation)
    context["is_nwfg_evaluation"] = is_nwfg_evaluation
    context["subject_color"] = get_subject_color(getattr(evaluation, 'subject', None))

    evaluation_completed = evaluation.completed
    evaluation_end_reached = getattr(evaluation, 'evaluation_end', None) and evaluation.evaluation_end < datetime.datetime.now()

    if evaluation_completed or evaluation_end_reached or getattr(evaluation, 'deleted', False):
        logger.warning(f"Nicht mehr verfügbare Evaluation aufgerufen! {evaluation.pk}")
        return show_error_page(request, "Diese Evaluation ist nicht mehr verfügbar.")

    if is_nwfg_evaluation:
        context["class_evaluation_id"] = evaluation_id
        context["subject_code"] = evaluation.nwfg_code[:3]
        context["nwfg_code"] = evaluation.nwfg_code

        # in the queryset, the Befragungsrunden are sorted in ascending order
        # based on the database models (meta settings).
        # the current Befragungsrunde round is therefore the last element in the queryset.
        evaluation_parts = NWFGEvaluationPart.objects.filter(nwfg_evaluation=evaluation)
        current_part = evaluation_parts.last()
        context.update({
            'befragungsrunde': current_part.befragungsrunde if current_part else None,
            'erhebungszeitpunkt': current_part.erhebungszeitpunkt if current_part else None,
            'first_part_started': bool(evaluation_parts),
        })

    if request.method == "GET":
        context["subject"] = evaluation.subject
        context["teacher_name"] = evaluation.teacher_name

        if not is_nwfg_evaluation:
            context["evaluation_end"] = evaluation.evaluation_end.strftime(
                '%d.%m.%Y - %H:%M')

        return render(request, 'evaluation_tool/pages/start-evaluation-page.html', context)

    if request.method == "POST":

        if not is_nwfg_evaluation:
            single_evaluation = SingleEvaluation.objects.create(class_evaluation=evaluation)
            create_items_for_new_single_evaluation(
                is_nwfg=False, single_evaluation=single_evaluation, class_evaluation=evaluation
            )
            return redirect(
                "evaluation-form-page",
                evaluation_id=evaluation_id,
                single_evaluation_id=single_evaluation.pk
            )
        else:
            if str(request.POST.get("action")) == "Evaluation starten":
                return redirect(evaluation_id + '/auth')
            else:
                return redirect(evaluation_id + '/new-auth')


def get_all_question_data() -> dict:
    """
    This function returns a dictionary that stores the corresponding information for each question code (key).
    The dictionary contains all the questions that exist.
    :return: dictionary
    """
    with open("static/data/question_pool.json") as file:
        question_pool = json.load(file)

    question_data = {}

    for dimension in question_pool.get("unspecific_dimensions", {}):
        question_data.update(question_pool["unspecific_dimensions"][dimension].get("pool", {}))

    specific_dimensions = question_pool.get("specific_dimension", {})
    for dimension in specific_dimensions:
        subjects = specific_dimensions.get(dimension, {}).get("subjects", {})
        for subject in subjects:
            question_data.update(subjects[subject].get("pool", {}))

    return question_data



def get_question_data(is_nwfg: bool = False, single_evaluation=None):
    """
    This method is used to determine all the information about the questions in order to be able to display them in the user interface.
    This includes the question codes in the order of the previously randomly mixed questions, as well as the question texts for the respective question code 
    and the total number of questions that have already been answered.

    :param is_nwfg: boolean (only questions for nwfg study!)
    :param single_evaluation: UUID for single evaluation
    :return: tuple(question_codes: list[str], question_data: dict, number_of_answered_questions: int)
    """

    if is_nwfg:
        items = NWFGItem.objects.filter(nwfg_single_evaluation=single_evaluation)
    else:
        items = Item.objects.filter(single_evaluation=single_evaluation)

    
    # The Question Codes are in the order in which the questions should be displayed
    # for a student based on the meta specifications.
    question_codes = [item.code for item in items]

    # Collect selected_likert_item in a single query
    likert_items = items.filter(selected_likert_item__isnull=False).values('code', 'selected_likert_item')

    # Collect selected_likert_item in a single query
    likert_items_dict = {item['code']: item['selected_likert_item'] for item in likert_items}

    # Collect all question data in a single query
    question_data = get_all_question_data()

    for code in question_codes:
        question_data[code]["selected_likert_item"] = likert_items_dict.get(code)

    # Count the amount of answered questions
    number_of_answered_questions = len(likert_items)

    return question_codes, question_data, number_of_answered_questions



def get_evaluation_form_page(request, evaluation_id, single_evaluation_id):
    """
    This method is used to display the single questions to a student. Five questions are always displayed.
    Once a student has answered these (Likert) questions, she/he can answer the next ones by clicking on "Next".
    Each time "Next" is clicked, the student's answers to the questions are persisted by a POST request.

    :param request: django specific
    :param evaluation_id: UUID
    :param single_evaluation_id: UUID
    :return: render object
    """
    context = {}

    evaluation = get_evaluation(evaluation_id)

    if evaluation is None:
        logger.warning(f"Ungültige Evaluations ID aufgerufen! {evaluation_id}")
        return show_error_page(request, "Diese Evaluation gibt es nicht.")

    is_nwfg = isinstance(evaluation, NWFGEvaluation)

    if is_nwfg:
        single_evaluation = NWFGSingleEvaluation.objects.get(
            nwfg_single_evaluation_id=single_evaluation_id)
    else:
        single_evaluation = SingleEvaluation.objects.get(
            single_evaluation_id=single_evaluation_id)

    context["subject_color"] = get_subject_color(evaluation.subject)

    evaluation_completed = evaluation.completed
    single_evaluation_completed = single_evaluation.completed

    if is_nwfg:
        evaluation_part_completed = single_evaluation.nwfg_evaluation_part.completed
    else:
        evaluation_end_reached = evaluation.evaluation_end < datetime.datetime.now()

    if evaluation_completed or (is_nwfg and evaluation_part_completed) or evaluation_end_reached or evaluation.deleted:
        logger.warning(f"Nicht mehr verfügbare Evaluation aufgerufen! {evaluation.pk}")
        return show_error_page(request, "Diese Evaluation ist nicht mehr verfügbar.")

    if single_evaluation_completed:
        return redirect(
            "evaluation-form-page-submit",
            evaluation_id=evaluation_id,
            single_evaluation_id=single_evaluation.pk
        )

    # get the question codes of the questions in the given evaluation
    # / the data for all questions / number of answered questions
    question_codes, question_data, number_of_answered_questions = get_question_data(
        is_nwfg=is_nwfg, single_evaluation=single_evaluation
    )

    # number of questions answered
    context["number_of_answered_questions"] = number_of_answered_questions

    # number of questions in total
    context["number_of_questions"] = len(question_codes)

    # maximum available page
    # participant always needs to answer the given five questions to see the next page
    context["maximum_page"] = int(context["number_of_answered_questions"] / 5) + 1

    if context["number_of_answered_questions"] == context["number_of_questions"]:
        context["maximum_page"] = int(context["number_of_answered_questions"] / 5) + \
                                  (1 if context["number_of_answered_questions"] % 5 != 0 else 0)

    # calculate the number of subpages that are needed
    context["number_of_sub_pages"] = int(context["number_of_questions"] / 5) + (context["number_of_questions"] % 5 > 0)
    context["number_of_sub_pages_iterator"] = range(1, context["number_of_sub_pages"] + 1)

    context["five_questions"] = {}
    context["current_site_index"] = context["maximum_page"]
    context["next_site_index"] = context["maximum_page"] + 1
    context["previous_site_index"] = context["maximum_page"] - 1

    if request.method == "GET":
        for question_code in question_codes[(context["current_site_index"] * 5) - 5: context["current_site_index"] * 5]:
            context["five_questions"][question_code] = question_data[question_code]

    if request.method == "POST":
        action = request.POST.get("action").split("_")

        if len(action) > 1:
            requested_page_index = int(action[1])

        action_name = action[0]

        form = ItemsForm(request.POST)

        if action_name == "next":
            # index of the page on which next is clicked
            page_index_post = requested_page_index - 1

            if form.is_valid() and ((context["number_of_answered_questions"] / 5) + 1 >= page_index_post):
                with transaction.atomic():
                    for i in range(5):
                        question_index = (page_index_post - 1) * 5 + i
                        question_code = question_codes[question_index]
                        selected_likert_item = int(form["q" + str(i + 1)].value())

                        filter_condition = Q(nwfg_single_evaluation=single_evaluation, code=question_code) if is_nwfg else Q(single_evaluation=single_evaluation, code=question_code)

                        if is_nwfg:
                            NWFGItem.objects.filter(filter_condition).update(selected_likert_item=selected_likert_item)
                        else:
                            Item.objects.filter(filter_condition).update(selected_likert_item=selected_likert_item)

                # update number of answered questions
                question_codes, question_data, number_of_answered_questions = get_question_data(
                    is_nwfg=is_nwfg, single_evaluation=single_evaluation)
                context["number_of_answered_questions"] = number_of_answered_questions

                # Wenn item submit ok / valide -> update der Navigation
                context["current_site_index"] = requested_page_index
                context["next_site_index"] = context["current_site_index"] + 1
                context["previous_site_index"] = context["current_site_index"] - 1

            for question_code in question_codes[
                                 (context["current_site_index"] * 5) - 5: context["current_site_index"] * 5]:
                context["five_questions"][question_code] = question_data[question_code]

        elif action_name == "back":
            # index der seite auf der next geklickt wird
            page_index_post = requested_page_index + 1

            # Wenn item submit ok / valide -> update der Navigation
            context["current_site_index"] = requested_page_index
            context["next_site_index"] = context["current_site_index"] + 1
            context["previous_site_index"] = context["current_site_index"] - 1
            for question_code in question_codes[
                                 (context["current_site_index"] * 5) - 5: context["current_site_index"] * 5]:
                context["five_questions"][question_code] = question_data[question_code]

        elif action_name == "send":
            # It is possible that there are less than five questions on the last page of the evaluation
            # since the number of questions in an evaluation does not necessarily have to be a multiple of 5.
            # Therefore, it must be checked differently whether all questions are valid.
            # However, there are a maximum of five questions on the last page.

            # first we need to check if the input is valid
            number_of_questions_last_page = (context["number_of_questions"] % 5) \
                if (context["number_of_questions"] % 5) != 0 else 5

            last_form_valid = True

            for i in range(1, number_of_questions_last_page + 1):

                if form["q" + str(i)].value() is None:
                    last_form_valid = False

                    # --> Warum hier ein try-block ?!
                    try:
                        if form["q" + str(i)].value() < 1 or form["q" + str(i)].value() > 5:
                            last_form_valid = False
                    except:
                        last_form_valid = False

            page_index_post = context["current_site_index"]

            if last_form_valid and ((context["number_of_answered_questions"] / 5) + 1 >= page_index_post):

                for i in range(number_of_questions_last_page):
                    question_index = (page_index_post - 1) * 5 + i
                    question_code = question_codes[question_index]
                    selected_likert_item = int(form["q" + str(i + 1)].value())
                    if is_nwfg:
                        item = NWFGItem.objects.get(
                            nwfg_single_evaluation=single_evaluation, code=question_code)
                        item.selected_likert_item = selected_likert_item
                        item.save()
                    else:
                        item = Item.objects.get(
                            single_evaluation=single_evaluation, code=question_code)
                        item.selected_likert_item = selected_likert_item
                        item.save()
                return redirect("evaluation-form-page-submit", evaluation_id=evaluation_id,
                                single_evaluation_id=single_evaluation.pk)

    context["number_of_questions_on_page"] = len(
        question_codes[
        (context["current_site_index"] * 5) - 5: context["current_site_index"] * 5
        ]
    )
    context["question_label_start_index"] = context["current_site_index"] * 5 - 5

    return render(request, 'evaluation_tool/pages/single-evaluation-page.html', context)


def get_evaluation_form_page_submit(request, evaluation_id, single_evaluation_id):
    """
    This method is used to display the page for submitting an evaluation.

    :param request: django specific
    :param evaluation_id: UUID
    :param single_evaluation_id: UUID
    :return: render object
    """
    context = {}

    evaluation = get_evaluation(evaluation_id)

    if evaluation is None:
        logger.warning(f"Ungültige Evaluations ID aufgerufen! {evaluation_id}")
        return show_error_page(request, "Diese Evaluation gibt es nicht.")

    is_nwfg = isinstance(evaluation, NWFGEvaluation)

    if is_nwfg:
        single_evaluation = NWFGSingleEvaluation.objects.get(
            nwfg_single_evaluation_id=single_evaluation_id)
    else:
        single_evaluation = SingleEvaluation.objects.get(
            single_evaluation_id=single_evaluation_id)

    context["subject_color"] = get_subject_color(evaluation.subject)

    evaluation_completed = evaluation.completed
    single_evaluation_completed = single_evaluation.completed

    if is_nwfg:
        evaluation_part_completed = single_evaluation.nwfg_evaluation_part.completed
    else:
        evaluation_end_reached = evaluation.evaluation_end < datetime.datetime.now()

    if evaluation_completed or (is_nwfg and evaluation_part_completed) or evaluation_end_reached or evaluation.deleted:
        logger.warning(f"Nicht mehr verfügbare Evaluation aufgerufen! {evaluation.pk}")
        return show_error_page(request, "Diese Evaluation ist nicht mehr verfügbar.")

    if is_nwfg:
        questions = NWFGItem.objects.filter(
            nwfg_single_evaluation=single_evaluation)
        answered_questions = NWFGItem.objects.filter(
            nwfg_single_evaluation=single_evaluation,
            selected_likert_item__isnull=False
        )
    else:
        questions = Item.objects.filter(single_evaluation=single_evaluation)
        answered_questions = Item.objects.filter(
            single_evaluation=single_evaluation,
            selected_likert_item__isnull=False
        )

    context["single_evaluation_completed"] = single_evaluation_completed

    if len(questions) > len(answered_questions):
        logger.warning(
            f"Nicht alle Fragen beantwortet für Id Class: {evaluation_id} und Single Id: {single_evaluation_id}")
        return show_error_page(request, "Diese Evaluation nicht beendet werden. Bitte beantworte alle Fragen.")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "confirm" and len(questions) == len(answered_questions):
            single_evaluation.completed = True
            single_evaluation.save()
            return redirect(
                "evaluation-form-page-submit",
                evaluation_id=evaluation_id,
                single_evaluation_id=single_evaluation.pk
            )
        if action == "back":
            return redirect(
                "evaluation-form-page",
                evaluation_id=evaluation_id,
                single_evaluation_id=single_evaluation.pk
            )

    context["is_nwfg_evaluation"] = is_nwfg
    context["single_evaluation_id"] = single_evaluation_id
    context["class_evaluation_id"] = evaluation_id

    return render(request, 'evaluation_tool/pages/submit-evaluation-page.html', context)

def get_status_page(request, evaluation_id, status_code):
    """
    This method is used to display the status page. This method handles inputs such as stopping an evaluation or starting the next Befragungsrunde.

    :param request: django specific
    :param evaluation_id: UUID
    :param status_code: ??
    :return: render status page (only non-nwfg), redirects on changes, HttpResponse on error
    """
    # Items heraussuchen, Items sortieren, Seite festlegen (default = 1), Fragen für bestimmte Seite geben
    context = {}

    # Die Evaluation Page ist nicht verfügbar, wenn:
    # ClassEvaluation completed oder vorbei / SingleEvaluation completed
    # NWFGEvaluation completed / NWFGEvaluationPart der Single Evaluation completed / SingleEvaluation completed
    try:
        class_evaluation = ClassEvaluation.objects.get(
            class_evaluation_id=evaluation_id
        )
        context["subject_color"] = get_subject_color(class_evaluation.subject)
        context["evaluation_completed"] = class_evaluation.completed
        context["evaluation_end_reached"] = class_evaluation.evaluation_end < datetime.datetime.now()

        # display evaluation start / end
        context["evaluation_start"] = class_evaluation.evaluation_start.strftime('%d.%m.%Y - %H:%M')

        if class_evaluation.evaluation_stopped_timestamp is None:
            context["evaluation_end"] = class_evaluation.evaluation_end.strftime('%d.%m.%Y - %H:%M')
        else:
            context["evaluation_end"] = class_evaluation.evaluation_stopped_timestamp.strftime('%d.%m.%Y - %H:%M')

        is_nwfg = False

        if class_evaluation.deleted:
            logger.warning(f"Nicht mehr verfügbare Evaluation aufgerufen! {class_evaluation.pk}")
            return show_error_page(request, "Diese Evaluation ist nicht mehr verfügbar.")

        if str(class_evaluation.status_url_token) != status_code:
            logger.warning(f"Ungültiger Statuscode wurde übermittelt: {status_code}")
            return show_error_page(request, "Dieser Status-Code kann keiner Evaluation zugeordnet werden.")

    except ObjectDoesNotExist:
        try:
            class_evaluation = NWFGEvaluation.objects.get(
                nwfg_evaluation_id=evaluation_id)
            context["subject_color"] = get_subject_color(
                class_evaluation.subject)
            evaluation_completed = class_evaluation.completed  # --> meintest du: context["evaluation_completed"] ?
            context["evaluation_completed"] = evaluation_completed

            is_nwfg = True

            if str(class_evaluation.status_url_token) != status_code:
                logger.warning(f"Ungültiger Statuscode wurde übermittelt: {status_code}")
                return show_error_page(request, "Dieser Status-Code kann keiner Evaluation zugeordnet werden.")

        except ObjectDoesNotExist:
            logger.warning(f"Ungültige Evaluations ID aufgerufen! {evaluation_id}")
            return show_error_page(request, "Diese Evaluation gibt es nicht.")

    context["subject"] = class_evaluation.subject
    context["evaluation_id"] = class_evaluation.pk
    context["evaluation_id_str"] = str(class_evaluation.pk)  # for csv and pdf download
    context["completed"] = class_evaluation.completed
    context["is_nwfg"] = is_nwfg
    context["status_code"] = status_code  # for csv and pdf download

    if is_nwfg:
        evaluation_parts = NWFGEvaluationPart.objects.filter(
            nwfg_evaluation=class_evaluation
        )

        # If the NWFG evaluation has been created but no survey round has been started yet, a template appears on the status page, 
        # which allows the teacher to start the first Befragungsrunde as well as to see how many students have created a sample.
        if len(evaluation_parts) == 0:
            n_used_acronyms = len(NWFGEvaluationAcronym.objects.filter(nwfg_evaluation=evaluation_id))
            context["n_used_acronyms"] = n_used_acronyms

            if request.method == "POST":
                action = request.POST.get("action")
                if action == "start_first_evaluation":
                    # create new Befragungsrunde (=nwfg_evaluation_part)
                    next_nwfg_evaluation_part = NWFGEvaluationPart.objects.create(
                        erhebungszeitpunkt=1,
                        befragungsrunde=1,
                        nwfg_evaluation=class_evaluation
                    )

                    # send_mail_new_nwfg_evaluation_round(
                    #     class_evaluation=class_evaluation.pk,
                    #     nwfg_evaluation_part=next_nwfg_evaluation_part,
                    #     status_code=class_evaluation.status_url_token,
                    #     subject=class_evaluation.subject,
                    #     to_email_address=class_evaluation.email,
                    # )

                    # Since such changes change pretty much everything, a redirect is used here.
                    logger.info(f"Nächste Runde der NWFG Evaluation {evaluation_id} gestartet.")
                    return redirect(
                        "status-page",
                        evaluation_id=evaluation_id,
                        status_code=status_code
                    )

            return render(request, 'evaluation_tool/pages/status-page-new-nwfg-evaluation.html', context)

        context["current_erhebungszeitpunkt"] = evaluation_parts.reverse()[0].erhebungszeitpunkt
        context["current_befragungsrunde"] = evaluation_parts.reverse()[0].befragungsrunde
        context["current_part_status"] = "completed"

        context["is_last_evaluation"] = True if (
                context["current_erhebungszeitpunkt"] == 3 and context["current_befragungsrunde"] == 2
        ) else False

        if not (context["is_last_evaluation"]):
            context["next_erhebungszeitpunkt"] = context["current_erhebungszeitpunkt"] if (
                    context["current_befragungsrunde"] < 2
            ) else context["current_erhebungszeitpunkt"] + 1

            context["next_befragungsrunde"] = context["current_befragungsrunde"] + 1 if (
                    context["current_befragungsrunde"] < 2
            ) else 1

        context["share_url"] = os.getenv("WEBSITE_URL") + "evaluation/" + \
                               str(class_evaluation.pk) + "/share"

        # create data for the evaluation parts
        context["evaluation_data"] = {}

        for i in range(6):

            context["evaluation_data"][i] = {}

            try:
                if evaluation_parts[i].completed is True:
                    context["evaluation_data"][i]["status"] = "completed"

                else:
                    context["evaluation_data"][i]["status"] = "started"
                    context["current_part_status"] = "started"

                # Store Erhebungszeitpunkt / Befragungsrunde
                context["evaluation_data"][i]["erhebungszeitpunkt"] = evaluation_parts[i].erhebungszeitpunkt
                context["evaluation_data"][i]["befragungsrunde"] = evaluation_parts[i].befragungsrunde

                # Store Participant Statistic
                context["evaluation_data"][i]["evaluations_started"] = 0
                context["evaluation_data"][i]["evaluations_completed"] = 0

                participants_in_evaluation_part = NWFGSingleEvaluation.objects.filter(
                    nwfg_evaluation_part=evaluation_parts[i]
                )
                for participant in participants_in_evaluation_part:
                    if participant.completed:
                        context["evaluation_data"][i]["evaluations_completed"] += 1
                        context["evaluation_data"][i]["evaluations_started"] += 1
                    else:
                        context["evaluation_data"][i]["evaluations_started"] += 1

            except:  # -->Error type? ObjectDoesntExist ?
                context["evaluation_data"][i]["status"] = "not_started"

        context["evaluation_data"]["evaluations_started"] = 0
        # get data for stats
        d = DataAnalyzer(evaluation_id, True)
        stats_data = d.get_stats_per_dim()
        context["evaluation_stats_data"] = stats_data
        context["evaluation_stats_data_json"] = json.dumps(stats_data)
        context["num_responses_included"] = context["evaluation_data"][
                                                "evaluations_started"] - d.get_excluded_participants()
        logger.info(f"Statusseite für NWFG Evaluation {evaluation_id} aufgerufen.")

        if request.method == "POST":
            action = request.POST.get("action")
            current_part = evaluation_parts.reverse()[0]

            if action == "stop" and context["current_part_status"] == "started":

                # The current Befragungsrunde is marked as completed, and it is saved when it was completed (timestamp)
                current_part.completed = True
                current_part.evaluation_stopped_timestamp = datetime.datetime.now()
                current_part.save()

                # If the second Befragungsrunde of a Erhebungszeitpunkt gets stopped, a mail should also be sent.
                if current_part.befragungsrunde == 2 and current_part.erhebungszeitpunkt == 3:
                    send_mail_finished_nwfg_evaluation(class_evaluation=class_evaluation.pk, to_email_address=class_evaluation.email, status_code=class_evaluation.status_url_token)

                # if the current Befragunsrunde is the last of the nine
                if context["is_last_evaluation"]:
                    class_evaluation.completed = True
                    class_evaluation.save()

                # Since such changes change pretty much everything, a redirect is used here to reload the page.
                logger.info(f"NWFG Evaluation {evaluation_id} gestoppt!")
                return redirect(
                    "status-page",
                    evaluation_id=evaluation_id,
                    status_code=status_code
                )

            else:
                # page is loaded normally + error text displayed when entering this else block.
                # this error could occur but only if the user changes the code in the frontend.
                # The frontend is built so that such errors are prevented.
                # but the system must be robust enough to withstand such manipulations <-- sehr gut! :-)
                context["error_action"] = "Es ist ein ungewöhnlicher Fehler aufgetreten."
                logger.error(f"Ungewöhnlicher Fehler nach Stoppen der NWFG Evaluation {evaluation_id}")

            if action == "next_evaluation" and not (context["is_last_evaluation"]):

                if not current_part.completed:
                    # If the next Befragungsrunde gets started,
                    # the one that has been active until now is marked as completed.
                    current_part.completed = True
                    current_part.evaluation_stopped_timestamp = datetime.datetime.now()
                    current_part.save()

                    #if current_part.befragungsrunde == 2:
                        #send_mail_finished_nwfg_evaluation(class_evaluation=class_evaluation.pk, to_email_address=class_evaluation.email, status_code=class_evaluation.status_url_token)

                # create new Befragungsrunde (=nwfg_evaluation_part)
                next_nwfg_evaluation_part = NWFGEvaluationPart.objects.create(
                    erhebungszeitpunkt=context["next_erhebungszeitpunkt"],
                    befragungsrunde=context["next_befragungsrunde"],
                    nwfg_evaluation=class_evaluation
                )

                # send_mail_new_nwfg_evaluation_round(
                #     class_evaluation=class_evaluation.pk,
                #     nwfg_evaluation_part=next_nwfg_evaluation_part,
                #     status_code=class_evaluation.status_url_token,
                #     subject=class_evaluation.subject,
                #     to_email_address=class_evaluation.email,
                # )

                # Since such changes change pretty much everything, a redirect is used here.
                logger.info(f"Nächste Runde der NWFG Evaluation {evaluation_id} gestartet.")
                return redirect(
                    "status-page",
                    evaluation_id=evaluation_id,
                    status_code=status_code
                )

    # if not a nwfg evaluation
    else:

        seconds_left = class_evaluation.evaluation_end - datetime.datetime.now()
        seconds_left = seconds_left.total_seconds()

        if seconds_left <= 0:
            context["time_over"] = True

        else:
            context["time_over"] = False

        context["seconds_left"] = seconds_left

        # create data for the evaluation
        context["evaluation_data"] = {}

        # Store Participant Statistic
        context["evaluation_data"]["evaluations_started"] = 0
        context["evaluation_data"]["evaluations_completed"] = 0

        # Store status url
        context["share_url"] = os.getenv("WEBSITE_URL") + "evaluation/" + \
                               str(class_evaluation.pk) + "/share"

        participants_in_evaluation = SingleEvaluation.objects.filter(
            class_evaluation=class_evaluation
        )

        for participant in participants_in_evaluation:

            if participant.completed:
                context["evaluation_data"]["evaluations_completed"] += 1
                context["evaluation_data"]["evaluations_started"] += 1

            else:
                context["evaluation_data"]["evaluations_started"] += 1

        # get data for stats
        d = DataAnalyzer(str(class_evaluation.pk), is_nwfg)
        stats_data = d.get_stats_per_dim()
        context["evaluation_stats_data"] = stats_data
        context["evaluation_stats_data_json"] = json.dumps(stats_data)
        context["num_responses_included"] = context["evaluation_data"][
                                                "evaluations_started"] - d.get_excluded_participants()
        logger.info(f"Statusseite für ClassEvaluation {evaluation_id} aufgerufen.")

        if request.method == "POST":

            action = request.POST.get("action")

            if action == "stop" and not class_evaluation.completed:

                class_evaluation.completed = True

                # Es wird bewusst im if-Statement geprüft, ob die Umfrage schon vorbei ist,
                # da auch die Zeit gespeichert werden muss
                class_evaluation.evaluation_stopped_timestamp = datetime.datetime.now()
                class_evaluation.save()

                send_mail_finished_class_evaluation(class_evaluation=class_evaluation.pk,
                                                    status_code=class_evaluation.status_url_token,
                                                    to_email_address=class_evaluation.email)

                # Since such changes change pretty much everything, a redirect is used here.
                logger.info(f"ClassEvaluation {evaluation_id} gestoppt!")
                return redirect(
                    "status-page",
                    evaluation_id=evaluation_id,
                    status_code=status_code
                )
            else:
                # page is loaded normally + error text displayed when entering this else block.
                # this error could occur but only if the user changes the code in the frontend.
                # The frontend is built so that such errors are prevented.
                # but the system must be robust enough to withstand such manipulations
                context["error_action"] = "Es ist ein ungewöhnlicher Fehler aufgetreten."
                logger.error(f"Ungewöhnlicher Fehler nach Stoppen der ClassEvaluation {evaluation_id}")

            if action == "delete_evaluation":
                email = class_evaluation.email
                logger.info(f"ClassEvaluation mit ID {evaluation_id} und E-Mail {email} gelöscht!")
                class_evaluation.deleted = True
                class_evaluation.email = ""
                class_evaluation.teacher_name = ""
                class_evaluation.save()

                # Since such changes change pretty much everything, a redirect is used here.
                return redirect(
                    "status-page",
                    evaluation_id=evaluation_id,
                    status_code=status_code
                )

    return render(request, 'evaluation_tool/pages/status-page.html', context)


def download_csv(request, evaluation_id, status_code):
    try:
        evaluation_object = ClassEvaluation.objects.get(
            class_evaluation_id=evaluation_id
        )
        is_nwfg = False
    except ObjectDoesNotExist:
        try:
            evaluation_object = NWFGEvaluation.objects.get(
                nwfg_evaluation_id=evaluation_id
            )
            is_nwfg = True
        except ObjectDoesNotExist:
            return show_error_page(request, "Diese Evaluation gibt es nicht.")

    if str(evaluation_object.status_url_token) != status_code:
        return show_error_page(request, "Diese Status-Seite existiert nicht.")

    evaluation_id_for_data = evaluation_object.pk

    ex = ExcelExporter(subject=evaluation_object.subject, class_id=evaluation_id_for_data)

    data = ex.get_full_data()
    buffer = io.BytesIO()
    output = create_excel_export(buffer, data)

    now = datetime.datetime.now()

    filename=f"Amadeus_Evaluationsbericht_{evaluation_object.subject}_{now.year}-{now.month}-{now.day}.xlsx"

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def get_evaluation_pdf(request, evaluation_id, status_code):
    t1 = time.time()
    try:
        evaluation_object = ClassEvaluation.objects.get(
            class_evaluation_id=evaluation_id
        )
        is_nwfg = False
    except ObjectDoesNotExist:
        try:
            evaluation_object = NWFGEvaluation.objects.get(
                nwfg_evaluation_id=evaluation_id
            )
            is_nwfg = True
        except ObjectDoesNotExist:
            return show_error_page(request, "Diese Evaluation gibt es nicht.")

    if str(evaluation_object.status_url_token) != status_code:
        return show_error_page(request, "Diese Status-Seite existiert nicht.")

    evaluation_id_for_data = evaluation_object.pk

    d = DataAnalyzer(evaluation_id_for_data, is_nwfg)
    data_dict = d.get_stats_per_dim()
    excluded = d.get_excluded_participants()
    print(f"Exluded: {excluded}")
    participated = len(SingleEvaluation.objects.filter(class_evaluation_id=evaluation_id_for_data))
    print(f"Participants: {participated}")
    num_included_responses = participated - excluded

    def replace_spaces_with_underscore(subject: str) -> str:
        parts = subject.split(" ")
        return "_".join(parts)

    # create pdf
    buffer = io.BytesIO()

    pdf = PdfWriter(
        buffer=buffer, data_dict=data_dict,
        subject=evaluation_object.subject,
        count=num_included_responses
    )

    output = pdf.get_eval_pdf()
    now = datetime.datetime.now()
    subject_name = replace_spaces_with_underscore(d.subject)
    t2 = time.time()
    duration = t2 - t1
    logger.info(f"PDF von Evaluation {evaluation_id_for_data} heruntergeladen. Dauer: {duration}.")
    return FileResponse(
        output, as_attachment=True,
        filename=f"Amadeus_Evaluationsbericht_{subject_name}_{now.year}-{now.month}-{now.day}.pdf"
    )

@staff_member_required
def staff_downloads(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = DownloadForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            print(form.cleaned_data)
            subject = form.cleaned_data['subject']
            answered = form.cleaned_data['min_answered']
            # redirect to a new URL:
            buffer = io.BytesIO()
            output = full_data_export(subject, answered, buffer)

            now = datetime.datetime.now()

            filename = f"Amadeus_Full-Export_{subject.capitalize()}_{now.year}-{now.month}-{now.day}.xlsx"

            response = HttpResponse(output,
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={filename}'
            return response

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DownloadForm()

    return render(request, "evaluation_tool/pages/download.html", {"form": form})
