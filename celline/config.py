import os
from typing import Any, Dict, Optional
import toml
import subprocess
import inquirer


class Config:
    EXEC_ROOT: str
    PROJ_ROOT: str

    @staticmethod
    def initialize(exec_root_path: str, proj_root_path: Optional[str]):
        Config.EXEC_ROOT = exec_root_path
        Config.PROJ_ROOT = proj_root_path
        if proj_root_path is None:
            return
        if not os.path.isfile(f"{proj_root_path}/setting.toml"):
            Setting.create_new()


class Setting:
    # model variables
    name: str
    version: float
    wait_time: int
    r_path: str = ""

    @staticmethod
    def validate():
        if not os.path.isfile(f"{Config.PROJ_ROOT}/setting.toml"):
            raise FileNotFoundError("Could not find setting file in your project.")

    @staticmethod
    def as_dict():
        return {
            "project": {"name": Setting.name, "version": Setting.version},
            "fetch": {"wait_time": Setting.wait_time},
            "R": {"r_path": Setting.r_path},
        }

    @staticmethod
    def as_cfg_obj(dict: Dict[str, Any]):
        Setting.name = dict["project"]["name"]
        Setting.version = dict["project"]["version"]
        Setting.wait_time = dict["fetch"]["wait_time"]
        Setting.r_path = dict["R"]["r_path"]

    @staticmethod
    def initialize():
        Setting.validate()
        with open(f"{Config.PROJ_ROOT}/setting.toml", mode="r") as f:
            Setting.as_cfg_obj(toml.load(f))

    @staticmethod
    def create_new():
        proc = subprocess.Popen("which R", stdout=subprocess.PIPE, shell=True)
        result = proc.communicate()
        default_r = result[0].decode("utf-8").replace("\n", "")
        questions = [
            inquirer.Text(name="projname", message="What is a name of your project?"),
            inquirer.Path(name="rpath", message="Where is R?", default=default_r),
        ]
        result = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        if result is None:
            quit()
        Setting.name = result["projname"]
        Setting.r_path = result["rpath"]
        Setting.version = 0.01
        Setting.wait_time = 4
        Setting.flush()
        print("Completed.")

    @staticmethod
    def flush():
        with open(f"{Config.PROJ_ROOT}/setting.toml", mode="w") as f:
            toml.dump(Setting.as_dict(), f)
