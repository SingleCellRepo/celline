from typing import Type, NamedTuple, Final, Optional, List, Dict
from enum import Enum
from celline.DB.dev.model import BaseModel
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ElementTree, Element
import requests


class SRR(BaseModel):
    __BASE_XML_PATH: Final[
        str
    ] = "https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/run_new?acc="

    class Schema(NamedTuple):
        accession_id: str
        strategy: str
        parent_gsm: str

    def set_class_name(self) -> str:
        return __class__.__name__

    def set_scheme(self) -> type[Schema]:
        return SRR.Schema

    def exist(self, srr_id: str):
        return (
            self.df.filter(self.plptr(SRR.Schema.accession_id) == srr_id).shape[0]
        ) != 0

    def decide_strategy(self, file_infos: List[Dict[str, str]]) -> Optional[str]:
        suggested_strategy: Optional[str] = None
        for file_info in file_infos:
            if ".bam" in file_info["filename"]:
                return "bam"
            if (".fastq" in file_info) or (".fq" in file_info):
                suggested_strategy = "fastq"
        return suggested_strategy

    def search(self, srr_id: str):
        if self.exist(srr_id):
            return self.df.filter(self.plptr(SRR.Schema.accession_id) == srr_id).head(1)
        url = f"{SRR.__BASE_XML_PATH}{srr_id}"
        tree = ET.fromstring(requests.get(url, timeout=100).content.decode())
        member = tree.find("RUN/Pool/Member")
        if member is None:
            raise KeyError("Could not find member. Is SRR ID correct?")
        __files = tree.find("RUN/SRAFiles")
        if __files is None:
            raise KeyError("Could not find files. Is SRR ID correct?")
        files = [
            file
            for file in [d.attrib for d in list(__files)]
            if file["supertype"] == "Original"
        ]
        if len(files) == 0:
            raise KeyError("Could not find original files.")
        strategy = self.decide_strategy(files)
        if strategy is None:
            raise TypeError(
                "Could not resolve given accession because original filename does not contains fastq or bam."
            )
        newdata = SRR.Schema(
            accession_id=srr_id,
            strategy=strategy,
            parent_gsm=member.attrib["sample_name"],
        )
