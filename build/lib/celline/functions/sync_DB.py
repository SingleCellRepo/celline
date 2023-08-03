import os

from typing import TYPE_CHECKING, List, Optional, Final

import toml

from celline.config import Config
from celline.functions._base import CellineFunction
from celline.DB.handler import GEOHandler

if TYPE_CHECKING:
    from celline import Project


class SyncDB(CellineFunction):
    def __init__(self, force_update_target: Optional[List[str]] = None) -> None:
        self.update_target = force_update_target

    def call(self, project: "Project"):
        fpath: Final[str] = f"{Config.PROJ_ROOT}/samples.toml"
        if not os.path.isfile(fpath):
            raise FileNotFoundError("sample.toml file was not found.")
        with open(fpath, encoding="utf-8", mode="r") as f:
            all_samples = list(toml.load(f).keys())
        for sample in all_samples:
            force_search = False
            if self.update_target is not None and sample in self.update_target:
                force_search = True
            GEOHandler.sync(sample, force_search)
        return self
