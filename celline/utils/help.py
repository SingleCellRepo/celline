import sys
from typing import Any, Dict

import yaml
from yaml import Dumper, Loader


class Help:
    """
    Support help program
    """

    __HELP_PATH = f"{sys.path[0]}/docs/__help.yaml"

    def __init__(self) -> None:
        with open(Help.__HELP_PATH, mode="r") as f:
            self.contents: Dict[str, Dict[str, Any]
                                ] = yaml.load(f, Loader=Loader)
        pass

    def __build(self, command: str) -> str:
        target = self.contents[command]
        cmd = f"""
celline {command}\n  """
        args = target["args"]
        for arg in args:
            if args[arg]["optional"]:
                cmd += f"--{arg}"
            else:
                cmd += f"{arg}"
            cmd += f"\n    : {args[arg]['description']}"
        return cmd

    def call(self, command: str):
        if command not in self.contents:
            return "\n".join([self.__build(cmd) for cmd in self.contents.keys()])
        else:
            return self.__build(command)
