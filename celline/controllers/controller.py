from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Dict, List


class Controller(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    @property
    def command(self) -> str:
        raise NotImplementedError("The command is not implemented yet.")

    @abstractmethod
    @property
    def request_arguments(self) -> str:
        raise NotImplementedError("The command is not implemented yet.")

    @abstractmethod
    def call(self, args: List[str]) -> None:
        raise NotImplementedError("The controller is not implemented yet.")
