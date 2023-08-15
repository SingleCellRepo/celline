from typing import TYPE_CHECKING
from celline.functions._base import CellineFunction

if TYPE_CHECKING:
    from celline import Project

class Integrate(CellineFunction):
    def register(self) -> str:
        return "integrate"

    def call(self, project: "Project"):
        return project
