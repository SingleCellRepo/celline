import os
from typing import TYPE_CHECKING, Dict, Final, List, NamedTuple, Optional, Union

import polars as pl
import toml
import tqdm

from celline.config import Config
from celline.DB.handler import GEOHandler
from celline.DB.model import GSE, GSM, SRR
from celline.functions._base import CellineFunction
from celline.utils.serialization import NamedTupleAndPolarsStructure

if TYPE_CHECKING:
    from celline import Project


class Add(CellineFunction):
    """
    Add accession ID to your project.
    """

    class SampleInfo(NamedTuple):
        id_name: str
        title: Optional[str] = ""

    add_target_id: Final[List[SampleInfo]]

    def __init__(self, sample_id: Union[List[SampleInfo], pl.DataFrame]) -> None:
        """
        #### Add accession ID to DB & your project.

        #### Note: Parallel calculations are not supported

        Args:
            sample_id (<List[Add.SampleInfo]> | <pl.DataFrame>): Accession ID to add.
        """
        if isinstance(sample_id, pl.DataFrame):
            cols = sample_id.get_columns()
            if [col.name for col in cols] != ["id_name", "title"]:
                raise KeyError(
                    "The given DataFrame must consist of an id_name column and a title column."
                )
            sample_id = NamedTupleAndPolarsStructure[Add.SampleInfo].deserialize(
                sample_id, Add.SampleInfo
            )
        self.add_target_id = sample_id

    def get_samples(self) -> Dict[str, str]:
        """
        Get sample information from samples.toml file.

        Returns:
            Dict[str, str]: Samples information.
        """
        sample_info_file = f"{Config.PROJ_ROOT}/samples.toml"
        samples: Dict[str, str] = {}
        if os.path.isfile(sample_info_file):
            with open(sample_info_file, mode="r", encoding="utf-8") as f:
                samples = toml.load(f)
        return samples

    def __add_gsm_accession_proj(self, sample_id: str, sample_name: str) -> None:
        """
        Add GSM accession ID and sample name to the samples.toml file.

        Args:
            sample_id (str): GSM accession ID.
            sample_name (str): Sample name.
        """
        sample_info_file = f"{Config.PROJ_ROOT}/samples.toml"
        samples: Dict[str, str] = {}
        if os.path.isfile(sample_info_file):
            with open(sample_info_file, mode="r", encoding="utf-8") as f:
                samples = toml.load(f)
        if sample_id in samples:
            return
        samples[sample_id] = sample_name
        with open(sample_info_file, mode="w", encoding="utf-8") as f:
            toml.dump(samples, f)

    def call(self, project: "Project") -> "Project":
        """
        Call the function to add accession IDs to the project.

        Args:
            project (<Project>): The project to add the accession IDs to.

        Returns:
            <Project>: The project with the added accession IDs.
        """
        cnt = 0
        for sample in tqdm.tqdm(self.add_target_id):
            if sample.id_name.startswith("GSE"):
                gse_schema = GSE().search(sample.id_name)
                for gsm_id in tqdm.tqdm(
                    gse_schema.child_gsm_ids.split(","), leave=False
                ):
                    gsm_schema = GSM().search(gsm_id)
                    given_title = self.add_target_id[cnt].title
                    sample_name = (
                        gsm_schema.title
                        if (given_title is None or given_title == "")
                        else given_title
                    )
                    self.__add_gsm_accession_proj(
                        sample_id=gsm_schema.accession_id, sample_name=sample_name
                    )
            elif sample.id_name.startswith("GSM"):
                gsm_schema = GSM().search(sample.id_name)
                given_title = self.add_target_id[cnt].title
                sample_name = (
                    gsm_schema.title
                    if (given_title is None or given_title == "")
                    else given_title
                )
                self.__add_gsm_accession_proj(
                    sample_id=gsm_schema.accession_id, sample_name=sample_name
                )
            else:
                raise KeyError("Please set GSE or GSM")
            cnt += 1
        samples = self.get_samples()
        cnt = 1
        for sample in samples:
            print(f"Migrating {sample}: ({cnt}/{len(samples)})")
            GEOHandler.sync(sample, log=True)
            cnt += 1
        return project