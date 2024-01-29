import json
import matplotlib.pyplot as plt
# from matplotlib import rcParams
# import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO
# from svglib.svglib import svg2rlg

from django.core.exceptions import ObjectDoesNotExist
from evaluation_tool.models import SingleEvaluation, Item, NWFGSingleEvaluation, NWFGItem, NWFGEvaluation, \
    NWFGEvaluationPart, ClassEvaluation


def recode(n: int, has_to_be_recoded: bool) -> int:
    assert isinstance(n, int) and 1 <= n <= 5, "argument must be an integer between 1 and 5"
    return n - ((n - 3) * 2) if has_to_be_recoded else n


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


def create_item_list(subject: str, is_nwfg: bool):
    """
    return a list of all item names from the json question pool
    :param subject: teaching subject
    :param is_nwfg:
    :return: list of all item names
    """
    items = []
    with open("static/data/question_pool.json", "r", encoding="utf-8") as file:
        question_pool_dict = json.loads(file.read())

    for dim in question_pool_dict["unspecific_dimensions"]:
        for key in question_pool_dict["unspecific_dimensions"][dim]["pool"].keys():
            if is_nwfg:
                items.append(key)
            else:
                if not question_pool_dict["unspecific_dimensions"][dim]["pool"][key]["nwfg_study_exclusive"]:
                    items.append(key)

    if subject != "Allgemeine Lehrevaluation":
        for dim in question_pool_dict["specific_dimension"]:
            for key in question_pool_dict["specific_dimension"][dim]["subjects"][subject]["pool"].keys():
                if is_nwfg:
                    items.append(key)
                else:
                    if not question_pool_dict["specific_dimension"][dim]["subjects"][subject]["pool"][key]["nwfg_study_exclusive"]:
                        items.append(key)
    return items


def count_answered_items(queryset) -> int:
    """
    Count the fully given answers in a SingleEvaluation (NWFG or not doesn't matter).
    :param: queryset: a django queryset of item model
    """
    return queryset.filter(selected_likert_item__isnull=False).count()


class DataAnalyzer:

    def __init__(self, evaluation_id: str, is_nwfg: bool = False):
        self.is_nwfg = is_nwfg
        try:
            self.evaluation_id = evaluation_id
        except ObjectDoesNotExist:
            raise Exception(f"Evaluation with id {evaluation_id} does not exist")

        self.excluded_participants = 0

        # build the data_dict which holds all the given answers (Item.selected_likert_item /
        # NWFGItem.selected_likert_item) of an ClassEvaluation or all the erhebungszeitpunkte of a NWFGEvaluation.
        self.data_dict = {}

        if self.is_nwfg:
            evaluation_obj = NWFGEvaluation.objects.get(nwfg_evaluation_id=self.evaluation_id)

            self.subject = evaluation_obj.subject
            # get the IDs from all items in specified item pools
            nwfg_items = create_item_list(self.subject, is_nwfg=True)

            # get the answers from the NWFGEvaluation
            evaluation_parts = NWFGEvaluationPart.objects.filter(nwfg_evaluation=self.evaluation_id)

            current_erhebungszeitpunkt = evaluation_obj.current_erhebungszeitpunkt
            # there are max 3 erhebungszeitpunkte
            # we need to gather_data_from_dict all items for one erhebungszeitpunkt
            # but those erhebungszeitpunkte are divided into max two befragungsrunden which equal an evaluation_part
            for i in range(1, current_erhebungszeitpunkt + 1):
                self.data_dict[i] = {}
                for part in evaluation_parts:
                    if part.erhebungszeitpunkt == i:
                        q = NWFGSingleEvaluation.objects.filter(nwfg_evaluation_part=part.nwfg_evaluation_part_id)
                        for se in q:
                            if se.completed:
                                f = NWFGItem.objects.filter(nwfg_single_evaluation=se.nwfg_single_evaluation_id)
                                if "id" in self.data_dict[i].keys():
                                    self.data_dict[i]["id"].append(
                                        str(se.nwfg_single_evaluation_id))  # convert uuid to string
                                else:
                                    self.data_dict[i]["id"] = [str(se.nwfg_single_evaluation_id)]  # convert uuid to string
                                # check for any possible item code
                                for item in nwfg_items:
                                    get_item = f.filter(code=item)
                                    # if code is found in current survey
                                    if 0 < len(get_item) < 2:
                                        # add likert item
                                        n = get_item[0].selected_likert_item
                                        if get_item[0].code in self.data_dict[i].keys():
                                            self.data_dict[i][get_item[0].code].append(recode(n, get_item[0].recoded))
                                        else:
                                            self.data_dict[i][get_item[0].code] = [recode(n, get_item[0].recoded)]
                                    # if code is not found add a Numpy NaN type
                                    else:
                                        if item in self.data_dict[i].keys():
                                            self.data_dict[i][item].append(np.NaN)
                                        else:
                                            self.data_dict[i][item] = [np.NaN]

        else:
            class_evaluation = ClassEvaluation.objects.get(
                class_evaluation_id=evaluation_id
            )
            self.subject = class_evaluation.subject

            items = create_item_list(self.subject, is_nwfg=False)
            answers_needed = int(len(items) / 4)

            # get the answers from the ClassEvaluation
            q = SingleEvaluation.objects.filter(class_evaluation_id=self.evaluation_id)
            for se in q:
                # only grab items from completed SingleEvaluations!
                f = Item.objects.filter(single_evaluation_id=se.single_evaluation_id)
                if count_answered_items(f) >= answers_needed:
                    if "id" in self.data_dict.keys():
                        self.data_dict["id"].append(str(se.single_evaluation_id))  # convert uuid to string
                    else:
                        self.data_dict["id"] = [str(se.single_evaluation_id)]  # convert uuid to string
                    for item in items:
                        get_item = f.filter(code=item)
                        if 0 < len(get_item) < 2:
                            n = get_item[0].selected_likert_item
                            if n and get_item[0].code in self.data_dict.keys():
                                self.data_dict[get_item[0].code].append(recode(n, get_item[0].recoded))
                            elif n:
                                self.data_dict[get_item[0].code] = [recode(n, get_item[0].recoded)]
                            elif not n and item in self.data_dict.keys():
                                self.data_dict[item].append(np.NaN)
                            else:
                                self.data_dict[item] = [np.NaN]
                        else:
                            if item in self.data_dict.keys():
                                self.data_dict[item].append(np.NaN)
                            else:
                                self.data_dict[item] = [np.NaN]
                else:
                    self.excluded_participants += 1

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

    def get_data_dict(self) -> dict:
        return self.data_dict

    def get_excluded_participants(self) -> int:
        return self.excluded_participants

    def build_dims(self, data_dict):
        """
        Return a dictionary with all the means and standard deviations per dimension for an evaluation or
        current evaluation part if NWFG.
        :return: dict(int(=dimension) {"name": str, "mean": float, "std": float, "median": float, "counts": tuple})
        """

        df = pd.DataFrame(data_dict)
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

            # we filter by column names since last two digits of item.code give dim & subdim
            reg = '[a-z-]*_' + i

            filtered = df.filter(regex=reg)
            filtered_np_array = np.array(filtered)

            # only add the stats when there are suitable values
            if len(list(filtered)) > 0:
                dims[i]["mean"] = round(np.nanmean(filtered_np_array), 2)
                dims[i]["std"] = round(np.nanstd(filtered_np_array, ddof=1), 2)
                try:
                    dims[i]["median"] = int(np.nanmedian(filtered_np_array))
                except ValueError:
                    dims[i]["median"] = np.nanmedian(filtered_np_array)
                counts = np.unique(filtered_np_array[~np.isnan(filtered_np_array)], return_counts=True)  # counts per likert scale dim
                dims[i]["counts"] = ([int(count) for count in counts[0].tolist()], counts[1].tolist())  # map ndarray to list for json dumping
                if len(dims[i]["counts"][0]) < 5:
                    fill_up_5_item_likert_scale(dims[i]["counts"])

        return dims

    def get_stats_per_dim(self) -> dict:
        """Allocate the dimensions if evaluation is nwfg"""
        if self.is_nwfg:
            # there are max 3 erhebungszeitpunkte to the dimensions
            dims = {}
            for key, value in self.data_dict.items():
                dims[key] = self.build_dims(value)

            return dims
        else:
            return self.build_dims(self.data_dict)

    def create_csv_output(self, is_nwfg):
        """
        ToDo: more output?
        :return:
        """
        output = []

        csv_header = [
            "Dimension",
            "Mittelwert",
            "Standardabweichung",
            "Median",
            "trifft nicht zu",
            "trifft eher nicht zu",
            "trifft teils teils zu",
            "trifft eher zu",
            "trifft zu"
        ]

        output.append(csv_header)

        def replace_umlauts(s: str) -> str:
            """replace all german umlauts with ascii equivalents"""
            mapping = {"ä": "ae", "ü": "ue", "ö": "oe", "Ä": "Ae", "Ü": "Ue", "Ö": "Oe", "ß": "ss"}
            for k in mapping.keys():
                s = s.replace(k, mapping[k])
            return s

        stats = self.get_stats_per_dim()

        if is_nwfg:
            for key in stats.keys():
                for i in self.dimensions.keys():
                    stats_row = [
                        replace_umlauts(self.dimensions[i]),
                        round(stats[key][i]["mean"], 2),
                        round(stats[key][i]["std"], 2),
                        stats[key][i]["median"]
                    ]

                    idx = 0  # index for numpy arrays in counts tuple
                    for j in range(5):
                        if j + 1 in stats[key][i]["counts"][0]:  # not every likert item must be chosen
                            stats_row.append(stats[key][i]["counts"][1][idx])
                            idx += 1
                        else:  # if likert item is not chosen put 0
                            stats_row.append(0)

                    output.append(stats_row)
        else:
            if self.subject == "Allgemeine Lehrevaluation":
                keys = list(self.dimensions.keys())[:-2]
            else:
                keys = list(self.dimensions.keys())

            for i in keys:
                stats_row = [
                    replace_umlauts(self.dimensions[i]),
                    str(round(stats[i]["mean"], 2)).replace(".", ","),
                    str(round(stats[i]["std"], 2)).replace(".", ","),
                    str(stats[i]["median"]).replace(".", ",")
                ]

                idx = 0  # index for numpy arrays in counts tuple
                for j in range(5):
                    if j + 1 in stats[i]["counts"][0]:  # not every likert item must be chosen
                        stats_row.append(stats[i]["counts"][1][idx])
                        idx += 1
                    else:  # if likert item is not chosen put 0
                        stats_row.append(0)

                output.append(stats_row)

        return output


# def create_bullet_graph(counts, dimension_name, mean, imgdata, pos_x_ticks=None):
#     plt.switch_backend('Agg')  # necessary to subdue matplotlib from creating empty graph windows
#     rcParams['font.family'] = 'monospace'
#     # remove x labels and ticks
#     plt.tick_params(
#         axis='x',          # changes apply to the x-axis
#         which='both',      # both major and minor ticks are affected
#         bottom=False,      # ticks along the bottom edge are off
#         top=False,         # ticks along the top edge are off
#         labelbottom=False)
#     # clear all existing axis and figures
#     plt.cla()
#     plt.clf()
#
#     # calc parameters
#     limits = list(np.array(counts).cumsum())
#     max_limit = max(limits)
#     limits_in_percentage = [round(limit / max_limit * 100, 2) for limit in limits]
#     proportional_mean = mean * 100 / len(limits)
#
#     sns_color_palette = sns.color_palette("rocket_r", len(limits))
#
#     # create new axes to work on
#     fig = plt.figure(figsize=(5, 1))
#     axs = plt.axes()
#
#     # draw the plot
#     axs.set_aspect("equal")
#
#     # get position of xticks
#     if pos_x_ticks == "upper":
#         axs.xaxis.tick_top()
#         axs.xaxis.set_label_position('top')
#     elif pos_x_ticks == "na":
#         axs.set(xticklabels=[])
#         axs.set(xlabel=None)
#         axs.tick_params(axis='both', which='both', length=0)
#
#     # axs.yaxis.tick_right() # previously y_label was at the right position of graph
#     axs.set_yticks([1])
#
#     def get_num_from_dim_name(dim_name):
#         # return the number of the dimension with a trailing dot
#         match int(dim_name[0]):
#             case 6 | 7:
#                 return dim_name[:3]
#             case _:
#                 return dim_name[:2]
#
#     axs.set_yticklabels([f"{get_num_from_dim_name(dimension_name)} "])
#     prev_limit = 0
#
#     for idx, lim in enumerate(limits_in_percentage):
#         axs.barh([1], lim - prev_limit, left=prev_limit, height=16, color=sns_color_palette[idx])
#         prev_limit = lim
#
#     axs.barh([1], proportional_mean, color="white", height=4)
#
#     fig.savefig(imgdata, format="svg")
#
#     return imgdata
