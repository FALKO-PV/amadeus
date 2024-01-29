import json
from collections import defaultdict


def split_code(code: str) -> dict[str]:

    name_fach, *dims = code.split("_")

    name, *fach = name_fach.split("-")

    fach = fach[0] if bool(len(fach)) else None

    match len(dims):
        case 1:
            dim, subdim, item = dims[0], None, None
        case 2:
            dim, subdim, item = dims[0], dims[1], None
        case 3:
            dim, subdim, item = dims[0], dims[1], dims[2]

    return {
        'name': name,
        'fach': fach,
        'dim': dim,
        'subdim': subdim,
        'item': item
    }


def map_csv_to_json(csv_file_name='final_codes.csv', json_file_name='question_pool.json'):

    subject = {
        'ger': 'Deutsch',
        'eng': 'Englisch',
        'rel': 'Evangelische Religion',
        'lat': 'Latein',
        'mat': 'Mathematik',
        'mus': 'Musik'
    }

    ud = "unspecific_dimensions"
    sd = "specific_dimension"

    out_dict = {
        ud: {'1': {}},
        sd: {'8': {
                'dimension_name': 'Ästhetik',
                'subjects': {}
            },
            '9': {
                'dimension_name': 'Fachspezifik',
                'subjects': {}
            }
        }
    }

    cur_subdim = ""
    fach = ""
    idx = None

    with open(csv_file_name, 'r', encoding='utf-8') as csv_file:

        lines = [line.strip() for line in csv_file.readlines()]

    for line in lines:

        if line.startswith("\ufeff"):
            continue

        code, text, exclusive, recode = line.split(";")

        text = text.replace('"', '').strip()
        recode = recode.replace('\n', '').strip()

        code_info = split_code(code)

        if code_info['fach']:
            fach = subject[code_info['fach']]

        # sort general items into "unspecific_dimensions"
        if not code_info['fach']:

            # at first dimension
            if not code_info['subdim'] and not code_info['item']:

                idx = 1

                out_dict[ud][code_info['dim']] = {'dimension_name': text, 'pool': {}}

            elif code_info['subdim'] and not code_info['item']:

                cur_subdim = text

            else:
                if not idx:
                    idx = 1

                out_dict[ud][code_info['dim']]['pool'][code] = {
                    'nwfg_study_exclusive': bool(int(exclusive)),
                    'recode': bool(int(recode)),
                    'index': idx,
                    'question_text': text,
                    'subdimension': cur_subdim,
                }

                idx += 1

        else:
            # add subject specific content
            if code_info['dim'] and not code_info['subdim']:

                idx = 1

            elif code_info['subdim'] and not code_info['item']:

                cur_subdim = text

            elif code_info['subdim'] and code_info['item']:

                if not fach in out_dict[sd][code_info['dim']]['subjects']:
                    out_dict[sd][code_info['dim']]['subjects'][fach] = {}

                if 'pool' in out_dict[sd][code_info['dim']]['subjects'][fach]:

                    out_dict[sd][code_info['dim']]['subjects'][fach]['pool'][code] = {
                        'nwfg_study_exclusive': bool(int(exclusive)),
                        'recode': bool(int(recode)),
                        'index': idx,
                        'question_text': text,
                        'subdimension': cur_subdim,
                    }

                    idx += 1

                else:
                    out_dict[sd][code_info['dim']]['subjects'][fach]['pool'] = {}
                    out_dict[sd][code_info['dim']]['subjects'][fach]['pool'][code] = {
                        'nwfg_study_exclusive': bool(int(exclusive)),
                        'recode': bool(int(recode)),
                        'index': idx,
                        'question_text': text,
                        'subdimension': cur_subdim,
                    }

                    idx += 1


    with open(json_file_name, 'w', encoding='utf-8') as json_file:

        json.dump(out_dict, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    map_csv_to_json()
