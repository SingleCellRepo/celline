from enum import Enum
import os
import subprocess
import datetime
from typing import Dict, Optional, TYPE_CHECKING, NamedTuple, Callable, List

import polars as pl
import toml
from pprint import pprint

from celline.functions._base import CellineFunction
from celline.DB.model import GSM, GSE, SRR
from celline.config import Config
from celline.utils.path import Path
from celline.template import TemplateManager
from celline.middleware import ThreadObservable
from celline.server import ServerSystem

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
        sample_info_file = f"{Config.PROJ_ROOT}/samples.toml"
        if not os.path.isfile(sample_info_file):
            print("sample.toml could not be found. Skipping.")
            return project
        with open(sample_info_file, mode="r", encoding="utf-8") as f:
            samples: Dict[str, str] = toml.load(f)
            all_job_files: List[str] = []
            for sample in samples:
                gsm_schema = GSM().search(sample)
                srr_schema = SRR().search(gsm_schema.child_srr_ids.split(",")[0])
                filetype = srr_schema.strategy
                path = Path(gsm_schema.parent_gse_id, sample)
                path.prepare()
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
