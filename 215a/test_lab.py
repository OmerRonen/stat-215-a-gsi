import shutil
import subprocess
import os
import tempfile
import argparse
import logging

from git import Repo

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

gsi_dir = "/accounts/campus/omer_ronen/Documents/215a/stat-215-a-gsi"
git_at = open(os.path.join(gsi_dir, "215a", ".git_at")).readlines()[0].split("\n")[0]


def _get_args():
    parser = argparse.ArgumentParser(description='Testing 215A labs')
    parser.add_argument('lab_number', type=int, help='lab number to test')

    args = parser.parse_args()
    return args


def _get_repos():
    return [r.split("\n")[0] for r in open(os.path.join(gsi_dir, "data/repos"), "r").readlines()]


def _get_data_path(lab_number):
    return os.path.join(gsi_dir, f"lab{lab_number}", "data")


def _get_test_script(lab_number):
    return os.path.join(gsi_dir, f"lab{lab_number}", "test.sh")


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
        else:
            LOGGER.info(f"{git_user} passed the test")


def main():
    args = _get_args()
    lab_number = args.lab_number
    repos = _get_repos()
    for student in repos:
        test_lab(student, lab_number)


if __name__ == '__main__':
    main()
