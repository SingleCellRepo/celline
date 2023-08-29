import os
import subprocess

from setuptools import Command, find_packages, setup
from setuptools.command.install import install
from tqdm import tqdm
import yaml


class CustomInstallCommand(install):
    """Custom command to prompt user for R path and install R packages"""

    def run(self):
        install.run(self)


# pyenv.yamlからPythonパッケージを取得する
with open("pyenv.yaml", "r", encoding="utf-8") as file:
    python_dependencies = yaml.safe_load(file)

install_requires = [
    f"{package['name']}=={package['version']}" for package in python_dependencies
]

setup(
    name="celline",
    version="0.1.5",
    packages=find_packages(),
    include_package_data=True,  # パッケージに非Pythonファイルを含めるために必要
    package_data={
        # bashやRなどの外部ファイルを追加
        "": ["*.sh", "*.R", "*.yaml"],
    },
    install_requires=install_requires,
    cmdclass={
        "install": CustomInstallCommand,
    },
)
