# import celline.DB._base import
from enum import Enum, unique
import polars as pl
from typing import Callable, List, Final, NamedTuple, Type, TypeVar
from celline.DB.dev.model import BaseModel
from pysradb.sraweb import SRAweb
from pprint import pprint
from varname import nameof

# from celline.utils.type import pl_ptr


class GSE(BaseModel):
    DB: Final[SRAweb] = SRAweb()

    class Schema(NamedTuple):
        accession_id: str
        title: str
        summary: str
        child_gsm_ids: str
        # projna_id = Ref
        # srp_id = "srp_id"

    def set_class_name(self) -> str:
        return __class__.__name__

    def set_schema(self) -> Type[Schema]:
        return GSE.Schema

    def exist(self, gse_id: str):
        return (
            self.df.filter(self.plptr(GSE.Schema.accession_id) == gse_id).shape[0]
        ) != 0

    def search(self, gse_id: str) -> Schema:
        if self.exist(gse_id):
            return self.as_schema(
                GSE.Schema,
                self.df.filter(self.plptr(GSE.Schema.accession_id) == gse_id).head(1),
            )[0]
        __result = GSE.DB.fetch_gds_results(gse_id)
        if __result is None:
            raise KeyError(f"Requested GSE: {gse_id} does not exists in database.")
        target_gsm = (__result.query(f'accession == "{gse_id}"')).to_dict()
        del __result
        return self.add_schema(
            GSE.Schema(
                accession_id=str(target_gsm["accession"][0]),
                title=str(target_gsm["title"][0]),
                summary=str(target_gsm["summary"][0]),
                child_gsm_ids=",".join(
                    d["accession"] for d in target_gsm["samples"][0]
                ),
            )
        )  # type: ignore
