# from typing import Type, NamedTuple, Final, Optional, List, Dict
# from enum import Enum
# from celline.DB.dev.model import BaseModel
# from xml.etree import ElementTree as ET
# from xml.etree.ElementTree import ElementTree, Element
# import requests
# import polars as pl


# class SRR(BaseModel):
#     __BASE_XML_PATH: Final[
#         str
#     ] = "https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/run_new?acc="

#     class Schema(NamedTuple):
#         accession_id: str
#         strategy: str
#         parent_gsm: str
#         raw_link: str

#     def set_class_name(self) -> str:
#         return __class__.__name__

#     def set_schema(self) -> type[Schema]:
#         return SRR.Schema

#     def exist(self, srr_id: str):
#         return (
#             self.df.filter(self.plptr(SRR.Schema.accession_id) == srr_id).shape[0]
#         ) != 0

#     def decide_strategy(self, file_infos: List[Dict[str, str]]) -> Optional[str]:
#         suggested_strategy: Optional[str] = None
#         for file_info in file_infos:
#             if ".bam" in file_info["filename"]:
#                 return "bam"
#             if (".fastq" in file_info["filename"]) or (".fq" in file_info["filename"]):
#                 suggested_strategy = "fastq"
#         if suggested_strategy is None:
#             print(file_infos)
#         return suggested_strategy

#     def search(self, srr_id: str) -> Schema:
#         if self.exist(srr_id):
#             return self.as_schema(
#                 SRR.Schema,
#                 self.df.filter(self.plptr(SRR.Schema.accession_id) == srr_id).head(1),
#             )[0]
#         url = f"{SRR.__BASE_XML_PATH}{srr_id}"
#         tree = ET.fromstring(requests.get(url, timeout=100).content.decode())
#         member = tree.find("RUN/Pool/Member")
#         if member is None:
#             raise KeyError("Could not find member. Is SRR ID correct?")
#         __files = tree.find("RUN/SRAFiles")
#         if __files is None:
#             raise KeyError("Could not find files. Is SRR ID correct?")
#         files = [
#             file
#             for file in [d.attrib for d in list(__files)]
#             if file["supertype"] == "Original"
#         ]
#         if len(files) == 0:
#             raise KeyError("Could not find original files.")
#         strategy = self.decide_strategy(files)
#         if strategy is None:
#             raise TypeError(
#                 "Could not resolve given accession because original filename does not contains fastq or bam."
#             )
#         newdata = self.add_schema(
#             SRR.Schema(
#                 accession_id=srr_id,
#                 strategy=strategy,
#                 parent_gsm=member.attrib["sample_name"],
#                 raw_link=",".join([file["url"] for file in files if "url" in file]),
#             )
#         )

#         return newdata  # type: ignore
from typing import Type, NamedTuple, Final, Optional, List, Dict
from enum import Enum
from celline.DB.dev.model import BaseModel
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ElementTree, Element
import requests
import polars as pl


class SRR(BaseModel):
    BASE_XML_PATH: Final[
        str
    ] = "https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/run_new?acc="

    class Schema(NamedTuple):
        accession_id: str
        strategy: str
        parent_gsm: str
        raw_link: str

    def set_class_name(self) -> str:
        """Set class name"""
        return self.__class__.__name__

    def set_schema(self) -> Type[Schema]:
        """Set schema"""
        return SRR.Schema

    def exist(self, srr_id: str) -> bool:
        """Check if the specified SRR ID exists"""
        return bool(
            self.df.filter(self.plptr(SRR.Schema.accession_id) == srr_id).shape[0]
        )

    @staticmethod
    def decide_strategy(file_infos: List[Dict[str, str]]) -> str:
        """Determine analysis strategy"""
        suggested_strategy: Optional[str] = None
        for file_info in file_infos:
            if ".bam" in file_info.get("filename", ""):
                return "bam"
            if (".fastq" in file_info.get("filename", "")) or (
                ".fq" in file_info.get("filename", "")
            ):
                suggested_strategy = "fastq"
        if suggested_strategy is None:
            raise ValueError("Could not resolve the strategy from given file_infos.")
        return suggested_strategy

    def search(self, srr_id: str) -> Schema:
        """Search for SRR IDs"""
        if self.exist(srr_id):
            return self.as_schema(
                SRR.Schema,
                self.df.filter(self.plptr(SRR.Schema.accession_id) == srr_id).head(1),
            )[0]
        url = f"{SRR.BASE_XML_PATH}{srr_id}"
        tree = ET.fromstring(requests.get(url, timeout=100).content.decode())
        member = tree.find("RUN/Pool/Member")
        if member is None:
            raise KeyError("Could not find member. Is SRR ID correct?")
        files_elem = tree.find("RUN/SRAFiles")
        if files_elem is None:
            raise KeyError("Could not find files. Is SRR ID correct?")
        files = [
            file
            for file in [d.attrib for d in list(files_elem)]
            if file.get("supertype") == "Original"
        ]
        if not files:
            raise KeyError("Could not find original files.")
        strategy = self.decide_strategy(files)
        newdata = self.add_schema(
            SRR.Schema(
                accession_id=srr_id,
                strategy=strategy,
                parent_gsm=member.attrib.get("sample_name"),
                raw_link=",".join([file["url"] for file in files if "url" in file]),
            )
        )

        return newdata
