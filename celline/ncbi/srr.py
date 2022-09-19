import asyncio
import os
import re
import sys
from typing import Dict, List, Union

import pandas as pd  # type: ignore
import tqdm  # type: ignore
from pandas import DataFrame, Series
from requests_html import AsyncHTMLSession, HTMLResponse  # type: ignore

from celline.utils.config import Config, Setting
from celline.utils.exceptions import (InvalidDataFrameHeaderException,
                                      NCBIException)
from celline.utils.loader import Loader

##Type alias#############################
NullableString = Union[str, None]
#########################################


class _SRR:
    # def __init__(self, dumped_filepath: str, cloud_filepath: str, raw_filename: str, sample_name: str, sample_id: NullableString, lane_id: NullableString, read_type: NullableString, run_id: str, gsm_id: str, egress: str, filetype: str, sizeGB: float, spieces: str, location: str) -> None:
    # self.dumped_filepath = dumped_filepath
    # self.cloud_filepath = cloud_filepath
    # pass
    dumped_filepath: str = ""
    cloud_filepath: str = ""
    raw_filename: str = ""
    sample_name: str = ""
    sample_id: NullableString = None
    lane_id: NullableString = None
    read_type: NullableString = None
    """
    Read type of each lane, structually defined R1, R2, I1, I2
    """
    run_id: str = ""
    gsm_id: str = ""
    egress: str = "-"
    filetype: str = ""
    sizeGB: float = 0
    spieces: str = ""
    location: str = ""

    def __init__(self, run_id: str) -> None:
        if not run_id.startswith("SRR"):
            raise NCBIException("Please specify SRR ID.")
        self.run_id = run_id
        pass


class SRR:
    def __init__(self) -> None:
        pass

    @staticmethod
    async def __fetch(run_id: str, visualize=True):
        """
        Fetch target sra run data
        """
        if visualize:
            thread_loader = Loader()
            thread_loader.delay = 0.15
            thread_loader.format = "{SYMBOL}  {STATUS}"
            thread_loader.start_loading(f"⚙️ Fetching {run_id}...")
        session = AsyncHTMLSession()
        r: HTMLResponse = await session.get(
            f"https://trace.ncbi.nlm.nih.gov/Traces/index.html?view=run_browser&acc={run_id}&display=data-access"
        )  # type: ignore
        await r.html.arender(wait=Setting.wait_time/2, sleep=int(Setting.wait_time/2))
        if visualize:
            thread_loader.stop_loading(status="Finished fetching")
        return r

    @staticmethod
    def __build(response: HTMLResponse, run_id: str, sample_name: str, use_interactive=True):
        def get_headers() -> List[str]:
            headers = response.html.find(
                "#ph-run-browser-data-access > div:nth-child(2) > table > thead > tr"
            )[0].text.split("\n")  # type: ignore
            return headers[2:len(headers)]

        def build_run_table():
            num = 1
            all_data: List[List[str]] = []
            while(True):
                data = response.html.find(
                    f"#ph-run-browser-data-access > div:nth-child(2) > table > tbody > tr:nth-child({num})"
                )
                if len(data) == 0:  # type: ignore
                    break
                data = data[0].text.split("\n")  # type: ignore
                data = data[len(data) - 4:len(data)]
                if num == 1:
                    all_data = [data]
                else:
                    all_data.append(data)
                num += 1
            return DataFrame(
                all_data,
                columns=get_headers()
            )
        runtable = build_run_table()

        def get_filetype() -> str:
            # Define filetype
            cloud_filepath: str = runtable["Name"][0]
            if (
                re.search(
                    ".fastq.gz",
                    cloud_filepath
                ) is not None
            ) | (
                re.search(
                    ".fq.gz",
                    cloud_filepath
                ) is not None
            ) | (
                re.search(
                    ".fastq",
                    cloud_filepath
                ) is not None
            ) | (
                re.search(
                    ".fq",
                    cloud_filepath
                ) is not None
            ):
                return "fastq"
            elif re.search(
                ".bam",
                cloud_filepath
            ) is not None:
                return "bam"
            else:
                return "unknown"
        filetype = get_filetype()

        def get_location() -> str:
            # Decide location
            if filetype == "fastq":
                return runtable["Location"].unique()[0]
            else:
                locations = runtable[runtable["Free Egress"]
                                     == "worldwide"]["Location"].unique()
                if len(locations) == 0:
                    raise NCBIException(
                        "[ERROR] Detected non-fastq filetype (bam?), but could not access file. (Not permitted anonymous access?)")
                return locations[0]
        location = get_location()

        def get_sizeGB() -> DataFrame:
            num = 1
            size_data: List[float] = []
            while(True):
                rae_size_el = response.html.find(
                    f"#ph-run-browser-data-access > div:nth-child(2) > table > tbody > tr:nth-child({num}) > td:nth-child(2)"
                )
                if len(rae_size_el) == 0:  # type: ignore
                    break
                raw_size = rae_size_el[0].text  # type: ignore
                tb = re.search("T", raw_size)
                gb = re.search("G", raw_size)
                mb = re.search("M", raw_size)
                kb = re.search("K", raw_size)
                if tb is not None:
                    size = float(raw_size[0:tb.span()[0]]) * 1024
                elif gb is not None:
                    size = float(raw_size[0:gb.span()[0]])
                elif mb is not None:
                    size = float(raw_size[0:mb.span()[0]]) / 1024
                elif kb is not None:
                    size = float(raw_size[0:kb.span()[0]]) / (1024 ^ 2)
                else:
                    raise ValueError(
                        f"Could not convert size data: {raw_size}")
                size_data.append(size)
                num += 2
            return DataFrame({"size": size_data})

        runtable = runtable[runtable["Location"] == location]\
            .reset_index()\
            .merge(
                get_sizeGB(),
                left_index=True,
                right_index=True
        )
        del runtable["index"]

        def get_GSM_spieces() -> List[str]:
            metainfo = response.html.find(
                "#ph-run_browser > h1"
            )[0].text.split(";")  # type: ignore
            return [metainfo[0].split(": ")[0], metainfo[1].replace(" ", "")]
        gsm_spieces = get_GSM_spieces()
        runtable["GSM"] = gsm_spieces[0]
        runtable["spieces"] = gsm_spieces[1]

        def build_SRR(series: Series, run_id: str, use_interactive: bool) -> _SRR:
            def get_sampleid(cloud_file_name: str, filetype: str):
                search_result = re.search(
                    "_S",
                    cloud_file_name
                )
                if filetype == "fastq":
                    if search_result is not None:
                        sampleid = cloud_file_name[search_result.span()[1]]
                    else:
                        sampleid = "1"
                    return sampleid
                else:
                    return None

            def get_laneid(cloud_file_name: str, filetype: str, sample_name: str, interactive: bool):
                if filetype == "fastq":
                    search_result = re.search(
                        "_L",
                        cloud_file_name
                    )
                    if search_result is not None:
                        index = search_result.span()[1]
                        laneid = cloud_file_name[index:index+3]
                        return laneid
                    else:
                        if interactive:
                            while(True):
                                laneid = input(
                                    f"Could not detect laneID automatically\ndetected file name: {cloud_file_name}\nlaneID? L[001-]: ")
                                if len(laneid) == 3:
                                    break
                                else:
                                    print("please designate laneID like 001")
                        else:
                            return None
                else:
                    return None

            def get_readtype(cloud_file_name: str, filetype: str, sample_name: str, interactive: bool):
                if filetype == "fastq":
                    search_result_R = re.search(
                        "_R",
                        cloud_file_name
                    )
                    if search_result_R is not None:
                        index = search_result_R.span()[1]
                        idnum = f"R{cloud_file_name[index]}"
                        return idnum
                    else:
                        search_result_I = re.search(
                            "_I",
                            cloud_file_name
                        )
                        # suspect index
                        if search_result_I is not None:
                            index = search_result_I.span()[1]
                            idnum = f"I{cloud_file_name[index]}"
                            return idnum
                        else:
                            if interactive:
                                while(True):
                                    idnum = input(
                                        f"Could not detect RepID or IndexID automatically\ndetected file name: {sample_name}\nID? R1, R2, I1, or I2: ")
                                    if idnum in ["R1", "R2", "I1", "I2"]:
                                        break
                                    else:
                                        print(
                                            "please designate ID in R1, R2, I1, or I2.")
                            else:
                                return None
                else:
                    return None

            def get_raw_filename(sample_name: str, read_type: NullableString, run_id: str, filetype: str):
                if filetype == "fastq":
                    if read_type == "R1":
                        raw_filename = f"{run_id}_1.fastq.gz"
                    elif read_type == "R2":
                        raw_filename = f"{run_id}_2.fastq.gz"
                    elif read_type == "I1":
                        raw_filename = f"{run_id}_3.fastq.gz"
                    elif read_type == "I2":
                        raw_filename = f"{run_id}_4.fastq.gz"
                    else:
                        return f"{sample_name}_Unknown.fastq.gz"
                    return raw_filename
                else:
                    return sample_name

            def build_dumped_filename(sample_name: str, filetype: str, sample_id: NullableString, lane_id: NullableString, read_type: NullableString):
                if filetype == "fastq":
                    return f"{sample_name}_S{sample_id}_L{lane_id}_{read_type}_001.fastq.gz"
                elif filetype == "bam":
                    return f'{sample_name}.bam'
                else:
                    return f'{sample_name}.unknown'

            srr = _SRR(run_id)
            # Assign parametres
            srr.cloud_filepath = str(series["Name"])
            srr.filetype = filetype
            srr.location = location
            cloud_file_name: str = srr.cloud_filepath.split("/")[-1]
            srr.sample_id = get_sampleid(cloud_file_name, filetype)
            srr.lane_id = get_laneid(
                cloud_file_name=cloud_file_name,
                filetype=filetype,
                sample_name=sample_name,
                interactive=use_interactive
            )
            srr.read_type = get_readtype(
                cloud_file_name=cloud_file_name,
                filetype=filetype,
                sample_name=sample_name,
                interactive=use_interactive
            )
            srr.egress = str(series["Free Egress"][0])
            srr.raw_filename = get_raw_filename(
                sample_name=sample_name,
                read_type=srr.read_type,
                run_id=run_id,
                filetype=filetype
            )
            srr.dumped_filepath = build_dumped_filename(
                sample_name=sample_name,
                filetype=srr.filetype,
                sample_id=srr.sample_id,
                lane_id=srr.lane_id,
                read_type=srr.read_type
            )
            srr.sizeGB = float(series["size"])
            srr.gsm_id = str(series["GSM"])
            srr.spieces = str(series["spieces"])
            return srr
        results: Dict[str, _SRR] = {}
        for col_n in range(len(runtable.index)):
            srr = build_SRR(
                series=runtable[runtable.index == col_n].iloc[0],
                run_id=run_id,
                use_interactive=use_interactive
            )
            results[srr.dumped_filepath] = srr
        return(results)

    @staticmethod
    def get_sample_name(visualize=True):
        while(True):
            sample_name_str: str = input("Sample name? ")
            if sample_name_str != "":
                break
            else:
                print("Empty sample name is not allowed")
        if visualize:
            print(
                f"\033[32m✓\033[0m  Sample name: {sample_name_str}")
        return sample_name_str

    @staticmethod
    async def add(run_id: str, default_sample_name: NullableString = None, use_interactive=True, visualize=True):
        """
       Auto-fetch and write the given run_id information in the SRA Run list file (PROJ_ROOT/runs.tsv).

        Parameters
        ----------
        run_id : str
            SRA Run ID
        default_sample_name : NullableString[str or None]
            Sample name in the given run ID, or interactively enter a sample name if None is assigned.
        use_interactive: bool = True
            Use interactive interface?
        visualize: bool = True
            Visualize terminal interface?
        """
        run_path = f"{Config.PROJ_ROOT}/runs.tsv"
        if os.path.isfile(run_path) & os.stat(run_path).st_size != 0:
            current = pd.read_csv(run_path, sep="\t", index_col=0)
        else:
            current = DataFrame()
        if default_sample_name is None:
            sample_name = SRR.get_sample_name(visualize)
        # Fetch response via fetch function.
        response = await SRR.__fetch(run_id, visualize)
        # Get runs
        runs = SRR.__build(response, run_id, sample_name, use_interactive)
        compiled = {}
        for run in runs.keys():
            compiled[run] = vars(runs[run])
        df = pd.concat(
            [
                DataFrame(compiled)
                .T
                .set_index("dumped_filepath"),
                current
            ]
        )
        df.index.name = "dumped_filepath"
        df = df.groupby(level=0).last()
        df.to_csv(
            f"{Config.PROJ_ROOT}/runs.tsv",
            sep="\t"
        )
        if visualize:
            print(
                f"\033[32m✓\033[0m  Finished writing runs.")

    @staticmethod
    async def add_range(run_list_path: str):
        COLUMS = ["SRR_ID", "sample_name"]
        if not os.path.isfile(run_list_path) | os.stat(run_list_path).st_size == 0:
            df = DataFrame(
                columns=COLUMS,
                index=None
            )
            df.set_index("SRR_ID", inplace=True)
            df.to_csv(
                run_list_path,
                sep="\t"
            )
            raise FileNotFoundError(
                f"Could not find SRR list in your project. Please write run list to {run_list_path}.\n(We prepared SRR_list template :))"
            )
        run_list = pd.read_csv(run_list_path, sep="\t")
        if not run_list.columns.tolist() in COLUMS:
            raise InvalidDataFrameHeaderException(
                f"Header must contains {COLUMS}"
            )
        runs = pd.read_csv(
            f"{Config.PROJ_ROOT}/runs.tsv",
            sep="\t",
            index_col=0
        )
        all_srr = runs["runid"].unique().tolist()
        run_list = run_list[~run_list["runid"].isin(all_srr)].reset_index()
        all_len = len(run_list["runid"])

        if all_len != 0:
            bar = tqdm(total=all_len)
            for i in range(all_len):
                target = run_list[run_list.index == i]
                srrID: str = target["SRR_ID"].unique()[0]
                sampleName: str = target["sample_name"].unique()[0]
                await SRR.add(
                    run_id=srrID,
                    default_sample_name=sampleName,
                    use_interactive=False,
                    visualize=False
                )
                bar.update(1)
            bar.clear()
