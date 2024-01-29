from evaluation_tool.models import Item, NWFGItem
import random
import json


def shuffle_questions_for_student(questions_for_student):
    l = list(questions_for_student.items())
    random.shuffle(l)
    questions_for_student = dict(l)
    return questions_for_student


def create_items_for_new_single_evaluation(is_nwfg=False, single_evaluation=None, evaluation_part=None,
                                           class_evaluation=None, nwfg_evaluation_acronym=None):
    with open("static/data/question_pool.json") as file:
        question_pool = json.loads(file.read())

    subject = class_evaluation.subject

    questions_for_student = dict()

    if is_nwfg:
        befragungsrunde = int(evaluation_part.befragungsrunde)
        erhebungszeitpunkt = int(evaluation_part.erhebungszeitpunkt)
        pool = int(nwfg_evaluation_acronym.pool)

        pool_mapping = {"A": [1, 3, 7], "B": [2, 4, 8], "C": [5, 6, 9]}

        if (pool, befragungsrunde, erhebungszeitpunkt) in [(1, 1, 1), (3, 2, 1), (2, 1, 2), (1, 2, 2), (3, 1, 3), (2, 2, 3)]:
            dimensions_for_student = pool_mapping["A"]
        elif (pool, befragungsrunde, erhebungszeitpunkt) in [(2, 1, 1), (1, 2, 1), (3, 1, 2), (2, 2, 2), (1, 1, 3), (3, 2, 3)]:
            dimensions_for_student = pool_mapping["B"]
        elif (pool, befragungsrunde, erhebungszeitpunkt) in [(3, 1, 1), (2, 2, 1), (1, 1, 2), (3, 2, 2), (2, 1, 3), (1, 2, 3)]:
            dimensions_for_student = pool_mapping["C"]

        for dimension in dimensions_for_student:
            if dimension <= 7:
                questions_for_dimension = question_pool["unspecific_dimensions"][str(dimension)]["pool"]
                questions_for_student.update(questions_for_dimension)
            if dimension >= 8:
                questions_for_subject = question_pool["specific_dimension"][str(dimension)]["subjects"][subject]["pool"]
                questions_for_student.update(questions_for_subject)
    else:
        for dimension in range(1, 10):
            if dimension <= 7:
                questions_for_dimension = question_pool["unspecific_dimensions"][str(dimension)]["pool"]
                questions_for_dimension = {k: v for k, v in questions_for_dimension.items() if v["nwfg_study_exclusive"] is False}
                questions_for_student.update(questions_for_dimension)
            if dimension >= 8 and subject != "Allgemeine Lehrevaluation":
                questions_for_subject = question_pool["specific_dimension"][str(dimension)]["subjects"][subject]["pool"]
                questions_for_subject = {k: v for k, v in questions_for_subject.items() if v["nwfg_study_exclusive"] is False}
                questions_for_student.update(questions_for_subject)

    # individual shuffle for a student
    questions_for_student = shuffle_questions_for_student(questions_for_student)

    if is_nwfg:
        idx = 0
        for key in questions_for_student.keys():
            NWFGItem.objects.create(code=key, recoded=questions_for_student[key]['recode'], nwfg_single_evaluation=single_evaluation, question_index_for_student=idx)
            idx += 1
    else:
        idx = 0
        for key in questions_for_student.keys():
            recode = questions_for_student[key]['recode']
            Item.objects.create(code=key, recoded=questions_for_student[key]['recode'], single_evaluation=single_evaluation, question_index_for_student=idx)
            idx += 1
