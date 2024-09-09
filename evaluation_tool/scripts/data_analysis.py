from evaluation_tool.models import NWFGItem, Item, NWFGEvaluation, ClassEvaluation
from django.core.exceptions import ObjectDoesNotExist
from io import BytesIO

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def recode(n: int, has_to_be_recoded: bool) -> any:
    if n is None:
        return n
    assert isinstance(n, int) and 1 <= n <= 5, "argument must be an integer between 1 and 5"
    return n - ((n - 3) * 2) if has_to_be_recoded else n


def sort_by_index_and_extract_counts(pandas_series):
    pandas_series.sort_index(inplace=True)
    index_list = [int(i) for i in pandas_series.index]
    count_list = pandas_series.to_list()
    return index_list, count_list


def fill_up_5_item_likert_scale(tuple_of_int_lists):
    """
    Not all dimensions get all likert items from participants. So there are count tuples in function "build_dims" which
    could look like this ([2,3,5],[12,18,9]). But we want to show all likert items and the ones not given to be 0!
    So the end-tuple should look like this: ([1,2,3,4,5],[0,12,18,0,9]).
    :param: tuple_of_int_lists: the tuple for the likert items and corresponding counts:
    ([likert_numbers],[likert_counts])
    :return: filled up tuple of int lists (see description)
    """
    assert len(tuple_of_int_lists) == 2, "tuple length not right"

    for i in range(5):
        if i + 1 not in tuple_of_int_lists[0]:
            tuple_of_int_lists[0].insert(i, i + 1)
            tuple_of_int_lists[1].insert(i, 0)

    return tuple_of_int_lists


class DataAnalyzer:
    def __init__(self, evaluation_id: str, is_nwfg: bool = False):

        self.data = None

        self.dimensions = {
            "1": "Auswahl von Inhalten und Methoden",
            "2": "Kognitive Aktivierung",
            "3": "Unterstützung des Übens",
            "4": "Formatives Assessment",
            "5": "Unterstützung des Lernens",
            # "6": "Sozio-emotionale Unterstützung",
            "6_1": "Verhältnis zw. Lehrkraft u. Schüler:innen",
            "6_2": "Verhältnis zw. Schüler:innen",
            # "7": "Klassenführung",
            "7_1": "Verhaltensmanagement",
            "7_2": "Zeitmanagement",
            "8": "Ästhetisch-emotionales Lernen",
            "9": "Fachspezifische Qualitätsmerkmale"
        }

        self.excluded_participants = 0

        if is_nwfg:
            self.columns = [
                "code", "t", "user", "completed", "item", "likert", "recoded"
            ]
            self.sort_df_by = ["code", "t", "user"]
            try:
                self.subject = NWFGEvaluation.objects.get(nwfg_evaluation_id=evaluation_id).subject
                all_items = NWFGItem.objects.filter(
                    nwfg_single_evaluation__nwfg_evaluation_part__nwfg_evaluation=evaluation_id
                ).values(
                    'nwfg_single_evaluation__nwfg_evaluation_part__nwfg_evaluation__nwfg_code',
                    'nwfg_single_evaluation__acronym__acronym',
                    'nwfg_single_evaluation__nwfg_evaluation_part__erhebungszeitpunkt',
                    'nwfg_single_evaluation__completed',
                    'code',
                    'selected_likert_item',
                    'recoded',
                )
                self.data = [
                    [
                        str(i['nwfg_single_evaluation__nwfg_evaluation_part__nwfg_evaluation__nwfg_code']), # evaluation code
                        str(i['nwfg_single_evaluation__acronym__acronym']),                                 # user acronym
                        str(i['nwfg_single_evaluation__nwfg_evaluation_part__erhebungszeitpunkt']),         # Messzeitpunkt
                        str(i['nwfg_single_evaluation__completed']),                                        # has single evaluation been completed?
                        str(i['code']),                                                                     # code for item
                        recode(i['selected_likert_item'], i['recoded']),                                    # the likert item with right value
                        str(i['recoded']),                                                                  # is item recoded?
                    ]
                    for i in all_items
                ]
            except ObjectDoesNotExist:
                print('Object does not exist!')

        else:
            self.columns = [
                "code", "user", "completed", "item", "likert", "recoded"
            ]
            self.sort_df_by = ["code", "user"]
            try:
                self.subject = ClassEvaluation.objects.get(class_evaluation_id=evaluation_id).subject
                all_items = Item.objects.filter(
                    single_evaluation__class_evaluation_id=evaluation_id
                ).values(
                    'single_evaluation_id',
                    'single_evaluation__completed',
                    'code',
                    'selected_likert_item',
                    'recoded',
                )
                self.data = [
                    [
                        evaluation_id,                                    # class evaluation id
                        str(i['single_evaluation_id']),                   # id for single evaluation
                        str(i['single_evaluation__completed']),           # has single evaluation been completed?
                        str(i['code']),                                   # code for item
                        recode(i['selected_likert_item'], i['recoded']),  # the likert item with right value
                        str(i['recoded']),                                # is item recoded?
                    ]
                    for i in all_items
                ]
            except ObjectDoesNotExist:
                print('Object does not exist!')

    def _get_data(self):
        return self.data

    def _calc_excluded_participants(self, dataframe, threshold: float):
        answered_items_count = dataframe.groupby('user').count()['likert']
        max_answers_from_users = answered_items_count.max()
        boundary_to_exclude_user = max_answers_from_users * threshold
        # get users below boundary
        users_below_boundary = answered_items_count[answered_items_count < boundary_to_exclude_user]
        self.excluded_participants = len(users_below_boundary)
        # filter out users beyond boundary from df if necessary
        if self.excluded_participants > 0:
            dataframe = dataframe[~ dataframe['user'].isin(list(users_below_boundary.index))]
        return dataframe

    def get_excluded_participants(self):
        return self.excluded_participants

    def _create_dataframe(self):
        df = pd.DataFrame(self._get_data())
        df.columns = self.columns
        # get the category number for sorting
        df['cat1'] = df['item'].apply(lambda x: int(x.split("_")[1]))
        df['cat2'] = df['item'].apply(lambda x: int(x.split("_")[2]))
        df['cat3'] = df['item'].apply(lambda x: int(x.split("_")[3]))
        sort_by = self.sort_df_by + ['cat1', 'cat2', 'cat3']
        df.sort_values(by=sort_by, inplace=True)
        df.reset_index(drop=True, inplace=True)
        # don't need the 'cat*' columns anymore as it was only for sorting
        df.drop(columns=['cat1', 'cat2', 'cat3'], inplace=True)
        # filter out users who answered items below boundary
        df = self._calc_excluded_participants(df, 0.25)
        return df

    def get_stats_per_dim(self):
        df = self._create_dataframe() if self.data else pd.DataFrame([])
        dims = {}
        if self.subject == "Allgemeine Lehrevaluation":
            keys = list(self.dimensions.keys())[:-2]
        else:
            keys = list(self.dimensions.keys())

        for i in keys:
            dims[i] = {
                "name": self.dimensions[i],
                "mean": 0.0,
                "std": 0.0,
                "median": 0,
                "counts": ([1, 2, 3, 4, 5], [0, 0, 0, 0, 0])
            }

            if df.shape[0] > 0:
                reg = '[a-z-]_' + i
                filtered = df[df.item.str.contains(reg, regex=True)]

                if len(filtered) > 0:
                    dims[i]["mean"] = round(filtered.likert.mean(), 2)
                    dims[i]["std"] = round(filtered.likert.std(), 2)
                    dims[i]["median"] = round(filtered.likert.median(), 0)
                    counts = sort_by_index_and_extract_counts(filtered.likert.value_counts())
                    if len(counts[0]) < 5:
                        dims[i]["counts"] = fill_up_5_item_likert_scale(counts)
                    else:
                        dims[i]["counts"] = counts
        return dims


def get_stats_per_part_per_dim(self):
    pass


def create_dim_barplot(datadict, key, fig_width, fig_height):
    x_axis = np.array([
        "Trifft \nnicht zu\n(1).",
        "Trifft eher\nnicht zu\n(2).",
        "Teils,\nteils\n(3).",
        "Trifft\neher zu\n(4).",
        "Trifft\nzu\n(5)."
    ])
    y_axis = np.array(datadict[key]["counts"][1])

    if y_axis.sum() == 0:
        rel_y_axis = (y_axis / 0.001) * 100
    else:
        rel_y_axis = (y_axis / y_axis.sum()) * 100

    rel_y_axis = rel_y_axis.astype(int)

    color = "#567EAE"

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.bar(x_axis, rel_y_axis, color=color)
    ax.xaxis.set_tick_params(labelsize=6)
    ax.set_yticks([])

    def set_axis_text(axis, idx, val, max_val):
        fontsize = "8"
        x_offset = 0.15 if val >= 10 else 0.075
        y_offset = max_val / 7
        correction = max_val / 11
        # is val in the upper 5th of max_val?
        if val >= max_val - (max_val / 5):
            return axis.text(idx - x_offset, val - y_offset - correction, str(val) + " %",
                             color="white", fontsize=fontsize, fontweight="bold")
        else:
            return axis.text(idx - x_offset, val + y_offset - correction, str(val) + " %",
                             color=color, fontsize=fontsize, fontweight="bold")

    max_y_val = rel_y_axis.max()

    for i, v in enumerate(rel_y_axis):
        set_axis_text(ax, i, v, max_y_val)

    imgdata = BytesIO()
    fig.savefig(imgdata, format='png')
    imgdata.seek(0)  # rewind the data

    # drawing = svg2rlg(imgdata)
    return imgdata


def count_answered_items(queryset) -> int:
    """
    Count the fully given answers in a SingleEvaluation (NWFG or not doesn't matter).
    :param: queryset: a django queryset of item model
    """
    return queryset.filter(selected_likert_item__isnull=False).count()
