from __future__ import annotations

# import celline.DB._base import
from enum import Enum, unique
import polars as pl
from typing import Callable, List, Final, NamedTuple, Type, TypeVar
from celline.DB.dev.model import BaseModel, Primary, BaseSchema
from pysradb.sraweb import SRAweb
from varname import nameof

from dataclasses import dataclass

# from celline.utils.type import pl_ptr


@dataclass
class SRA_GSE_Schema(BaseSchema):
    summary: str


class SRA_GSE(BaseModel[SRA_GSE_Schema]):
    DB: Final[SRAweb] = SRAweb()

    def set_class_name(self) -> str:
        return __class__.__name__

    def def_schema(self) -> type[SRA_GSE_Schema]:
        return SRA_GSE_Schema

    def search(self, acceptable_id: str, force_search=False) -> SRA_GSE_Schema:
        cache = self.get_cache(acceptable_id, force_search)
        if cache is not None:
            return cache
        __result = SRA_GSE.DB.fetch_gds_results(acceptable_id)
        if __result is None:
            raise KeyError(
                f"Requested GSE: {acceptable_id} does not exists in database."
            )
        target_gsm = (__result.query(f'accession == "{acceptable_id}"')).to_dict()
        del __result
        return self.add_schema(
            SRA_GSE_Schema(
                key=str(target_gsm["accession"][0]),
                title=str(target_gsm["title"][0]),
                summary=str(target_gsm["summary"][0]),
                children=",".join(d["accession"] for d in target_gsm["samples"][0]),
                parent=None,
            )
        )
