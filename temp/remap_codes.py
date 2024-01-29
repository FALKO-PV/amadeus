mapping = {
        "ats": "sel",
        "koa": "coa",
        "uub": "pra",
        "fas": "fas",
        "uls": "ssl",
        "seu": "soe",
        "klf": "crm",
        "aes": "aes",
        "de": "ger",
        "en": "eng",
        "re": "rel",
        "la": "lat",
        "ma": "mat",
        "mu": "mus",
        "fps": "dsp"
        }

with open("codes_recoded_enc_221219.csv", "r") as read_csv:
    val_list = [line.split(";") for line in read_csv.readlines()]

new_list = []

for el in val_list:
    if el[0] == "\ufeffcode":
        continue
    first_part = el[0].split("_")
    start = first_part[0]
    print(start)
    if len(start) > 3:
        fst, scd = start.split("-")
        new_start = mapping[fst] + "-" + mapping[scd]
    else:
        new_start = mapping[start]

    new_first_part = "_".join([new_start] + first_part[1:])

    new_line = ";".join([new_first_part] + el[1:])

    new_list.append(new_line.replace('"""', '"'))

with open("final_codes.csv", "w") as save_csv:
    for val in new_list:
        save_csv.write(val)
