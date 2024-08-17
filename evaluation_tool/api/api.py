from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from evaluation_tool.models import NWFGEvaluation
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from evaluation_tool.subjects import subject_mapping
import json
import re

@csrf_exempt
def create_evaluation_api(request, nwfg_code):
    """
    This method processes POST requests to create a new evaluation using the provided NWFG code.
    The NWFG code is validated against a specific pattern, and the request body is expected to contain
    the required fields 'email' and 'teacher_name'. If the request is valid, a new evaluation is created
    and a JSON response is returned with the evaluation details. If the request method is not POST,
    an HttpResponseNotAllowed is returned.
    :param request: Django request object
    :param nwfg_code: NWFG code for the evaluation
    :return: JsonResponse with evaluation details, HttpResponseBadRequest or HttpResponseNotAllowed
    """

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "POST is the only available HTTP method.")

    nwfg_pattern = r"^(ENG|GER|LAT|MAT|MUS|REL)\d{12}$"

    if not re.match(nwfg_pattern, nwfg_code):
        return HttpResponseBadRequest("nwfg_code is not in the correct format.")

    # check if nwfg code already exists
    existing_evaluation = NWFGEvaluation.objects.get(nwfg_code=nwfg_code)
    if existing_evaluation:
        return HttpResponseBadRequest("Evaluation with given NWFG-Code is already in use.")

    request_body = json.loads(request.body.decode("utf-8"))

    if "email" not in request_body:
        return HttpResponseBadRequest("Email is missing in the request body.")

    if "teacher_name" not in request_body:
        return HttpResponseBadRequest("Teacher name is missing in the request body.")

    if "school_type" not in request_body:
        return HttpResponseBadRequest("School type is missing in the request body.")

    # validate email
    email = request_body["email"]

    # validate teacher name
    teacher_name = request_body["teacher_name"]
    teacher_name_is_valid = len(teacher_name) <= 200

    school_type = request_body["school_type"]

    if not teacher_name_is_valid:
        return HttpResponseBadRequest("Teacher is not provided.")

    subject = subject_mapping[nwfg_code[:3]]

    nwfg_evaluation = NWFGEvaluation.objects.create(
        nwfg_code=nwfg_code,
        teacher_name=teacher_name,
        email=email,
        subject=subject,
        school_type=school_type
    )

    response_data = {
        "evaluation_id": nwfg_evaluation.nwfg_evaluation_id,
        "status_code": nwfg_evaluation.status_url_token
    }

    return JsonResponse(response_data)
