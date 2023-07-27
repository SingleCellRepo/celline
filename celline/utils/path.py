import os
import shutil
from celline.config import Config
from typing import Final
import datetime
import glob


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
        return f"{self.resources_sample}/counted"

    @property
    def resources_sample_raw(self):
        return f"{self.resources_sample}/raw"

    @property
    def resources_sample_raw_fastqs(self):
        return f"{self.resources_sample_raw}/fastqs"

    @property
    def resources_sample_log(self):
        return f"{self.resources_sample}/logs"

    def resources_log_file(self, prefix: str):
        return f"{self.resources_sample_log}/{prefix}_{datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S')}.log"

    @property
    def data_sample(self):
        return f"{self.data}/{self.project_id}/{self.sample_id}"

    @property
    def data_sample_log(self):
        return f"{self.data}/{self.project_id}/{self.sample_id}/logs"

    @property
    def data_sample_src(self):
        return f"{self.data}/{self.project_id}/{self.sample_id}/src"

    def data_log_file(self, prefix: str):
        return f"{self.data_sample_log}/{prefix}_{datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S')}.log"

    @property
    def is_downloaded(self):
        patterns = [
            f"{self.sample_id}_S1_L00*_{suffix}_001.fastq.gz"
            for suffix in ["R1", "R2", "I1", "I2"]
        ]
        total_files = 0
        for pattern in patterns:
            files = glob.glob(os.path.join(self.resources_sample_raw_fastqs, pattern))
            total_files += len(files)

        if 2 <= total_files <= 4:
            return True
        return False

    def prepare(self):
        if not os.path.isdir(self.resources_sample_raw):
            os.makedirs(self.resources_sample_raw, exist_ok=True)
        if not self.is_downloaded:
            shutil.rmtree(self.resources_sample_raw_fastqs, ignore_errors=True)
        if not os.path.isdir(self.resources_sample_log):
            os.makedirs(self.resources_sample_log, exist_ok=True)
        if not os.path.isdir(self.resources_sample_src):
            os.makedirs(self.resources_sample_src, exist_ok=True)
        if not os.path.isdir(self.data_sample_log):
            os.makedirs(self.data_sample_log, exist_ok=True)
        if not os.path.isdir(self.data_sample_src):
            os.makedirs(self.data_sample_src, exist_ok=True)
