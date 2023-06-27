from celline.functions._base import CellineFunction
from typing import TYPE_CHECKING, Final, Dict, List
from celline.DB import GSE, GSM
from pprint import pprint
import polars as pl

# from celline.database import NCBI, GSE, GSM

if TYPE_CHECKING:
    from celline import Project


class Add(CellineFunction):
    """
    Add accession ID to your project
    """

    add_target_id: Final[Dict[str, List[str]]]

    def __init__(self, **add_target_id: List[str]) -> None:
        """
        ## Description\n
        Add accession ID to DB & your project.\n
        ### ┗ Arguments\n
             @add_target_id<Dict[str, str]>: Accession ID to add.\n
             ┣ Key: "GSE", "GSM", "SRR"\n
             ┗ Value: "GSE000000"
        """
        self.add_target_id = add_target_id

    # def register(self) -> str:
    #     return "add"

    # def add(self, project: "Project", id: str):
    #     print(f"Added to {id}")
    #     return

    def call(self, project: "Project"):
        if "GSE" in self.add_target_id:
            for gse in self.add_target_id["GSE"]:
                if not gse.startswith("GSE"):
                    raise KeyError(f"{gse} is not GSE ID")
                GSE().search(gse)
        if "GSM" in self.add_target_id:
            for gsm in self.add_target_id["GSM"]:
                if not gsm.startswith("GSM"):
                    raise KeyError(f"{gsm} is not GSM ID")
                GSM().search(gsm)
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
