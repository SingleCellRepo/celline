import os
from typing import Any, Dict
import toml


class Config:
    EXEC_ROOT: str
    PROJ_ROOT: str

    @staticmethod
    def initialize(exec_root_path: str, proj_root_path: str):
        if not os.path.isfile(f"{proj_root_path}/setting.toml"):
            raise FileNotFoundError(
                "Could not find setting.toml. Please create or initialize your project.")
        Config.EXEC_ROOT = exec_root_path
        Config.PROJ_ROOT = proj_root_path


class Setting:
    FILE_PATH = f"{Config.PROJ_ROOT}/setting.toml"
    # model variables
    name: str
    version: float
    wait_time: int

    @staticmethod
    def validate():
        if not os.path.isfile(Setting.FILE_PATH):
            raise FileNotFoundError(
                "Could not find setting file in your project.")

    @staticmethod
    def as_dict():
        return {
            "project": {
                "name": Setting.name,
                "version": Setting.version
            },
            "fetch": {
                "wait_time": Setting.wait_time
            }
        }

    @staticmethod
    def as_cfg_obj(dict: Dict[str, Any]):
        Setting.name = dict["project"]["name"]
        Setting.version = dict["project"]["version"]
        Setting.wait_time = dict["fetch"]["wait_time"]

    @staticmethod
    def read():
        Setting.validate()
        with open(Setting.FILE_PATH, mode="r") as f:
            Setting.as_cfg_obj(toml.load(f))

    @staticmethod
    def write():
        Setting.validate()
        with open(Setting.FILE_PATH, mode="w") as f:
            toml.dump(Setting.as_dict(), f)
