import json
import numpy as np
import pandas as pd
from typing import Tuple
from evaluation_tool.models import ClassEvaluation, SingleEvaluation, Item
from evaluation_tool.scripts.data_analysis import count_answered_items
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from dotenv import load_dotenv
import os

env = load_dotenv('../../.env')


def create_item_list(fulltext=False, selected_subject=None):
    items = []

    with open(f"{os.getenv('STATIC_FOLDER')}/data/question_pool.json", "r", encoding="utf-8") as file:
        question_pool_dict = json.loads(file.read())

        for dim in question_pool_dict["unspecific_dimensions"]:
            for key in question_pool_dict["unspecific_dimensions"][dim]["pool"].keys():
                if not question_pool_dict["unspecific_dimensions"][dim]["pool"][key]["nwfg_study_exclusive"]:
                    if fulltext:
                        items.append({
                            "key": key,
                            "text": question_pool_dict["unspecific_dimensions"][dim]["pool"][key]["question_text"],
                            "dim": question_pool_dict["unspecific_dimensions"][dim]["dimension_name"],
                        })
                    else:
                        items.append(key)

        for dim in question_pool_dict["specific_dimension"]:
            # if there's no subject given like when you want to get data from all subjects
            if not selected_subject:
                for subject in question_pool_dict["specific_dimension"][dim]["subjects"]:
                    for key in question_pool_dict["specific_dimension"][dim]["subjects"][subject]["pool"].keys():
                        if not question_pool_dict["specific_dimension"][dim]["subjects"][subject]["pool"][key]["nwfg_study_exclusive"]:
                            if fulltext:
                                items.append({
                                    "key": key,
                                    "text": question_pool_dict["specific_dimension"][dim]["subjects"][subject]["pool"][key]["question_text"],
                                    "dim": f"Fachspezifik: {subject}",
                                })
                            else:
                                items.append(key)
            # skip selecting subject specific dimensions when it's a general evaluation
            elif selected_subject == "Allgemeine Lehrevaluation":
                pass
            else:
                for key in question_pool_dict["specific_dimension"][dim]["subjects"][selected_subject]["pool"].keys():
                    if not question_pool_dict["specific_dimension"][dim]["subjects"][selected_subject]["pool"][key]["nwfg_study_exclusive"]:
                        if fulltext:
                            items.append({
                                "key": key,
                                "text": question_pool_dict["specific_dimension"][dim]["subjects"][selected_subject]["pool"][key]["question_text"],
                                "dim": question_pool_dict["specific_dimension"][dim]["dimension_name"]
                            })
                        else:
                            items.append(key)

    return items


def get_started_and_completed(class_evaluation_id) -> Tuple[int, int]:

    started = len(SingleEvaluation.objects.filter(class_evaluation_id=class_evaluation_id))
    completed = len(SingleEvaluation.objects.filter(class_evaluation_id=class_evaluation_id).filter(completed=True))

    return started, completed


def save_full_data_as_csv(data, path):

    df = pd.DataFrame(data)

    df.to_csv(path, index=False, header=False, encoding="utf-8", na_rep="na")


class DataExporter:

    def __init__(self):

        COLS = [
            "single_eval_id",
            "class_eval_id",
            "subject",
            "creation_timestamp",
            "email",
            "started_by",
            "completed_by",
            "included_responses"
        ]

        self.ITEMS = create_item_list()

        self.columns = COLS + self.ITEMS

        self.STARTED_THRESHOLD = 5
        self.COMPLETED_THRESHOLD = 3
        self.PERCENT_THRESHOLD = 0.25

    def create_observation(self, eval_obj: ClassEvaluation,
                           single_obj: SingleEvaluation,
                           started, completed,
                           item_queryset):

        observation = [
            single_obj.pk,
            eval_obj.pk,
            eval_obj.subject,
            str(eval_obj.creation_timestamp),
            eval_obj.email,
            started,
            completed,
            count_answered_items(item_queryset),
        ]

        for item in self.ITEMS:
            try:
                it = item_queryset.get(code=item)

                if it.selected_likert_item:
                    observation.append(it.selected_likert_item)
                else:
                    observation.append(np.nan)

            except ObjectDoesNotExist:
                observation.append(np.nan)

        return observation

    def get_full_data(self):

        observations = [self.columns]

        evaluations = ClassEvaluation.objects.all()

        for evaluation in evaluations:

            started, completed = get_started_and_completed(evaluation.pk)

            if started >= self.STARTED_THRESHOLD and completed >= self.COMPLETED_THRESHOLD:

                for single_evaluation in SingleEvaluation.objects.filter(class_evaluation_id=evaluation.pk):

                    items = Item.objects.filter(single_evaluation_id=single_evaluation.pk)

                    if count_answered_items(items) / len(items) >= self.PERCENT_THRESHOLD:

                        observations.append(
                            self.create_observation(
                                evaluation, single_evaluation,
                                started, completed, items
                            )
                        )
        return observations


class ExcelExporter(DataExporter):

    def __init__(self, subject, class_id):
        super().__init__()

        self.subject = subject
        self.class_id = class_id

        self.ITEMS = create_item_list(fulltext=True, selected_subject=self.subject)

        self.columns = [item["text"] for item in self.ITEMS]

    def create_observation(self, eval_obj: ClassEvaluation,
                           single_obj: SingleEvaluation,
                           started, completed,
                           item_queryset):

        observation = []

        for item in self.ITEMS:
            try:
                it = item_queryset.get(code=item["key"])

                if it.selected_likert_item:
                    observation.append(it.selected_likert_item)
                else:
                    observation.append(np.nan)

            except ObjectDoesNotExist:
                observation.append(np.nan)

        return observation

    def get_full_data(self):

        observations = [self.columns, [item["dim"] for item in self.ITEMS]]

        single_evaluations = SingleEvaluation.objects.filter(class_evaluation_id=self.class_id)

        for single_evaluation in single_evaluations:

            items = Item.objects.filter(single_evaluation_id=single_evaluation.pk)

            if count_answered_items(items) / len(items) >= self.PERCENT_THRESHOLD:
                observations.append(
                    self.create_observation(
                        self.class_id, single_evaluation,
                        None, None, items))

        return observations


def create_excel_export(buffer, data):

    df = pd.DataFrame(data)

    trans = df.T
    new_cols = ["Text", "Dimension"] + [f"id_{i}" for i in range(1, trans.shape[1] - 1)]
    trans.columns = new_cols
    trans.index = range(1, len(trans.index) + 1)

    vals = trans.filter(like="id_").astype("float")

    mean = vals.mean(axis=1).round(2)
    mean.index = trans.index
    mean.name = "Mittelwert"

    sdt = vals.std(axis=1).round(2)
    sdt.index = trans.index
    sdt.name = "Standardabweichung"

    dims = trans.iloc[:, :2]

    new_df = dims.join(mean.to_frame().join(sdt.to_frame().join(vals)))
    new_df.index.name = "Item Nr."

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        new_df.to_excel(writer, sheet_name="Sheet1")

    buffer.seek(0)
    return buffer

    # new_df.to_excel(buffer)


def full_data_export(subject: str, answered: int, buffer):
    if subject == 'all':
        view = 'full_view'
    else:
        view = 'full_view' + subject

    with connection.cursor() as cursor:
        cursor.execute(f'''
        SELECT * FROM {view}
        JOIN (SELECT evaluation, count("Teilnehmer:in") AS answered FROM {view} GROUP BY evaluation) AS counting
            ON {view}.evaluation = counting.evaluation
        WHERE answered >= {answered}
        ORDER BY {view}.evaluation;
        ''')
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        df.columns = columns

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name=f"export_{subject}")

        buffer.seek(0)
        return buffer


