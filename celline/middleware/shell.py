from __future__ import annotations
from typing import Callable, Optional, Final
import subprocess
import os


class Shell:
    resonse: Optional[str] = None
    exception: Optional[subprocess.CalledProcessError] = None
    DEFAULT_SHELL: Final[Optional[str]] = os.environ.get("SHELL")

    @staticmethod
    def execute(bash_command: str):
        shell = Shell()
        if Shell.DEFAULT_SHELL is None:
            return shell
        rc_file = ""
        if "bash" in Shell.DEFAULT_SHELL:
            rc_file = "~/.bashrc"
        elif "zsh" in Shell.DEFAULT_SHELL:
            rc_file = "~/.zshrc"

        try:
            result = subprocess.run(
                f"source {rc_file} && {bash_command}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                executable=Shell.DEFAULT_SHELL,
                check=True,
            )
            shell.resonse = result.stdout.decode()
        except subprocess.CalledProcessError as e:
            shell.exception = e
        return shell

    def then(self, callbackfn: Callable[[str], None]):
        if self.resonse is not None:
            callbackfn(self.resonse)
        return self

    def catch(self, callbackfn: Callable[[subprocess.CalledProcessError], None]):
        if self.exception is not None:
            callbackfn(self.exception)
