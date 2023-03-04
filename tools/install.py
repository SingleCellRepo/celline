# from pathlib import Path
from __future__ import print_function
import sys
import glob
import os
import readline
import shutil
import subprocess
import sys
import time
from typing import List

import inquirer
from inquirer import Path, prompt
import tqdm


def spinner_gen():
    while 1:
        yield '|'
        yield '/'
        yield '-'
        yield '\\'


current_dir = os.getcwd()

pwd = sys.argv[1]
install_target_dir = sys.argv[2]
HOME = sys.argv[3]
# if "." in sys.argv[2]:
#     install_target_dir = os.path.abspath(f"{sys.argv[2]}")
# elif sys.argv[2].startswith("~"):
#     install_target_dir = sys.argv[2].replace("~", HOME)
# else:
#     install_target_dir = sys.argv[2]

# if not install_target_dir.endswith("/"):
#     install_target_dir += "/"
install_target_dir += "/celline"

questions = [
    inquirer.Confirm(
        name="confirm", message=f"Install to '{install_target_dir}' <-- '{pwd}'?", default=True
    ),
    # inquirer.Confirm(
    #     name="confirm",
    #     message=f"Install to '{install_target_dir}' ?",
    #     default=True
    # )
]
answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)
if answers is not None:
    if answers["confirm"] is False:
        quit()

# shutil.copytree(pwd, install_target_dir, dirs_exist_ok=True)

all_directories: List[str] = []
all_files: List[str] = []
print("Migrating install target")
for root, dirs, files in os.walk(top=f"{pwd}"):
    for dir in dirs:
        target_dir = os.path.join(root, dir).replace(pwd, "")
        if not "/." in target_dir:
            target_dir = "/".join(target_dir.split("/")[1:])
            all_directories.append(target_dir)
    for fil in files:
        target_file = os.path.join(root, fil).replace(pwd, "")
        if (
            (not "/." in target_file)
            and (not "test/" in target_file)
            and (not ".venv" in target_file)
            and (not ".mypy_cache" in target_file)
            and (not "__pycache__" in target_file)
        ):
            target_file = "/".join(target_file.split("/")[1:])
            all_files.append(target_file)

dir_iter_tqdm = tqdm.tqdm(all_directories)
for dir in dir_iter_tqdm:
    dir_iter_tqdm.set_description(f"Copying: {dir}")
    os.makedirs(f"{install_target_dir}/{dir}", exist_ok=True)
    dir_iter_tqdm.set_description("Copying Directory: Complete")

file_iter_tqdm = tqdm.tqdm(all_files)
for file in file_iter_tqdm:
    file_iter_tqdm.set_description(f"Copying: {file}")
    if os.path.isfile(f"{install_target_dir}/{file}"):
        os.remove(f"{install_target_dir}/{file}")
    shutil.copy(f"{pwd}/{file}", f"{install_target_dir}/{file}")
    file_iter_tqdm.set_description("Copying File: Complete")

# Install requirements
# Install poetry

# proc = subprocess.Popen("which poetry", stdout=subprocess.PIPE, shell=True)
# result = proc.communicate()
# poetry_path = result[0].decode("utf-8").replace("\n", "")
# install_poetry = True
# if poetry_path.startswith("/"):
#     questions = [
#         inquirer.Confirm(
#             name="install_poetry",
#             message=f"You have already installed the poetry at '{poetry_path}'.\nInstall poetry?",
#             default=False,
#         )
#     ]
#     answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)
#     if answers is not None:
#         if answers["install_poetry"] is False:
#             install_poetry = False
#             print(">> Skip installation of poetry.")
# if install_poetry:
#     proc = subprocess.Popen(
#         "curl -sSL https://install.python-poetry.org | python3 -",
#         shell=True,
#     )
#     result = proc.wait()

# SRA toolkit
proc = subprocess.Popen("which fastq-dump", stdout=subprocess.PIPE, shell=True)
result = proc.communicate()
sra_toolkit_path = result[0].decode("utf-8").replace("\n", "")
install_sra_toolkit = True
if sra_toolkit_path.startswith("/"):
    questions = [
        inquirer.Confirm(
            name="install_sratoolkit",
            message=f"You have already installed the sratookit'.\nInstall sratoolkit?",
            default=False,
        )
    ]
    answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)
    if answers is not None:
        if answers["install_sratoolkit"] is False:
            install_sra_toolkit = False

if install_sra_toolkit:
    questions = [
        inquirer.List(
            name="os",
            message=f"What is the architecture of the OS you are using?",
            choices=["CentOS_Linux", "Ubuntu_Linux", "MacOS", "cancel"],
        )
    ]
    answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)
    sratookit_install_path = ""
    if answers is not None:
        if answers["os"] == "CentOS_Linux":
            sratookit_install_path = "https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/3.0.2/sratoolkit.3.0.2-centos_linux64.tar.gz"
        elif answers["os"] == "Ubuntu_Linux":
            sratookit_install_path = "https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/3.0.2/sratoolkit.3.0.2-ubuntu64.tar.gz"
        elif answers["os"] == "MacOS":
            sratookit_install_path = "https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/3.0.2/sratoolkit.3.0.2-mac64.tar.gz"
        elif answers["os"] == "cancel":
            install_sra_toolkit = False
        else:
            raise TypeError("Unknown os selection.")
    if install_sra_toolkit:
        proc = subprocess.Popen(
            f"rm -rf {install_target_dir}/toolkits && cd {install_target_dir} && mkdir -p toolkits && cd toolkits && wget {sratookit_install_path} -O sratoolkit.tar.gz",
            shell=True,
        )
        result = proc.wait()
        proc = subprocess.Popen(
            f"cd {install_target_dir}/toolkits && tar -zxvf sratoolkit.tar.gz && mv {sratookit_install_path.split('/')[-1].replace('.tar.gz', '')} sratoolkit && rm sratoolkit.tar.gz",
            shell=True,
        )
        result = proc.wait()

proc = subprocess.Popen("echo ~", stdout=subprocess.PIPE, shell=True)
result = proc.communicate()
home_dir = result[0].decode("utf-8").replace("\n", "")
alias_text_to_rc = f"""
if [ -f {home_dir}/.cellinerc ]; then
    source {home_dir}/.cellinerc
fi
"""

proc = subprocess.Popen("echo $SHELL", stdout=subprocess.PIPE, shell=True)
result = proc.communicate()
shell_style = result[0].decode("utf-8").replace("\n", "")

if "bash" in shell_style:
    shell_rc = f"{home_dir}/.bashrc"
elif "zsh" in shell_style:
    shell_rc = f"{home_dir}/.zshrc"
else:
    questions = [
        inquirer.List(
            name="shellstyle",
            message=f"Could not find target shell style. which one?",
            choices=["Bash", "Zsh"],
        )
    ]
    answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)
    if answers is not None:
        if answers["shellstyle"] == "Bash":
            shell_rc = f"{home_dir}/.bashrc"
        elif answers["shellstyle"] == "Zsh":
            shell_rc = f"{home_dir}/.zshrc"
        else:
            raise TypeError("Unknown selection.")
    else:
        raise TypeError("Unknown selection.")


with open(shell_rc, "r") as f:
    lines = f.readlines()
if f"source {home_dir}/.cellinerc" not in "\n".join(lines):
    with open(shell_rc, "a") as f:
        f.write(alias_text_to_rc)

with open(f"{home_dir}/.cellinerc", "w") as f:
    f.write("## Celline rc file\n")
    rc_targetdata = [f'export PATH="{install_target_dir}/bin:$PATH"']
    if install_sra_toolkit:
        rc_targetdata.append(
            f'export PATH="{install_target_dir}/toolkits/sratoolkit/bin:$PATH"'
        )
    f.write("\n".join(rc_targetdata))
for root, dirs, files in os.walk(f"{install_target_dir}/bin"):
    for f in files:
        os.chmod(os.path.join(root, f), 0o777)
# questions = [
#     inquirer.Path(
#         "target_gsms",
#         message="PATH",
#         path_type="file"
#     )
# ]
# answers = inquirer.prompt(
#     questions
# )
# print(answers)
