import asyncio
import re
from typing import Dict, List, Union

from celline.utils.config import Setting
from celline.utils.exceptions import NCBIException
from celline.utils.loader import Loader
from pandas import DataFrame, Series
from requests_html import AsyncHTMLSession, HTMLResponse

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
        pass


class SRR:
    runs: Dict[str, _SRR] = {}

    @staticmethod
    async def fetch(run_id: str):
        """
        Fetch target sra run data
        """
        thread_loader = Loader()
        thread_loader.delay = 0.15
        thread_loader.format = "{SYMBOL}  {STATUS}"
        thread_loader.start_loading(f"Fetching {run_id}...")
        session = AsyncHTMLSession()
        r: HTMLResponse = await session.get(
            f"https://trace.ncbi.nlm.nih.gov/Traces/index.html?view=run_browser&acc={run_id}&display=data-access"
        )  # type: ignore
        await r.html.arender(wait=Setting.wait_time/2, sleep=int(Setting.wait_time/2))
        thread_loader.stop_loading(status="Finished fetching")
        return r

    @staticmethod
    def build(response: HTMLResponse, run_id: str, sample_name: NullableString = None, use_interactive: bool = True):

        def get_sample_name(sample_name: NullableString = None):
            if sample_name is not None:
                return str(sample_name)
            while(True):
                sample_name_str: str = input("Sample name? ")
                if sample_name_str != "":
                    break
                else:
                    print("Empty sample name is not allowed")
            return sample_name_str
        sample_name_str: str = get_sample_name(sample_name)

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

        def build_SRR(series: Series, run_id: str, use_interactive: bool) -> _SRR:
            def get_sampleid(cloud_file_name: str, filetype: str):
                search_result = re.search(
                    "_S",
                    cloud_file_name
                )
                if filetype == "fastq":
                    if search_result is not None:
                        sampleid = search_result.span()[1]
                    else:
                        sampleid = 1
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
                        laneid = sample_name[index:index+3]
                        return laneid
                    else:
                        if interactive:
                            while(True):
                                laneid = input(
                                    f"Could not detect laneID automatically\ndetected file name: {sample_name}\nlaneID? L[001-]: ")
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
                    search_result = re.search(
                        "_R",
                        cloud_file_name
                    )
                    if search_result is not None:
                        index = search_result.span()[1]
                        idnum = f"R{sample_name[index]}"
                    else:
                        result = re.search(
                            "_I",
                            sample_name
                        )
                        # suspect index
                        if result is not None:
                            index = result.span()[1]
                            idnum = f"I{sample_name[index]}"
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
            cloud_file_name: str = series["Name"].split("/")[-1]
            srr.sample_id = get_sampleid(cloud_file_name, filetype)
            srr.lane_id = get_laneid(
                cloud_file_name=cloud_file_name,
                filetype=filetype,
                sample_name=sample_name_str,
                interactive=use_interactive
            )
            srr.read_type = get_readtype(
                cloud_file_name=cloud_file_name,
                filetype=filetype,
                sample_name=sample_name_str,
                interactive=use_interactive
            )
            srr.egress = str(series["Free Egress"])
            srr.raw_filename = get_raw_filename(
                sample_name=sample_name_str,
                read_type=srr.read_type,
                run_id=run_id,
                filetype=filetype
            )
            srr.dumped_filepath = build_dumped_filename(
                sample_name=sample_name_str,
                filetype=srr.filetype,
                sample_id=srr.sample_id,
                lane_id=srr.lane_id,
                read_type=srr.read_type
            )
            return srr
        for col_n in range(len(runtable.index)):
            build_SRR(
                series=runtable[runtable.index == col_n],
                run_id=run_id,
                use_interactive=use_interactive
            )

    def __init__(self, run_id: str, sample_name: NullableString = None) -> None:
        # Run fetch process
        response = asyncio\
            .get_event_loop()\
            .run_until_complete(SRR.fetch(run_id))
        SRR.build(response, run_id, sample_name)
        pass
