from typing import TYPE_CHECKING, Callable, Optional, NamedTuple, Final
import os
import datetime

import rich

from celline.functions._base import CellineFunction
from celline.DB.dev.model import SampleSchema
from celline.DB.dev.handler import HandleResolver
from celline.sample import SampleResolver, SampleInfo
from celline.template import TemplateManager
from celline.server import ServerSystem
from celline.config import Setting, Config
from celline.middleware import ThreadObservable

if TYPE_CHECKING:
    from celline import Project


class Integrate(CellineFunction):
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
        all_data_sample_dir_path: str
        out_file_name: str
        logpath_runtime: str
        project_name: str

    def __init__(
        self,
        filter_func: Optional[Callable[[SampleSchema], bool]],
        outfile_name: Optional[str],
    ) -> None:
        self.filter_func = filter_func
        self.cluster_server: Final[Optional[str]] = ServerSystem.cluster_server_name
        if outfile_name is None:
            self.outfile_name: Final[str] = f"integrated_{datetime.datetime.now()}"
        else:
            self.outfile_name = outfile_name

    def register(self) -> str:
        return "integrate"

    def call(self, project: "Project"):
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        target_samples: list[SampleInfo] = []
        for info in SampleResolver.samples.values():
            if info.path.is_counted and info.path.is_doublet_predicted:
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
        os.makedirs(f"{Config.PROJ_ROOT}/integration", exist_ok=True)
        os.makedirs(f"{Config.PROJ_ROOT}/integration/logs", exist_ok=True)
        TemplateManager.replace_from_file(
            file_name="integrate.sh",
            structure=Integrate.JobContainer(
                nthread=str(1),
                cluster_server=""
                if self.cluster_server is None
                else self.cluster_server,
                jobname="Integration",
                logpath=f"{Config.PROJ_ROOT}/integration/logs/integrate_{now}.log",
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
                out_file_name=self.outfile_name,
                logpath_runtime=f"{Config.PROJ_ROOT}/integration/logs/RUNTIME_integrate_{now}.log",
                project_name=f"{Setting.name}",
            ),
            replaced_path=f"{Config.PROJ_ROOT}/integration/integrate_{now}.sh",
        )
        ThreadObservable.call_shell(
            [f"{Config.PROJ_ROOT}/integration/integrate_{now}.sh"]
        ).watch()
        return project
