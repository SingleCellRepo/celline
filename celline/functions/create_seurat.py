from typing import TYPE_CHECKING

from celline.functions._base import CellineFunction

if TYPE_CHECKING:
    from celline import Project


class CreateSeuratObject(CellineFunction):
    def call(self, project: "Project"):
        return super().call(project)
