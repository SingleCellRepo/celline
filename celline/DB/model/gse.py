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

    def set_scheme(self) -> Type[Schema]:
        return GSE.Schema

    def exist(self, gse_id: str):
        return (
            self.df.filter(self.plptr(GSE.Schema.accession_id) == gse_id).shape[0]
        ) != 0

    def search(self, gse_id: str):
        if self.exist(gse_id):
            return self.df.filter(self.plptr(GSE.Schema.accession_id) == gse_id).head(1)
        __result = GSE.DB.fetch_gds_results(gse_id)
        if __result is None:
            raise KeyError(f"Requested GSE: {gse_id} does not exists in database.")
        target_gsm = (__result.query(f'accession == "{gse_id}"')).to_dict()
        del __result
        gse = self.as_dataframe(
            GSE.Schema(
                accession_id=str(target_gsm["accession"][0]),
                title=str(target_gsm["title"][0]),
                summary=str(target_gsm["summary"][0]),
                child_gsm_ids=",".join(
                    d["accession"] for d in target_gsm["samples"][0]
                ),
            )
        )
        self.df = pl.concat([self.df, gse])
        self.flush()
        return gse

    T1 = TypeVar("T1")
