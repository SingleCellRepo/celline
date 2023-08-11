from enum import Enum
import os
import subprocess
import datetime
import shutil

from typing import Dict, Optional, TYPE_CHECKING, NamedTuple, Callable, List

import polars as pl
import toml
from pprint import pprint

from celline.functions._base import CellineFunction
from celline.DB.model import SRA_GSM, SRA_GSE, SRA_SRR
from celline.DB.dev.handler import HandleResolver
from celline.config import Config
from celline.utils.path import Path
from celline.template import TemplateManager
from celline.middleware import ThreadObservable
from celline.server import ServerSystem
from celline.sample import SampleResolver
from celline.DB.dev.model import BaseModel, BaseSchema
if TYPE_CHECKING:
    from celline import Project


class Download(CellineFunction):
    """
    #### Download data into your project.
    """

    class JobContainer(NamedTuple):
        """
        Represents job information for data download.
        """

        filetype: str
        nthread: str
        cluster_server: str
        jobname: str
        logpath: str
        sample_id: str
        download_target: str
        download_source: str
        run_ids_str: str

    def __init__(
        self,
        then: Optional[Callable[[str], None]] = None,
        catch: Optional[Callable[[subprocess.CalledProcessError], None]] = None,
    ) -> None:
        """
        #### Setup download job function with job mode and thread count.
        """
        self.nthread = 1
        self.then = then if then is not None else lambda _: None
        self.catch = catch if catch is not None else lambda _: None

    def call(self, project: "Project"):
        """
        Call the Download function to download data into the project.
        """
        all_job_files: List[str] = []
        for sample_id in SampleResolver.samples:
            resolver = HandleResolver.resolve(sample_id)
            if resolver is None:
                raise ReferenceError(f"Could not resolve target sample id: {sample_id}")
            sample_schema: BaseSchema = resolver.sample.search(sample_id)
            if sample_schema.children is None:
                raise NotImplementedError("Children could not found")
            run_schema: BaseSchema = resolver.run.search(sample_schema.children.split(",")[0])
            filetype = run_schema.strategy
            path = Path(gsm_schema.parent_gse_id, sample)
            path.prepare()
            if not path.is_downloaded:
                shutil.rmtree(path.resources_sample_raw_fastqs)
                TemplateManager.replace_from_file(
                    file_name="download.sh",
                    structure=Download.JobContainer(
                        filetype=filetype,
                        nthread=str(self.nthread),
                        cluster_server=""
                        if ServerSystem.cluster_server_name is None
                        else ServerSystem.cluster_server_name,
                        jobname="Download",
                        logpath=f"{path.resources_sample_log}/download_{datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S')}.log",
                        sample_id=sample,
                        download_target=path.resources_sample_raw,
                        download_source=srr_schema.raw_link,
                        run_ids_str=gsm_schema.child_srr_ids,
                    ),
                    replaced_path=f"{path.resources_sample_src}/download.sh",
                )
                all_job_files.append(f"{path.resources_sample_src}/download.sh")
        ThreadObservable.call_shell(all_job_files).watch()
        return project
