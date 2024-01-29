import os
import argparse
import time
from datetime import datetime

parser = argparse.ArgumentParser()

parser.add_argument(
    "export_dir", help="directory from where to backup the exports"
)

parser.add_argument(
    "directory", help="backup directory to move files to"
)

parser.add_argument(
    "user", help="name of the user to give permissions for the backup directory"
)

parser.add_argument(
    "-c", "--clean", required=False,
    help="Specify the cleaning of the directory before moving files to backup. "
         "Must be followed by a value of how many days will be kept (default: 3).",
    action="store_true"
)

parser.add_argument(
    "-d", "--days_to_keep", help="Specify the days to keep files.",
    type=int, required=False
)

args = parser.parse_args()

export_dir = args.export_dir
days_to_keep = args.days_to_keep or 3
backup_dir = args.directory
user = args.user


def get_file_date(file_str):
    name, extension = file_str.split(".")
    _, date_str = name.split("_")
    return datetime.strptime(date_str, "%Y-%m-%d")


def clean_files(days):
    os.chdir(export_dir)
    filelist = os.listdir()
    file_date_list = []
    for file in filelist:
        if file.startswith("export") and file.endswith(".csv"):
            file_date_list.append({"name": file, "date": get_file_date(file)})

    now = datetime.now()

    for file_dict in file_date_list:
        delta = now - file_dict["date"]
        if delta.days > days:
            os.remove(file_dict["name"])


if __name__ == "__main__":

    os.chdir(export_dir)

    if args.clean:
        clean_files(days_to_keep)

    time.sleep(5)

    os.system(f"rsync -avh --delete ./ {backup_dir}/")

    os.system(f"chown -R {user}:www-data {backup_dir}")
