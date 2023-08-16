from typing import TYPE_CHECKING, Final, NamedTuple, Optional, List
from celline.functions._base import CellineFunction
from celline.template import TemplateManager
from celline.server import ServerSystem
from celline.sample import SampleResolver
from celline.DB.dev.handler import HandleResolver
from celline.DB.dev.model import SampleSchema
from celline.config import Config
from celline.middleware import ThreadObservable
from celline.utils.path import Path
from celline.config import Setting
from dataclasses import dataclass
import pandas as pd
import polars as pl
import rich
from rich.table import Table
from rich.console import Console
import os
import shutil
import sys

if TYPE_CHECKING:
    from celline import Project


@dataclass
class CellTypeModel:
    species: str
    suffix: Optional[str]


class BuildCellTypeModel(CellineFunction):
    """### Build cell type prediction model"""

    class JobContainer(NamedTuple):
        """
        Represents job information for data download.
        """

        nthread: str
        cluster_server: str
        jobname: str
        logpath: str
        h5matrix_path: str
        celltype_path: str
        dist_dir: str
        r_path: str
        exec_root: str

    def __init__(
        self,
        species: str,
        suffix: str,
        nthread: int,
        h5matrix_path: str,
        celltype_path: str,
    ) -> None:
        if not celltype_path.endswith(".tsv"):
            rich.print(
                "[bold red]Build Error[/] celltype_path should be .tsv file path."
            )
            self.__show_help()
            sys.exit(1)
        _df = pl.read_csv(celltype_path, separator="\t")
        if _df.columns != ["cell", "celltype"]:
            rich.print(
                "[bold red]Build Error[/] celltype dataframe should be composed of cell, celltype column."
            )
            self.__show_help()
            sys.exit(1)
        if (
            not h5matrix_path.endswith(".h5")
            or not h5matrix_path.endswith(".loom")
            or not h5matrix_path.endswith(".h5seurat")
            or not h5matrix_path.endswith(".h5seuratv5")
        ):
            rich.print(
                "[bold red]Build Error[/] h5matrix_path should be .h5, h5seurat, h5seuratv5 or .loom file path."
            )
        self.model: Final[CellTypeModel] = CellTypeModel(species, suffix)
        self.nthread: Final[int] = nthread
        self.cluster_server: Final[Optional[str]] = ServerSystem.cluster_server_name
        self.h5matrix_path: Final[str] = h5matrix_path
        self.celltype_path: Final[str] = celltype_path

    def __show_help(self):
        df = pd.DataFrame(
            {
                "cell": [
                    "10X82_2_TCTCTCACCAGTTA",
                    "10X82_2_TCTCTCACCAGTTC",
                    "10X82_2_TCTCTCACCAGTTT",
                ],
                "celltype": ["Astrocyte", "Oligodendrocyte", "Neuron"],
            }
        )
        table = Table(show_header=True, header_style="bold magenta")
        console = Console()
        for column in df.columns:
            table.add_column(column)
        for _, row in df.iterrows():
            table.add_row(*row.astype(str).tolist())
        rich.print(
            """
[bold green]:robot: How to use?[/]

* [bold]h5matrix_path<str>[/]: h5 matrix path. This data should be h5 matrix which be output from Cellranger.
* [bold]celltype_path<str>[/]: cell type path. This dataframe should be tsv format which have following dataframe structure."""
        )
        console.print(table)

    def call(self, project: "Project"):
        dist_dir = f"{Config.PROJ_ROOT}/reference/{self.model.species}/{self.model.suffix if self.model.suffix is not None else 'default'}"
        if (
            os.path.isdir(dist_dir)
            and not os.path.isfile(f"{dist_dir}/reference.pred")
            and not os.path.isfile(f"{dist_dir}/reference.h5seurat")
        ):
            shutil.rmtree(dist_dir)
        os.makedirs(dist_dir, exist_ok=True)
        TemplateManager.replace_from_file(
            file_name="build_reference.sh",
            structure=BuildCellTypeModel.JobContainer(
                nthread=str(self.nthread),
                cluster_server=""
                if self.cluster_server is None
                else self.cluster_server,
                jobname="BuildCelltypeModel",
                logpath=f"{dist_dir}/build.log",
                h5matrix_path=self.h5matrix_path,
                dist_dir=dist_dir,
                celltype_path=self.celltype_path,
                r_path=f"{Setting.r_path}script",
                exec_root=Config.EXEC_ROOT,
            ),
            replaced_path=f"{dist_dir}/build.sh",
        )
        ThreadObservable.call_shell([f"{dist_dir}/build.sh"]).watch()
        return project


class PredictCelltype(CellineFunction):
    class JobContainer(NamedTuple):
        """
        Represents job information for data download.
        """

        nthread: str
        cluster_server: str
        jobname: str
        logpath: str
        all_sample_path: str
        refh5: str
        refpred: str
        dist_dir: str

    def __init__(self, model: CellTypeModel) -> None:
        self.model = model
        self.cluster_server: Final[Optional[str]] = ServerSystem.cluster_server_name

    def register(self) -> str:
        return "predict_celltype"

    def call(self, project: "Project"):
        def __build_path(sample_id: str):
            resolver = HandleResolver.resolve(sample_id)
            if resolver is None:
                raise ReferenceError(f"Could not resolve target sample id: {sample_id}")
            sample_schema: SampleSchema = resolver.sample.search(sample_id)
            if sample_schema.parent is None:
                raise KeyError("Could not find parent")
            return f"{Path(sample_schema.parent, sample_id).data_sample}/"

        __dist_dir = f"{Config.PROJ_ROOT}/reference/{self.model.species}/{self.model.suffix if self.model.suffix is not None else 'default'}"
        refh5 = f"{__dist_dir}/reference.h5seurat"
        refpred = f"{__dist_dir}/reference.pred"
        all_sample_ids = ",".join(SampleResolver.samples.keys())
        all_dist_dir = ",".join(
            [__build_path(sample_id) for sample_id in SampleResolver.samples.keys()]
        )
        TemplateManager.replace_from_file(
            file_name="build_reference.sh",
            structure=PredictCelltype.JobContainer(
                nthread=str(1),
                cluster_server=""
                if self.cluster_server is None
                else self.cluster_server,
                jobname="PredictCelltype",
                logpath=f"{Config.PROJ_ROOT}/reference/prediction.log",
                all_sample_path=all_sample_ids,
                refh5=refh5,
                refpred=refpred,
                dist_dir=all_dist_dir,
            ),
            replaced_path=f"{Config.PROJ_ROOT}/reference/prediction.sh",
        )
        ThreadObservable.call_shell(
            [f"{Config.PROJ_ROOT}/reference/prediction.sh"]
        ).watch()
        return project
