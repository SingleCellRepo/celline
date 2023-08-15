from __future__ import annotations
from typing import List, Optional, Any, Dict, TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from celline import Project


class CellineFunction(Protocol):
    """
    Abstract class to extend celline function
    """

    def __init__(self, **args) -> None:
        super().__init__()

    def register(self) -> str:
        """
        [Abstract] Register method
        return "method name for command"
        """
        return "None"

    def call(self, project: Project):
        """
        [Abstract] On call method.
        args["req_<number>"]: get required argument
        args["options"]: get optional arguments
        args["options"]["<arg_name>"]: get optional argument with <arg_name>
        """
