import shutil
import subprocess
import os
import tempfile
import argparse
import logging
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .utils import gsi_dir, clone_repo, get_lab_repos, get_last_edit, DEADLINES, get_repo, is_local, \
    calculate_lab1_final_grade, report_grades

LOGGER = logging.getLogger(__name__)


def _get_args():
    parser = argparse.ArgumentParser(description='Testing 215A labs')
    parser.add_argument('lab_number', type=int, help='lab number to test')
    parser.add_argument('--code', action="store_true", help='if true we test code')
    parser.add_argument('--grade', action="store_true", help='if true we grade')

    args = parser.parse_args()
    return args


def _get_data_path(lab_number):
    return os.path.join(gsi_dir, f"lab{lab_number}", "data")


def _get_test_script(lab_number):
    return os.path.join(gsi_dir, f"lab{lab_number}", "test.sh")


def test_lab(git_user, lab_number):
    with tempfile.TemporaryDirectory(suffix=f"_{git_user}") as d:
        LOGGER.info(f"Testing {git_user}")
        submission_time = get_last_edit(git_user, f"lab{lab_number}/lab{lab_number}.pdf")
        on_time = time.localtime(submission_time) < DEADLINES.lab1
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
        compiled = os.path.isfile(os.path.join(lab_dir, "md_log.txt"))
        return {"test": compiled, "on time": on_time}


def _get_peer_review(git_user, lab_number):
    data = pd.read_csv(os.path.join(gsi_dir, "gsi", f"pr_lab{lab_number}.csv"), index_col=0)
    reviewers = data.iloc[:, 0]
    r_1 = reviewers[data.iloc[:, 1] == git_user].iloc[0]
    try:
        r_2 = reviewers[data.iloc[:, 2] == git_user].iloc[0]
        user_reviewers = [r_1, r_2]
    except IndexError:
        user_reviewers = [r_1]
    reports = []
    for i, r in enumerate(user_reviewers):
        with tempfile.TemporaryDirectory() as d:
            _ = get_repo(r, d)
            peer_review_file = os.path.join(d, f"lab{lab_number}/peer_review/student_{i}/report.csv")
            if os.path.isfile(peer_review_file):
                with open(peer_review_file, encoding="utf8", errors='ignore') as f:
                    pr_data = pd.read_csv(f)
                reports.append(pr_data)

    return pd.concat(reports, axis=0)


def get_student_lab(git_user, lab_number):
    user_path = os.path.join(gsi_dir, f"lab{lab_number}", "students_labs", git_user)
    if not os.path.exists(user_path):
        os.mkdir(user_path)
    with tempfile.TemporaryDirectory() as d:
        _ = get_repo(git_user=git_user, d=d)

        report_file = os.path.join(d, f"lab{lab_number}/lab{lab_number}.pdf")
        shutil.copyfile(report_file, os.path.join(user_path, f"lab{lab_number}.pdf"))
    peer_review = _get_peer_review(git_user, lab_number)
    peer_review.to_csv(os.path.join(user_path, "peer_review.csv"))


def main():
    args = _get_args()
    lab_number = args.lab_number
    test_code = args.code
    grade = args.grade

    grades = {}

    report = {}
    repos = get_lab_repos(lab_number)
    report_fname = os.path.join(gsi_dir, "gsi", f"lab{lab_number}_report.csv")
    for student in repos:
        if grade:
            grades[student] = calculate_lab1_final_grade(student)
        elif test_code:
            if not is_local or True:
                report[student] = test_lab(student, lab_number)
                pd.DataFrame(report).to_csv(report_fname, index=[0])

            else:
                report = pd.read_csv(report_fname, index_col=0)
                has_passed = report.loc[:, student].test
                if not has_passed:
                    test_result = test_lab(student, lab_number)
                    report.loc["test", student] = test_result['test']
                    report.to_csv(report_fname)
        else:
            get_student_lab(student, lab_number)
    if grade:
        grades = pd.DataFrame(grades)
        grades.to_csv(os.path.join(gsi_dir, "data", "labs", "lab1", "grades_final.csv"))
        final_grades = np.array(grades.loc["Final",:].values).astype(np.float)
        final_grades = final_grades[np.invert(np.isnan(final_grades))]
        plt.hist(final_grades)
        plt.title("Lab 1 Final Grades")
        plt.xlabel("Grade (Out of 70)")
        plt.savefig(os.path.join(gsi_dir, "data", "labs", "lab1", "grades_final.png"))
        for s in repos:
            # if s not in ["xinzhou97", "aashen12", "ishaans99"]:
            #     continue
            report_grades(s)


if __name__ == '__main__':
    main()
