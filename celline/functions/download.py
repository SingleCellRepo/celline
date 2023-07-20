from enum import Enum
import os
import subprocess
import datetime
from typing import Dict, Optional, TYPE_CHECKING, NamedTuple, Callable

import polars as pl
import toml
from pprint import pprint

from celline.functions._base import CellineFunction
from celline.DB.model import GSM, GSE, SRR
from celline.config import Config
from celline.utils.path import Path
from celline.template import TemplateManager
from celline.middleware.shell import Shell

if TYPE_CHECKING:
    from celline import Project


class Download(CellineFunction):
    """
    Download data into your project.
    """

    class Mode(Enum):
        Bash = 1
        Nohup = 2
        PBS = 3

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
        job_mode: Mode = Mode.PBS,
        then: Optional[Callable[[str], None]] = None,
        catch: Optional[Callable[[subprocess.CalledProcessError], None]] = None,
        cluster_server: Optional[str] = None,
    ) -> None:
        """
        Initialize the Download function with job mode and thread count.
        """
        if job_mode == Download.Mode.PBS and cluster_server is None:
            raise SyntaxError(
                "If you use PBS system, please define the cluster server."
            )
        self.job_mode = job_mode
        self.cluster_server = cluster_server
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
            for sample in samples:
                gsm_schema = GSM().search(sample)
                srr_schema = SRR().search(gsm_schema.child_srr_ids.split(",")[0])
                filetype = srr_schema.strategy
                path = Path(gsm_schema.parent_gse_id, sample)
                path.prepare()
                TemplateManager.replace_from_file(
                    file_path=f"{Config.EXEC_ROOT}/templates/download.sh",
                    structure=Download.JobContainer(
                        filetype=filetype,
                        nthread=str(self.nthread),
                        cluster_server=""
                        if self.cluster_server is None
                        else self.cluster_server,
                        jobname="Download",
                        logpath=f"{path.resources_sample_log}/download_{datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S')}.log",
                        sample_id=sample,
                        download_target=path.resources_sample_raw,
                        download_source=srr_schema.raw_link,
                        run_ids_str=gsm_schema.child_srr_ids,
                    ),
                    replaced_path=f"{path.resources_sample_src}/download.sh",
                )
                shell = Shell()  # Prepare shell
                if self.job_mode == Download.Mode.PBS:
                    (
                        shell.execute(f"qsub {path.resources_sample_src}/download.sh")
                        .then(self.then)
                        .catch(self.catch)
                    )
                elif self.job_mode == Download.Mode.Bash:
                    (
                        shell.execute(f"bash {path.resources_sample_src}/download.sh")
                        .then(self.then)
                        .catch(self.catch)
                    )
                elif self.job_mode == Download.Mode.Nohup:
                    (
                        shell.execute(
                            f"nohup bash {path.resources_sample_src}/download.sh > {path.resources_sample_log}.runtime.log"
                        )
                        .then(self.then)
                        .catch(self.catch)
                    )
        return project
