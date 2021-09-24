import shutil
import subprocess
import os
import tempfile
import argparse
import logging

import pandas as pd

from .utils import gsi_dir, clone_repo, REPOS, get_lab_repos

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def _get_args():
    parser = argparse.ArgumentParser(description='Testing 215A labs')
    parser.add_argument('lab_number', type=int, help='lab number to test')

    args = parser.parse_args()
    return args


def _get_data_path(lab_number):
    return os.path.join(gsi_dir, f"lab{lab_number}", "data")


def _get_test_script(lab_number):
    return os.path.join(gsi_dir, f"lab{lab_number}", "test.sh")


def test_lab(git_user, lab_number):
    with tempfile.TemporaryDirectory(suffix=f"_{git_user}") as d:
        LOGGER.info(f"Testing {git_user}")
        clone_repo(git_user, d)
        LOGGER.info(f"files are {os.listdir(d)}")
        lab_dir = os.path.join(d, f"lab{lab_number}")
        if not os.path.exists(lab_dir):
            LOGGER.warning(f"{git_user} failed the test!!!")
            return

        shutil.copyfile(_get_test_script(lab_number), os.path.join(lab_dir, "test.sh"))
        data_dir = os.path.join(lab_dir, "data")
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir, ignore_errors=True)
        shutil.copytree(_get_data_path(lab_number), data_dir)
        subprocess.run(f"bash test.sh .", cwd=lab_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        LOGGER.info(f"dir is {os.listdir(lab_dir)}")
        if os.path.isfile(os.path.join(lab_dir, "md_log.txt")):
            LOGGER.warning(f"{git_user} failed the test!!!")
            return False
        else:
            LOGGER.info(f"{git_user} passed the test")
            return True


def main():
    args = _get_args()
    lab_number = args.lab_number
    report = {}
    for student in get_lab_repos(lab_number):
        report[student] = test_lab(student, lab_number)
    pd.DataFrame(report).to_csv(os.path.join(gsi_dir, "gsi", f"lab{lab_number}_report.csv"))


if __name__ == '__main__':
    main()
