# import celline.DB._base import
from enum import Enum, unique
import polars as pl
from typing import List, Final, NamedTuple, Type, get_type_hints
from celline.DB.dev.model import BaseModel
from pysradb.sraweb import SRAweb
from pprint import pprint
from varname import nameof


class GSM(BaseModel):
    DB: Final[SRAweb] = SRAweb()

    class Schema(NamedTuple):
        accession_id: str
        title: str
        summary: str
        species: str
        raw_link: str
        srx_id: str
        parent_gse_id: str
        child_srr_ids: str
        # projna_id = Ref
        # srp_id = "srp_id"

    def set_class_name(self) -> str:
        return __class__.__name__

    def set_scheme(self) -> Type[Schema]:
        return GSM.Schema

    def exist(self, gsm_id: str):
        return (
            self.df.filter(self.plptr(GSM.Schema.accession_id) == gsm_id).shape[0]
        ) != 0

    def search(self, gsm_id: str):
        if self.exist(gsm_id):
            return self.df.filter(self.plptr(GSM.Schema.accession_id) == gsm_id).head(1)
        __result = GSM.DB.fetch_gds_results(gsm_id)
        if __result is None:
            raise KeyError(f"Requested GSM: {gsm_id} does not exists in database.")
        newdata = self.as_dataframe(
            GSM.Schema(
                accession_id=__result["accession"][1],
                title=__result["title"][0],
                summary=__result["summary"][0],
                species=__result["taxon"][0],
                raw_link=__result["ftplink"][0],
                srx_id=__result["SRA"][0],
                parent_gse_id=__result["accession"][0],
            )
        )
        del __result
        self.df = pl.concat([self.df, newdata])
        self.flush()
        return newdata
