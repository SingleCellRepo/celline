from __future__ import annotations  # type: ignore
from typing import List, Dict, Union, Optional, TYPE_CHECKING
from pysradb.sraweb import SRAweb
from requests_html import AsyncHTMLSession, HTMLResponse
from celline.data.html import HTMLStructure
from celline.plugins.collections.generic import ListC
from celline.utils.type import ClassProperty
from celline.data.files import read_accessions
import inquirer
import inquirer.themes as themes
from tqdm import tqdm
import asyncio
from celline.config import Config, Setting
import yaml
from enum import Enum
import re
import os

DB = SRAweb()


class SRR:
    class ScRun:
        class FileType(Enum):
            Unknown = 0
            Fastq = 1
            Bam = 2

            @staticmethod
            def from_string(t: str):
                if (t == "fastq") or (t == "Fastq"):
                    return SRR.ScRun.FileType.Fastq
                elif (t == "bam") or (t == "Bam"):
                    return SRR.ScRun.FileType.Bam
                else:
                    return SRR.ScRun.FileType.Unknown

        class CloudPath:
            __cloud_path: str

            def __init__(self, cloud_path: str) -> None:
                self.__cloud_path = cloud_path
                pass

            @property
            def path(self) -> str:
                """Returns cloud file path"""
                return self.__cloud_path

            @property
            def name(self) -> str:
                """Returns could file name"""
                return self.__cloud_path.split("/")[-1]

        class Lane:
            __lane_id: str

            def __init__(self, lane_id: Optional[str] = None) -> None:
                if lane_id is not None:
                    self.__lane_id = lane_id
                pass

            @staticmethod
            def auto(
                filetype: SRR.ScRun.FileType,
                cloud_file_name: str,
                ignore_warning: bool = False,
            ):
                lane: SRR.ScRun.Lane = SRR.ScRun.Lane()
                if filetype == SRR.ScRun.FileType.Fastq:
                    search_result_L = re.search("_L00", cloud_file_name)
                    error = search_result_L is None
                    if search_result_L is not None:
                        index = search_result_L.span()[1]
                        if cloud_file_name[index].isdecimal():
                            lane.__lane_id = "L{:0=3}".format(
                                int(cloud_file_name[index])
                            )
                            del search_result_L
                            del index
                        else:
                            error = True
                    if error:
                        print("[Warning] Could not find lane ID in the cloud path.")
                        if not ignore_warning:
                            while True:
                                id_cand = input(
                                    f"Lane ID? ({cloud_file_name}) L00<?>: "
                                )
                                if id_cand.isdecimal():
                                    lane.__lane_id = "L{:0=3}".format(id_cand)
                                    break

                else:
                    lane.__lane_id = "Null"
                return lane

            @property
            def lane_id(self) -> Optional[str]:
                """Returns lane id"""
                if self.__lane_id == "Null":
                    return None
                return self.__lane_id

            @property
            def name(self) -> str:
                """Returns lane id as string"""
                return self.__lane_id

        class ReadType(Enum):
            Unknown = 0
            R1 = 1
            R2 = 2
            I1 = 3
            I2 = 4

            @staticmethod
            def from_string(t: str):
                if t == "R1":
                    return SRR.ScRun.ReadType.R1
                elif t == "R2":
                    return SRR.ScRun.ReadType.R2
                elif t == "I1":
                    return SRR.ScRun.ReadType.I1
                elif t == "I2":
                    return SRR.ScRun.ReadType.I2
                else:
                    return SRR.ScRun.ReadType.Unknown

        class FileSize:
            __size: float

            def __init__(self, size: float) -> None:
                self.__size = size
                pass

            @staticmethod
            def from_string(size_str: str):
                tb = re.search("T", size_str)
                gb = re.search("G", size_str)
                mb = re.search("M", size_str)
                kb = re.search("K", size_str)
                if tb is not None:
                    return SRR.ScRun.FileSize(float(size_str.replace("T", "")) * 1024)
                elif gb is not None:
                    return SRR.ScRun.FileSize(float(size_str.replace("G", "")))
                elif mb is not None:
                    return SRR.ScRun.FileSize(float(size_str.replace("M", "")) / 1024)
                elif kb is not None:
                    return SRR.ScRun.FileSize(
                        float(size_str.replace("K", "")) / (1024 ^ 2)
                    )
                else:
                    return SRR.ScRun.FileSize(0)

            @property
            def sizeTB(self) -> float:
                return self.__size / 1024

            @property
            def sizeGB(self) -> float:
                return self.__size

            @property
            def sizeMB(self) -> float:
                return self.__size / 1024

            @property
            def sizeKB(self) -> float:
                return self.__size / (1024 ^ 2)

        def __init__(
            self,
            id: str,
            cloud_path: CloudPath,
            filesize: FileSize,
            readtype: ReadType,
            lane: Lane,
        ):
            self.id: str = id
            """SRR ID"""
            self.cloud_path: SRR.ScRun.CloudPath = cloud_path
            self.filesize: SRR.ScRun.FileSize = filesize
            self.readtype: SRR.ScRun.ReadType = readtype
            self.lane: SRR.ScRun.Lane = lane

    def __init__(self, id: str, parent_gsm: str, file_type: ScRun.FileType, runs: List[ScRun]) -> None:
        self.id: str = id
        self.parent_gsm: str = parent_gsm
        self.file_type: SRR.ScRun.FileType = file_type
        self.sc_runs: List[SRR.ScRun] = runs
        pass

    @ClassProperty
    @classmethod
    def runs(cls):
        srrs: List[SRR] = []
        acessions: Dict[str, List] = {}
        """SRRID: runs"""
        raw_accessions = read_accessions()["SRR"]
        for id in raw_accessions:
            if id not in acessions:
                acessions[id] = []
            acessions[id].append(raw_accessions[id])
        for target_id in acessions:
            srrs.append(SRR.from_dict(acessions[target_id]))
        return srrs

    @staticmethod
    async def __fetch(sra_run_id: str):
        def build_scrun(raw: HTMLStructure):
            cloud_path = SRR.ScRun.CloudPath(raw.cloud_path)
            filetype = SRR.ScRun.FileType.from_string(raw.filetype)
            return SRR.ScRun(
                id=sra_run_id,
                cloud_path=SRR.ScRun.CloudPath(raw.cloud_path),
                filesize=SRR.ScRun.FileSize.from_string(raw.filesize),
                readtype=SRR.ScRun.ReadType.from_string(raw.read),
                lane=SRR.ScRun.Lane.auto(
                    filetype=filetype, cloud_file_name=cloud_path.name
                ),
            )

        session = AsyncHTMLSession()
        response: HTMLResponse = await session.get(
            f"https://trace.ncbi.nlm.nih.gov/Traces/index.html?view=run_browser&acc={sra_run_id}&display=data-access"
        )  # type: ignore
        await response.html.arender(
            wait=Setting.wait_time / 2, sleep=int(Setting.wait_time / 2)
        )
        result = HTMLStructure.build(response)
        if result.Length == 0:
            print(f"[ERROR] Could not find Run ID {sra_run_id}")
            quit()
        strct = result[0]
        if strct is None:
            print(f"[ERROR] Could not find Run ID {sra_run_id}")
            quit()

        return SRR(
            id=sra_run_id,
            parent_gsm=strct.gsmid,
            file_type=SRR.ScRun.FileType.from_string(strct.filetype),
            runs=result.Select(
                lambda raw: build_scrun(raw)).Values
        )

    @staticmethod
    def search(id: str) -> SRR:
        for srr in SRR.runs:
            if srr.id == id:
                return srr
        return asyncio.get_event_loop().run_until_complete(SRR.__fetch(id))

    @staticmethod
    def from_dict(dict: List[Dict]) -> SRR:
        if len(dict) == 0:
            print("[ERROR] Could not find SRR.")
            quit()
        id = dict[0]["id"]
        return SRR(
            id=id,
            parent_gsm=dict[0]["parent_gsm"],
            file_type=SRR.ScRun.FileType.from_string(
                dict[0]["filetype"]),
            runs=[
                SRR.ScRun(
                    id=d["id"],
                    cloud_path=SRR.ScRun.CloudPath(d["path"]),
                    filesize=SRR.ScRun.FileSize(d["size"]),
                    lane=SRR.ScRun.Lane(d["readtype"]),
                    readtype=SRR.ScRun.ReadType.from_string(d["readtype"]),
                )
                for d in dict
            ],
        )

    def to_dict(self) -> List[Dict]:
        result: List[Dict] = []
        for run in self.sc_runs:
            result.append(
                {
                    "id": self.id,
                    "path": run.cloud_path.path,
                    "size": f"{run.filesize.sizeGB}G",
                    "filetype": self.file_type.name,
                    "lane_id": run.lane.lane_id,
                    "readtype": run.readtype.name,
                    "parent_gsm": self.parent_gsm,
                }
            )
        return result


class GSM:
    def __init__(
        self,
        id: str,
        title: str,
        summary: str,
        species: str,
        raw_link: str,
        srx_id: str,
        child_srr_ids: List[str],
        parent_gse_id: str
    ):
        self.id: str = id
        """GSE ID"""
        self.title: str = title
        """Title name"""
        self.summary: str = summary
        """Experiment summary"""
        self.species: str = species
        """Species name"""
        self.raw_link: str = raw_link
        """Raw FTP link"""
        self.srx_id: str = srx_id
        """SRX ID"""
        self.child_srr_ids: List[str] = child_srr_ids
        """SRA Run ID (Run Accession)"""
        self.parent_gse_id: str = parent_gse_id
        """Parent GSE ID"""

    @ClassProperty
    @classmethod
    def runs(cls):
        gsms: List[GSM] = []
        raw_gsms = read_accessions()["GSM"]
        for _id in raw_gsms:
            gsms.append(GSM.from_dict(raw_gsms[_id]))
        return gsms

    @staticmethod
    def search(id: str):
        if not id.startswith("GSM"):
            print("[ERROR] Given ID is not a valid GSM ID.")
            quit()
        for gsm in GSM.runs:
            if gsm.id == id:
                return gsm
        __result = DB.fetch_gds_results(id)
        if __result is None:
            print("[ERROR] Could not find target GSM data.")
            quit()
        target_gsm = (__result.query(f'accession == "{id}"')).to_dict()
        return GSM(
            id=target_gsm["accession"][1],
            title=target_gsm["title"][1],
            summary=target_gsm["summary"][1],
            species=target_gsm["taxon"][1],
            raw_link=target_gsm["ftplink"][1],
            srx_id=target_gsm["SRA"][1],
            child_srr_ids=DB.gsm_to_srr(id)["run_accession"].to_list(),
            parent_gse_id=(__result.query(
                'accession.str.contains("GSE")', engine='python')).to_dict()["accession"][0]
        )

    @staticmethod
    def from_dict(dict: Dict):
        return GSM(
            id=dict["id"],
            title=dict["title"],
            summary=dict["summary"],
            species=dict["species"],
            raw_link=dict["raw_link"],
            srx_id=dict["srx_id"],
            child_srr_ids=dict["child_srr_ids"],
            parent_gse_id=dict["parent_gse_id"],
        )

    def to_dict(self) -> Dict[str, Union[str, List[str]]]:
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "species": self.species,
            "raw_link": self.raw_link,
            "srx_id": self.srx_id,
            "child_srr_ids": self.child_srr_ids,
            "parent_gse_id": self.parent_gse_id,
        }


class GSE:
    def __init__(
        self,
        id: str,
        title: str,
        summary: str,
        species: str,
        raw_link: str,
        projna_id: str,
        srp_id: str,
        child_gsm_ids: List[Dict[str, str]],
    ):
        self.id: str = id
        """GSE ID"""
        self.title: str = title
        """Title name"""
        self.summary: str = summary
        """Experiment summary"""
        self.species: str = species
        """Species name"""
        self.raw_link: str = raw_link
        """Raw FTP link"""
        self.projna_id: str = projna_id
        """PROJNA (bioproject) ID"""
        self.srp_id: str = srp_id
        """SRP ID"""
        self.child_gsm_ids: List[Dict[str, str]] = child_gsm_ids
        """accession: GSM ID\ntitle: sample name"""

    @ClassProperty
    @classmethod
    def runs(cls):
        gses: List[GSE] = []
        raw_gses = read_accessions()["GSE"]
        for _id in raw_gses:
            gses.append(GSE.from_dict(raw_gses[_id]))
        return gses

    @staticmethod
    def search(id: str):
        if not id.startswith("GSE"):
            print("[ERROR] Given ID is not a valid GSE ID.")
            quit()
        for gse in GSE.runs:
            if gse.id == id:
                return gse
        __result = DB.fetch_gds_results(id)
        if __result is None:
            print("[ERROR] Could not find target GSE data.")
            quit()
        target_gse = __result.query(f'accession == "{id}"')
        return GSE(
            id=target_gse.pipe(lambda d: d["accession"])[0],
            title=target_gse.pipe(lambda d: d["title"])[0],
            summary=target_gse.pipe(lambda d: d["summary"])[0],
            species=target_gse.pipe(lambda d: d["taxon"])[0],
            raw_link=target_gse.pipe(lambda d: d["ftplink"])[0],
            projna_id=target_gse.pipe(lambda d: d["bioproject"])[0],
            srp_id=target_gse.pipe(lambda d: d["SRA"])[0],
            child_gsm_ids=target_gse.pipe(lambda d: d["samples"])[0],
        )

    @staticmethod
    def from_dict(dict: Dict):
        return GSE(
            id=dict["id"],
            title=dict["title"],
            summary=dict["summary"],
            species=dict["species"],
            raw_link=dict["raw_link"],
            projna_id=dict["projna_id"],
            srp_id=dict["srp_id"],
            child_gsm_ids=dict["child_gsm_ids"],
        )

    def to_dict(self) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "species": self.species,
            "raw_link": self.raw_link,
            "projna_id": self.projna_id,
            "srp_id": self.srp_id,
            "child_gsm_ids": self.child_gsm_ids,
        }
