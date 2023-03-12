import inquirer
import inquirer.themes as themes
from celline.data.ncbi import GSE, GSM, SRR

# from celline.data.constructed import CellineDataStructure
from typing import List, Dict
from tqdm import tqdm
from celline.config import Config, Setting
from celline.data.files import append_accessions, append_runs, read_runs
import yaml
from celline.utils.type import ClassProperty


class NCBI:
    """
    Connect to SRA, GEO, Synapse database
    """

    @staticmethod
    def __from_gse(gse_id: str):
        """Fetch run data from GSE database"""
        gse = GSE.search(gse_id)
        choices = [
            f"{d['accession']}({d['title']})" for d in gse.child_gsm_ids]
        questions = [
            inquirer.Checkbox(
                "target_gsms",
                message="Choose dump target GSM IDs",
                choices=choices,
                carousel=True,
            )
        ]
        answers = inquirer.prompt(
            questions, theme=themes.GreenPassion(), raise_keyboard_interrupt=True
        )
        if answers is not None:
            gsms: List[GSM] = []
            gsm_ids: List[str] = []
            srrs: List[SRR] = []
            target_gsm_ids: List[str] = answers["target_gsms"]
            for gsm_i in tqdm(range(len(target_gsm_ids)), desc="Fetching GSM"):
                gsm_id = target_gsm_ids[gsm_i].split("(")[0]
                gsm_ids.append(gsm_id)
                gsm = GSM.search(gsm_id)
                gsms.append(gsm)
                target_srr_ids = gsm.child_srr_ids
                for srr_i in tqdm(
                    range(len(target_srr_ids)), desc="Fetching SRR", leave=False
                ):
                    srr = SRR.search(target_srr_ids[srr_i])
                    srrs.append(srr)
                append_runs(gsm_id, gsm.title)
            yamldata = {}
            yamldata["GSE"] = gse.to_dict()
            yamldata["GSM"] = [d.to_dict() for d in gsms]
            yamldata["SRR"] = [d.to_dict() for d in srrs]
            append_accessions(yamldata)
        return gse

    @staticmethod
    def __from_gsm(gsm_id: str):
        """Fetch run data from GSM database"""
        gsm = GSM.search(gsm_id)
        gse_id = gsm.parent_gse_id
        gses: List[GSE] = []
        for _ in tqdm(range(len(gse_id)), desc="Fetching GSE"):
            gses.append(GSE.search(gse_id))
        srr_ids = gsm.child_srr_ids
        srrs: List[SRR] = []
        for srr_i in tqdm(range(len(srr_ids)), desc="Fetching SRR", leave=False):
            srrs.append(SRR.search(srr_ids[srr_i]))
        yamldata = {}
        yamldata["GSE"] = gses[0].to_dict()
        yamldata["GSM"] = [gsm.to_dict()]
        yamldata["SRR"] = [d.to_dict() for d in srrs]
        append_accessions(yamldata)
        append_runs(gsm_id, gsm.title)
        return gsm

    @staticmethod
    def add(id: str):
        """Resolve a given id (SRR, GSM, GSE ids) to add to the run database"""
        if id.startswith("GSE"):
            NCBI.__from_gse(id)
        elif id.startswith("GSM"):
            gsm_list = id.split(",")
            gsm_ids: List[str] = []
            for gsm_el in gsm_list:
                if ":" in gsm_el:
                    target_gsm_ids = gsm_el.split(":")
                    start = int(target_gsm_ids[0].replace("GSM", ""))
                    end = int(target_gsm_ids[1].replace("GSM", "")) + 1
                    gsm_ids.extend(
                        [f"GSM{d}" for d in list(range(start, end, 1))])
                else:
                    gsm_ids.append(gsm_el)
            for i in tqdm(range(len(gsm_ids)), desc="Fetching"):
                NCBI.__from_gsm(gsm_ids[i])
        return

    @staticmethod
    def search(id: str):
        if id.startswith("GSE"):
            return NCBI.__from_gse(id)
        elif id.startswith("GSM"):
            gsm_list = id.split(",")
            gsm_ids: List[str] = []
            result: List[GSM] = []
            for gsm_el in gsm_list:
                if ":" in gsm_el:
                    target_gsm_ids = gsm_el.split(":")
                    start = int(target_gsm_ids[0].replace("GSM", ""))
                    end = int(target_gsm_ids[1].replace("GSM", "")) + 1
                    gsm_ids.extend(
                        [f"GSM{d}" for d in list(range(start, end, 1))])
                else:
                    gsm_ids.append(gsm_el)
            for i in tqdm(range(len(gsm_ids)), desc="Fetching"):
                result.append(NCBI.__from_gsm(gsm_ids[i]))
            return result
        else:
            print("[ERROR] Unknown request type")
            quit()

    @staticmethod
    def get_gsms():
        runs = {d.id: d for d in GSM.runs}
        result: Dict[str, GSM] = {}
        failed_gsm: List[str] = []
        target_runs_df = read_runs()
        for gsm_id in target_runs_df["gsm_id"].to_list():
            if gsm_id not in runs.keys():
                failed_gsm.append(gsm_id)
            else:
                result[gsm_id] = runs[gsm_id]
        for failed in failed_gsm:
            print(
                f"[ERROR] Could not find GSM ID. Did you deleted the cache? Please re-run `celline add {failed}`"
            )
        if len(failed_gsm) != 0:
            quit()
        return result
