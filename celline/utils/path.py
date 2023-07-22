import os
import shutil
from celline.config import Config
from typing import Final


class Path:
    project_id: Final[str]
    sample_id: Final[str]

    def __init__(self, project_id: str, sample_id: str) -> None:
        self.project_id = project_id
        self.sample_id = sample_id

    @property
    def resources(self):
        return f"{Config.PROJ_ROOT}/resources"

    @property
    def data(self):
        return f"{Config.PROJ_ROOT}/data"

    @property
    def resources_sample(self):
        return f"{self.resources}/{self.project_id}/{self.sample_id}"

    @property
    def resources_sample_src(self):
        return f"{self.resources_sample}/src"

    @property
    def resources_sample_counted(self):
        return f"{self.resources_sample}/conted"

    @property
    def resources_sample_raw(self):
        return f"{self.resources_sample}/raw"

    @property
    def resources_sample_raw_fastqs(self):
        return f"{self.resources_sample_raw}/fastqs"

    @property
    def resources_sample_log(self):
        return f"{self.resources_sample}/logs"

    @property
    def data_sample(self):
        return f"{self.data}/{self.project_id}/{self.sample_id}"

    def prepare(self):
        if not os.path.isdir(self.resources_sample_raw_fastqs):
            os.makedirs(self.resources_sample_raw_fastqs, exist_ok=True)
        if not os.path.isdir(self.resources_sample_log):
            os.makedirs(self.resources_sample_log, exist_ok=True)
        if not os.path.isdir(self.resources_sample_src):
            os.makedirs(self.resources_sample_src, exist_ok=True)
        if not os.path.isdir(self.resources_sample_counted):
            os.makedirs(self.resources_sample_counted, exist_ok=True)