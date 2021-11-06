import os
import shutil
import socket
import tempfile
import time
import yaml

import pandas as pd
import numpy as np

from collections import namedtuple
from git import Repo

gsi_dir_scf = "/accounts/campus/omer_ronen/Documents/215a/stat-215-a-gsi"
gsi_dir_local = "/Users/omerronen/Documents/Phd/215a2021/stat-215-a-gsi"
is_local = socket.gethostname() == "Omers-MacBook-Pro-2.local"

gsi_dir = gsi_dir_local if is_local else gsi_dir_scf
git_at = open(os.path.join(gsi_dir, "gsi", ".git_at")).readlines()[0].split("\n")[0]

REPOS = [r.split("\n")[0] for r in open(os.path.join(gsi_dir, "data/repos"), "r").readlines()]
Deadlines = namedtuple("Deadlines", "lab1 pr_lab1 lab2")
DEADLINES = Deadlines(lab1=time.strptime("17 Sep 21 00", "%d %b %y %H"),
                      pr_lab1=time.strptime("27 Sep 21 00", "%d %b %y %H"),
                      lab2=time.strptime("08 Oct 21 00", "%d %b %y %H"))


def clone_repo(git_user, local_directory):
    git_repo = f"https://OmerRonen:{git_at}@github.com/{git_user}/stat-215-a.git"
    Repo.clone_from(git_repo, local_directory)

    # cmd = f"git clone https://OmerRonen:{git_at}@github.com/{git_user}/stat-215-a.git  {local_directory}"
    # LOGGER.info(cmd)
    # process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # # while len(os.listdir(local_directory)) == 0:
    # process.wait()
    # out, err = process.communicate()

    # if err:
    #     raise OSError('The process raised an error:', err.decode())


def get_repo(git_user, d):
    clone_repo(git_user, d)

    repo = Repo(d)
    return repo


def get_last_edit(git_user, filename):
    with tempfile.TemporaryDirectory() as d:
        repo = get_repo(git_user, d)
        commits = repo.iter_commits('--all')
        for commit in commits:
            commit_files = [f.lower() for f in commit.stats.files]
            if filename in commit_files:
                return commit.committed_date


def get_lab_repos(lab_number):
    lab_repos_file = os.path.join(gsi_dir, "gsi", f"lab{lab_number}.yaml")
    if os.path.isfile(lab_repos_file):
        return yaml.load(open(lab_repos_file, "r"))['repos']
    active_repos = []

    for r in REPOS:
        print(r)
        with tempfile.TemporaryDirectory() as d:
            clone_repo(r, d)
            lab_1_f = os.path.join(d, f"lab{lab_number}")
            if not os.path.exists(lab_1_f):
                continue
            lab1_files = os.listdir(lab_1_f)

            submitted = len([f for f in lab1_files if f.split(".")[0].endswith("blind")]) >= 1
            if submitted:
                active_repos.append(r)

    with open(lab_repos_file, "w") as stream:
        yaml.dump({"repos": active_repos}, stream)
    return active_repos


def _get_student_data(git_user, df):
    idx = np.where(df.iloc[:, 0] == git_user)[0][0]
    return df.iloc[idx, :]


def calculate_final_grade(git_user, lab_number):
    if lab_number == 1:
        return calculate_lab1_final_grade(git_user)
    elif lab_number == 2:
        return calculate_lab2_final_grade(git_user)


def calculate_lab2_final_grade(git_user):
    grade = {}
    part1 = pd.read_csv(os.path.join(gsi_dir, "data", "labs", "lab1", "part1.csv"), index_col=0)
    part2 = pd.read_csv(os.path.join(gsi_dir, "data", "labs", "lab1", "part2.csv"), index_col=0)
    hw = pd.read_csv(os.path.join(gsi_dir, "data", "labs", "lab1", "hw.csv"), index_col=0)
    report = pd.read_csv(os.path.join(gsi_dir, "data", "labs", "lab1", "report.csv"), index_col=0)
    try:
        hw_user = _get_student_data(git_user, hw)
        part2_user = _get_student_data(git_user, part2)
        part1_user = _get_student_data(git_user, part1)

    except IndexError:
        return
    report_user = report.loc[:, git_user]

    hw_grade = hw_user.q1 * 4
    hw_comments = hw_user.iloc[4]
    on_time = report_user[1]
    grade['Homework (10)'] = hw_grade
    grade['hw comments'] = hw_comments
    grade['Code (10)'] = 10 * report_user.test
    grade["Submitted on Time"] = on_time
    grade['Reality Check (10)'] = part1_user.loc['Reality check'] * 2.5
    grade["comments (1-2)"] = part1_user.loc['comments on 1-3']
    grade['EDA (10)'] = 0.5 * (
            len(part1_user.loc['Cleaning'].split(",")) + part1_user.loc['Level of transparency'] \
            + part1_user.loc['Relevance of plots'] * 2.5)
    grade['Stability (10)'] = part2_user.loc["Stability"] * 2
    grade['Critique (10)'] = part2_user.loc["Critique"] * 2
    grade['Findings (10)'] = 1 + (
            part2_user.loc["Finding 1"] + part2_user.loc["Finding 2"] + part2_user.loc["Finding 3"])
    grade['Comments (3-5)'] = part2_user.loc["Comments"]

    part1_grade = grade['Reality Check (10)'] + grade['EDA (10)']
    part2_grade = grade['Stability (10)'] + grade['Findings (10)'] + grade['Critique (10)']
    grade['Final'] = part1_grade + part2_grade + hw_grade - 1 * (1 - on_time) + grade['Code (10)']

    return grade


def calculate_lab1_final_grade(git_user):
    grade = {}
    part1 = pd.read_csv(os.path.join(gsi_dir, "data", "labs", "lab1", "part1.csv"), index_col=0)
    part2 = pd.read_csv(os.path.join(gsi_dir, "data", "labs", "lab1", "part2.csv"), index_col=0)
    hw = pd.read_csv(os.path.join(gsi_dir, "data", "labs", "lab1", "hw.csv"), index_col=0)
    report = pd.read_csv(os.path.join(gsi_dir, "data", "labs", "lab1", "report.csv"), index_col=0)
    try:
        hw_user = _get_student_data(git_user, hw)
        part2_user = _get_student_data(git_user, part2)
        part1_user = _get_student_data(git_user, part1)

    except IndexError:
        return
    report_user = report.loc[:, git_user]

    hw_grade = hw_user.q1 * 4
    hw_comments = hw_user.iloc[4]
    on_time = report_user[1]
    grade['Homework (10)'] = hw_grade
    grade['hw comments'] = hw_comments
    grade['Code (10)'] = 10 * report_user.test
    grade["Submitted on Time"] = on_time
    grade['Reality Check (10)'] = part1_user.loc['Reality check'] * 2.5
    grade["comments (1-2)"] = part1_user.loc['comments on 1-3']
    grade['EDA (10)'] = 0.5 * (len(part1_user.loc['Cleaning'].split(",")) + part1_user.loc['Level of transparency'] \
                               + part1_user.loc['Relevance of plots'] * 2.5)
    grade['Stability (10)'] = part2_user.loc["Stability"] * 2
    grade['Critique (10)'] = part2_user.loc["Critique"] * 2
    grade['Findings (10)'] = 1 + (
            part2_user.loc["Finding 1"] + part2_user.loc["Finding 2"] + part2_user.loc["Finding 3"])
    grade['Comments (3-5)'] = part2_user.loc["Comments"]

    part1_grade = grade['Reality Check (10)'] + grade['EDA (10)']
    part2_grade = grade['Stability (10)'] + grade['Findings (10)'] + grade['Critique (10)']
    grade['Final'] = part1_grade + part2_grade + hw_grade - 1 * (1 - on_time) + grade['Code (10)']

    return grade


def report_grades(student, lab_number):
    grade_data = calculate_final_grade(student, lab_number)
    peer_reviews_file = os.path.join(os.path.join(gsi_dir, f"lab{lab_number}", "students_labs", student, "peer_review.csv"))
    with tempfile.TemporaryDirectory(suffix=student) as d:
        clone_repo(student, d)
        repo = Repo(d)
        lab_feedback = os.path.join(d, f"lab{lab_number}", "feedback")
        if not os.path.exists(lab_feedback):
            os.mkdir(lab_feedback)
        pr_file = os.path.join(lab_feedback, "peer_review.csv")
        feedback_file = os.path.join(lab_feedback, "feedback.csv")
        shutil.copyfile(peer_reviews_file, pr_file)
        pd.DataFrame(grade_data, index=[0]).to_csv(feedback_file)

        repo.git.add(os.path.join(gsi_dir, "gsi", feedback_file))
        repo.git.add(os.path.join(gsi_dir, "gsi", pr_file))
        repo.index.commit("feedback")
        origin = repo.remote(name='origin')
        try:
            origin.push()
        except Exception:
            pass
        shutil.rmtree(d)
