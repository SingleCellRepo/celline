from typing import TYPE_CHECKING, Optional, Callable, Final, Dict, List, NamedTuple
import subprocess
import rich

from celline.functions._base import CellineFunction
from celline.resources import Resources
from celline.template import TemplateManager
from celline.server import ServerSystem
from celline.config import Setting, Config
from celline.middleware import ThreadObservable

if TYPE_CHECKING:
    from celline import Project


class CreateSeuratObject(CellineFunction):
    class JobContainer(NamedTuple):
        """
        Represents job information for data download.
        """

        nthread: str
        cluster_server: str
        jobname: str
        logpath: str
        r_path: str
        exec_root: str
        input_h5_path: str
        data_dir_path: str
        proj_name: str
        useqc_matrix: str

    def __init__(
        self,
        useqc_matrix: bool,
        then: Optional[Callable[[str], None]] = None,
        catch: Optional[Callable[[subprocess.CalledProcessError], None]] = None,
    ) -> None:
        self.then: Final = then
        self.catch: Final = catch
        self.cluster_server: Final[Optional[str]] = ServerSystem.cluster_server_name
        self.useqc_matrix = "true" if useqc_matrix else "false"

    def call(self, project: "Project"):
        all_job_files: List[str] = []
        for sample in Resources.all_samples():
            if not (
                sample.counted and sample.celltype_predicted and sample.preprocessed
            ):
                rich.print(
                    f"[bold red]Sample {sample.name} is not counted/predicted or pre-processed yet.[/]: Skip"
                )
            input_h5_path = f"{sample.path.resources_sample_counted}/outs/filtered_feature_bc_matrix.h5"
            data_dir_path = sample.path.data_sample
            TemplateManager.replace_from_file(
                file_name="create_seurat.sh",
                structure=CreateSeuratObject.JobContainer(
                    nthread=str(1),
                    cluster_server=""
                    if self.cluster_server is None
                    else self.cluster_server,
                    jobname="Create Seurat",
                    logpath=sample.path.data_log_file("create_seurat"),
                    r_path=f"{Setting.r_path}script",
                    exec_root=Config.EXEC_ROOT,
                    input_h5_path=input_h5_path,
                    data_dir_path=data_dir_path,
                    proj_name=Setting.name,
                    useqc_matrix=self.useqc_matrix,
                ),
                replaced_path=f"{sample.path.data_sample_src}/create_seurat.sh",
            )
            all_job_files.append(f"{sample.path.data_sample_src}/create_seurat.sh")
        ThreadObservable.call_shell(all_job_files, proc_name="Creating seurat").watch()
        return project
