from setuptools import setup, find_packages, Command
from setuptools.command.install import install
from tqdm import tqdm
import subprocess
import os
import yaml


def get_r_path():
    try:
        r_path = subprocess.check_output(["which", "R"]).decode().strip()
    except subprocess.CalledProcessError:
        r_path = ""
    return r_path


class CustomInstallCommand(install):
    """Custom command to prompt user for R path and install R packages"""

    def run(self):
        # ユーザーにRのパスを尋ねる
        default_r_path = get_r_path()
        # r_path = (
        #     input(f"Enter path of R (default is '{default_r_path}'): ")
        #     or default_r_path
        # )

        # # renv.yamlからRパッケージを取得する
        # with open("renv.yaml", "r", encoding="utf-8") as f:
        #     r_dependencies = yaml.safe_load(f)

        # # 全パッケージ数をカウント
        # total_packages = sum(len(packages) for packages in r_dependencies.values())

        # # tqdmのプログレスバーを作成
        # pbar = tqdm(total=total_packages, desc="Installing R packages")

        # # それぞれのパッケージをインストール
        # for install_function, packages in r_dependencies.items():
        #     for package in packages:
        #         package_name = package["name"]
        #         version = package.get("version", "")
        #         args = ", ".join([f'"{arg}"' for arg in package.get("args", [])])

        #         result = subprocess.run(
        #             [
        #                 f"{r_path}script",
        #                 "-e",
        #                 f'options(repos = c(CRAN = "https://cran.ism.ac.jp/")); '  # CRANのミラーサイトを東京に設定
        #                 f'{install_function}("{package_name}", version = "{version}", {args})',
        #             ],
        #             stderr=subprocess.PIPE,
        #             check=True,
        #         )
        #         if result.returncode != 0:
        #             # Rパッケージのインストールがエラーを起こした場合、プロセス全体を終了し、エラーの内容を表示
        #             print(f"Error installing {package_name}: {result.stderr.decode()}")
        #             exit(1)

        #         # プログレスバーを更新
        #         pbar.update(1)

        # pbar.close()

        # call parent
        install.run(self)


# pyenv.yamlからPythonパッケージを取得する
with open("pyenv.yaml", "r", encoding="utf-8") as file:
    python_dependencies = yaml.safe_load(file)

install_requires = [
    f"{package['name']}=={package['version']}" for package in python_dependencies
]

setup(
    name="celline",
    version="0.1.4",
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
