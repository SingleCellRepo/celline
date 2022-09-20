import os
import shutil
from typing import List

import pandas as pd  # type:ignore

from celline.utils.config import Config


class Directory:

    @staticmethod
    def runs():
        if not os.path.isfile(f"{Config.PROJ_ROOT}/runs.tsv"):
            raise FileNotFoundError(
                f"Could not found run.tsv in your project: {Config.PROJ_ROOT}.")
        return pd.read_csv(f"{Config.PROJ_ROOT}/runs.tsv", sep="\t")

    @staticmethod
    def initialize():
        """
        Initialize directory structure
        """
        runs = Directory.runs()
        gses = runs["gse_id"].drop_duplicates().tolist()
        for gse in gses:
            parent = f"{Config.PROJ_ROOT}/resources/{gse}"
            os.makedirs(parent, exist_ok=True)
            gsms: List[str] = runs[runs["gse_id"] ==
                                   gse]["gsm_id"].drop_duplicates().tolist()
            os.makedirs(f"{parent}/0_dumped", exist_ok=True)
            for gsm in gsms:
                os.makedirs(f"{parent}/0_dumped/{gsm}", exist_ok=True)
                os.makedirs(f"{parent}/0_dumped/{gsm}/fastqs", exist_ok=True)
                for targetdir in runs["dumped_filepath"].tolist():
                    os.makedirs(
                        f'{Config.PROJ_ROOT}/resources/{"/".join(targetdir.split("/")[0:-1])}', exist_ok=True)
                os.makedirs(f"{parent}/0_dumped/{gsm}/bam", exist_ok=True)
            os.makedirs(f"{parent}/1_count", exist_ok=True)
            os.makedirs(f"{parent}/2_seurat", exist_ok=True)
            os.makedirs(f"{parent}/2_seurat/__integrated", exist_ok=True)
            for gsm in gsms:
                os.makedirs(f"{parent}/2_seurat/{gsm}", exist_ok=True)
        os.makedirs(f"{Config.PROJ_ROOT}/jobs/logs", exist_ok=True)
        os.makedirs(f"{Config.PROJ_ROOT}/jobs/auto/0_dump", exist_ok=True)
        os.makedirs(f"{Config.PROJ_ROOT}/jobs/auto/1_count", exist_ok=True)
        os.makedirs(f"{Config.PROJ_ROOT}/jobs/auto/2_seurat", exist_ok=True)

    @staticmethod
    def clean():
        runs = Directory.runs()
        gses = runs["gse_id"].drop_duplicates().tolist()
        for gse in gses:
            shutil.rmtree(f"{Config.PROJ_ROOT}/{gse}", ignore_errors=True)
