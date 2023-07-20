from celline.functions._base import CellineFunction
from typing import TYPE_CHECKING, Final, Dict, List, Optional, NamedTuple, Union
from celline.DB.model import GSE, GSM, SRR
from pprint import pprint
import polars as pl
from celline.config import Config
import os
import toml
from enum import Enum
import tqdm
from celline.utils.serialization import NamedTupleAndPolarsStructure
from celline.DB.handler import GEOHandler

# from celline.database import NCBI, GSE, GSM

if TYPE_CHECKING:
    from celline import Project


class Add(CellineFunction):
    """
    Add accession ID to your project
    """

    class SampleInfo(NamedTuple):
        id_name: str
        title: str = ""

    add_target_id: Final[List[SampleInfo]]

    def __init__(self, sample_id: Union[List[SampleInfo], pl.DataFrame]) -> None:
        """
        ## Description\n
        Add accession ID to DB & your project.\n
        ### ┗ Arguments\n
             @sample_id<List[Add.SampleInfo] | polars.DataFrame>: Accession ID to add.
        """
        if isinstance(sample_id, pl.DataFrame):
            cols = sample_id.get_columns()
            if [col.name for col in cols] != ["id_name", "title"]:
                raise KeyError(
                    "The given Dataframe must consist of an id_name column and a title column."
                )
            sample_id = NamedTupleAndPolarsStructure[Add.SampleInfo].deserialize(
                sample_id, Add.SampleInfo
            )
        self.add_target_id = sample_id

    # def register(self) -> str:
    #     return "add"

    # def add(self, project: "Project", id: str):
    #     print(f"Added to {id}")
    #     return
    def get_samples(self):
        sample_info_file = f"{Config.PROJ_ROOT}/samples.toml"
        # "SampleID", "SampleName"
        samples: Dict[str, str] = {}
        if os.path.isfile(sample_info_file):
            with open(sample_info_file, mode="r", encoding="utf-8") as f:
                samples = toml.load(f)
        return samples

    def __add_gsm_accession_proj(self, sample_id: str, sample_name: str):
        sample_info_file = f"{Config.PROJ_ROOT}/samples.toml"
        # "SampleID", "SampleName"
        samples: Dict[str, str] = {}
        if os.path.isfile(sample_info_file):
            with open(sample_info_file, mode="r", encoding="utf-8") as f:
                samples = toml.load(f)
        if sample_id in samples:
            return
        samples[sample_id] = sample_name
        with open(sample_info_file, mode="w", encoding="utf-8") as f:
            toml.dump(samples, f)
        # if os.path.isfile(sample_info_file)
        return

    def call(self, project: "Project"):
        cnt = 0
        for sample in tqdm.tqdm(self.add_target_id):
            if sample.id_name.startswith("GSE"):
                gse_schema = GSE().search(sample.id_name)
                for gsm_id in tqdm.tqdm(
                    gse_schema.child_gsm_ids.split(","), leave=False
                ):
                    gsm_schema = GSM().search(gsm_id)
                    sample_name = (
                        gsm_schema.title
                        if self.add_target_id[cnt].title == ""
                        else self.add_target_id[cnt].title
                    )
                    self.__add_gsm_accession_proj(
                        sample_id=gsm_schema.accession_id, sample_name=sample_name
                    )
            elif sample.id_name.startswith("GSM"):
                gsm_schema = GSM().search(sample.id_name)
                sample_name = (
                    gsm_schema.title
                    if self.add_target_id[cnt].title == ""
                    else self.add_target_id[cnt].title
                )
                self.__add_gsm_accession_proj(
                    sample_id=gsm_schema.accession_id, sample_name=sample_name
                )
            else:
                raise KeyError("Please set GSE of GSM")
            cnt += 1
        samples = self.get_samples()
        cnt = 1
        for sample in samples:
            print(f"Migrating {sample}: ({cnt}/{len(samples)})")
            GEOHandler.sync(sample, log=True)
            cnt += 1
        return project

    # def on_call(self, args: Dict[str, DictionaryC[str, Optional[str]]]):
    #     options = args["options"]
    #     id = options["req_1"]
    #     if id is not None:
    #         NCBI.add(id)

    #         # result = NCBI.search("GSE")
    #         # if id.startswith("GSE"):
    #         #     gse: GSE = result
    #         #     append_runs(gse.child_gsm_ids, "TEST")
    #         # elif id.startswith("GSM"):
    #         #     gsm: List[GSM] = result
    #         #     append_runs(gse.child_gsm_ids)
    #     return
