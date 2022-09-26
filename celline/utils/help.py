import sys
from typing import Any, Dict

import yaml
from yaml import Dumper, Loader


class Help:
    """
    Support help program
    """

    __HELP_PATH = f"{sys.path[0]}/docs/__help.yaml"
    __HELP_CONTENT: Dict[str, Any] = {}

    @staticmethod
    def __get_help_content() -> Dict[str, Any]:
        with open(Help.__HELP_PATH, mode="r") as f:
            Help.__HELP_CONTENT = yaml.load(f, Loader=Loader)
        return Help.__HELP_CONTENT

    @staticmethod
    def show():
        print(Help.__get_help_content())
