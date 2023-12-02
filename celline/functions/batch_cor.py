from dataclasses import dataclass
import datetime
import os
import sys
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Final,
    List,
    NamedTuple,
    Optional,
    Union,
)

import polars as pl
import rich
from rich.progress import track
import toml
import tqdm

from celline.DB.dev.handler import HandleResolver
from celline.DB.dev.model import SampleSchema
from celline.config import Config, Setting
from celline.functions._base import CellineFunction
from celline.middleware import ThreadObservable
from celline.sample import SampleInfo, SampleResolver
from celline.server import ServerSystem
from celline.template import TemplateManager
from celline.utils.serialization import NamedTupleAndPolarsStructure

if TYPE_CHECKING:
    from celline import Project


class BatchCorrection(CellineFunction):
    """
    Correction batch effect
    """

    def __init__(
        self,
        output_file_path: str,
        scgen_python_executable_path: str,
        filter_func: Optional[Callable[[SampleSchema], bool]],
    ) -> None:
        """
        #### Add accession ID to DB & your project.

        #### Note: Parallel calculations are not supported

        Args:
            h5ad_path (<List[Add.SampleInfo]> | <pl.DataFrame>): Accession ID to add.
        """
        self.filter_func = filter_func
        self.output_file_path = output_file_path
        self.scgen_python_executable_path = scgen_python_executable_path
        self.cluster_server: Final[Optional[str]] = ServerSystem.cluster_server_name

    def register(self) -> str:
        return "batch"

    def call(self, project: "Project") -> "Project":
        """
        Call the function to add accession IDs to the project.

        Args:
            project (<Project>): The project to add the accession IDs to.

        Returns:
            <Project>: The project with the added accession IDs.
        """
        # STEP0: Data collection
        target_samples: list[SampleInfo] = []
        for info in SampleResolver.samples.values():
            if info.path.is_counted:
                if self.filter_func is None:
                    add = True
                else:
                    add = self.filter_func(info.schema)
                if add:
                    target_samples.append(info)
            else:
                rich.print(
                    f":warning: [bold yellow]Warning[/] Target sample {info.schema.key} is not counted or preprocessed yet."
                )
        os.makedirs(f"{Config.PROJ_ROOT}/batch", exist_ok=True)
        os.makedirs(f"{Config.PROJ_ROOT}/batch/logs", exist_ok=True)
        # STEP1: Pure integrate
        self.__pure_merge(target_samples)
        # STEP2: Convert rds to h5ad
        self.__convert(project)
        # STEP3: Correct batch effect
        self.__correct_batch_effect()
        # STEP4: Convert to rds (seurat object)

        return project

    def __pure_merge(self, target_samples: list[SampleInfo]):
        class JobContainer(NamedTuple):
            nthread: str
            cluster_server: str
            jobname: str
            logpath: str
            r_path: str
            exec_root: str
            sample_ids: str
            project_ids: str
            all_bcmat_path: str
            outfile_path: str
            logpath_runtime: str
            project_name: str
            all_data_sample_dir_path: str

        NOW: Final[str] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        TemplateManager.replace_from_file(
            file_name="pure_merge.sh",
            structure=JobContainer(
                nthread=str(1),
                cluster_server=""
                if self.cluster_server is None
                else self.cluster_server,
                jobname="PureMerge_STEP1",
                logpath=f"{Config.PROJ_ROOT}/batch/logs/1_puremerge_{NOW}.log",
                r_path=f"{Setting.r_path}script",
                exec_root=Config.EXEC_ROOT,
                sample_ids=",".join(
                    [str(sample.schema.key) for sample in target_samples]
                ),
                project_ids=",".join(
                    [
                        sample.schema.parent if sample.schema.parent is not None else ""
                        for sample in target_samples
                    ]
                ),
                all_bcmat_path=",".join(
                    [
                        f"{sample.path.resources_sample_counted}/outs/filtered_feature_bc_matrix.h5"
                        for sample in target_samples
                    ]
                ),
                all_data_sample_dir_path=",".join(
                    [f"{sample.path.data_sample}" for sample in target_samples]
                ),
                outfile_path=f"{Config.PROJ_ROOT}/batch/STEP1_merged",
                logpath_runtime=f"{Config.PROJ_ROOT}/batch/logs/RUNTIME_1_puremerge_{NOW}.log",
                project_name=f"{Setting.name}",
            ),
            replaced_path=f"{Config.PROJ_ROOT}/batch/1_puremerge_{NOW}.sh",
        )

        ThreadObservable.call_shell(
            [f"{Config.PROJ_ROOT}/batch/1_puremerge_{NOW}.sh"]
        ).watch()

    def __convert(self, project: "Project"):
        merged_path = f"{Config.PROJ_ROOT}/batch/STEP1_merged.rds"
        merged_path_h5ad = f"{Config.PROJ_ROOT}/batch/STEP2_merged.h5ad"
        project.seurat_from_rawpath(merged_path, via_seurat_disk=False).save_h5ad(
            merged_path_h5ad
        )

    def __correct_batch_effect(self):
        class JobContainer(NamedTuple):
            nthread: str
            cluster_server: str
            logpath: str
            py_path: str
            exec_root: str
            h5ad_path: str
            output_dir: str

        NOW: Final[str] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        TemplateManager.replace_from_file(
            file_name="batch_cor.sh",
            structure=JobContainer(
                nthread=str(1),
                cluster_server=""
                if self.cluster_server is None
                else self.cluster_server,
                logpath=f"{Config.PROJ_ROOT}/batch/logs/integrate_{NOW}.log",
                py_path=self.scgen_python_executable_path,
                exec_root=Config.EXEC_ROOT,
                h5ad_path=f"{Config.PROJ_ROOT}/batch/STEP2_merged.h5ad",
                output_dir=self.output_file_path,
            ),
            replaced_path=f"{Config.PROJ_ROOT}/batch/3_removebatch_{NOW}.sh",
        )
        ThreadObservable.call_shell(
            [f"{Config.PROJ_ROOT}/batch/3_removebatch_{NOW}.sh"]
        ).watch()
