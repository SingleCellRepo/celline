from __future__ import annotations
import sys
import subprocess
import os

from typing import TYPE_CHECKING, NamedTuple, Callable, Optional, Final, List

import scrublet as scr
import scanpy as sc
import polars as pl
from rich.progress import track
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from celline.config import Config, Setting
from celline.functions._base import CellineFunction
from celline.resources import Resources
from celline.middleware import ThreadObservable, Shell
from celline.template import TemplateManager
from celline.server import ServerSystem

if TYPE_CHECKING:
    from celline import Project


class Preprocess(CellineFunction):
    """
    #### Run preprocess (prediction of multiplet & mitochondrial QC)
    """

    class JobContainer(NamedTuple):
        cluster_server: str
        jobname: str
        logpath: str
        raw_matrix_path: str
        output_doublet_path: str
        output_qc_path: str
        py_path: str
        exec_root: str
        r_path: str
        log_path: str

    def __init__(
        self,
        then: Optional[Callable[[str], None]] = None,
        catch: Optional[Callable[[subprocess.CalledProcessError], None]] = None,
    ) -> None:
        """
        #### Run preprocess (prediction of multiplet & mitochondrial QC)
        """
        self.job_mode: Final[ServerSystem.JobType] = ServerSystem.job_system
        self.then: Final[Optional[Callable[[str], None]]] = then
        self.catch: Final[
            Optional[Callable[[subprocess.CalledProcessError], None]]
        ] = catch
        self.cluster_server: Final[Optional[str]] = ServerSystem.cluster_server_name
        if self.job_mode == ServerSystem.JobType.PBS and self.cluster_server is None:
            raise SyntaxError(
                "If you use PBS job system, please define cluster_server."
            )

    def call(self, project: Project):
        UPPER_PERCENTILE = 97.5
        # [1st] Prepare doublet
        all_job_files: List[str] = []
        for sample in track(
            Resources.all_samples(),
            description="Preparing preprocess files...",
        ):
            src_file = f"{sample.path.data_sample_src}/preprocess.sh"
            if not sample.preprocessed:
                sample.path.prepare()
                TemplateManager.replace_from_file(
                    "preprocess.sh",
                    Preprocess.JobContainer(
                        cluster_server=self.cluster_server
                        if self.cluster_server is not None
                        else "",
                        jobname=f"Preprocess_{sample.sample_id}",
                        logpath=sample.path.data_log_file("preproc"),
                        output_doublet_path=f"{sample.path.data_sample}/doublet_info.tsv",
                        output_qc_path=f"{sample.path.data_sample}/qc_matrix.tsv",
                        raw_matrix_path=f"{sample.path.resources_sample_counted}/outs/filtered_feature_bc_matrix.h5",
                        py_path=sys.executable,
                        exec_root=f"{Config.EXEC_ROOT}/celline",
                        r_path=f"{Setting.r_path}script",
                        log_path=f"{sample.path.data_sample_log}/qc_matrix.R.log",
                    ),
                    replaced_path=src_file,
                )
                all_job_files.append(src_file)
        ThreadObservable.call_shell(all_job_files).watch()
        for sample in track(
            Resources.all_samples(),
            description="Processing estimating doublets...",
        ):
            SAMPLE_PATH = sample.path.data_sample
            if not os.path.isfile(
                f"{SAMPLE_PATH}/doublet_filtered.tsv"
            ) and os.path.isfile(f"{SAMPLE_PATH}/doublet_info.tsv"):
                pldf = pl.read_csv(f"{SAMPLE_PATH}/doublet_info.tsv", separator="\t")
                # doublet_scoreの95%信頼区間を計算
                upper_bound = float(
                    np.percentile(pldf["doublet_score"].to_numpy(), UPPER_PERCENTILE)
                )
                (
                    pldf.with_columns(
                        (pldf["doublet_score"] > upper_bound).alias("is_doublet_95")
                    ).write_csv(f"{SAMPLE_PATH}/doublet_filtered.tsv", separator="\t")
                )
                sns.histplot(pldf["doublet_score"].to_numpy(), kde=True)
                plt.axvline(upper_bound, color="red", linestyle="--")
                plt.xlabel("Doublet Score")
                plt.ylabel("Frequency")
                plt.title("Distribution of Doublet Score")
                plt.savefig(
                    f"{SAMPLE_PATH}/doublet_distribution.png", format="png", dpi=300
                )
                plt.close()
        return project
