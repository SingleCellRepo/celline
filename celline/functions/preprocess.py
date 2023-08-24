from __future__ import annotations
import sys
import subprocess
import os

from typing import TYPE_CHECKING, NamedTuple, Callable, Optional, Final, List

import scrublet as scr
import scanpy as sc
import polars as pl

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
        # [1st] Prepare doublet
        all_job_files: List[str] = []
        for sample in [
            sample for sample in Resources.all_samples() if not sample.preprocessed
        ]:
            src_file = f"{sample.path.data_sample_src}/preprocess.sh"
            if not (
                os.path.isfile(f"{sample.path.data_sample}/doublet_info.tsv")
                and os.path.isfile(f"{sample.path.data_sample}/qc_matrix.tsv")
            ):
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
                print(src_file)
                all_job_files.append(src_file)
        ThreadObservable.call_shell(all_job_files).watch()
        return project
