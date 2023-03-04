from celline.config import Config
import yaml
from typing import Dict, List, Union
import os


def read_accessions() -> Dict[str, List[Dict]]:
    filepath = f"{Config.EXEC_ROOT}/DB/accessions.yaml"
    if os.path.exists(filepath):
        with open(filepath, mode="r") as f:
            return yaml.safe_load(f)
    else:
        return {"SRR": {}, "GSM": {}, "GSE": {}}


def write_accessions(yamldata: Dict):
    with open(f"{Config.EXEC_ROOT}/DB/accessions.yaml", mode="w") as f:
        yaml.dump(yamldata, f)


def append_accessions(accessions: Dict):
    existing = read_accessions()
    gse = accessions["GSE"]
    if gse["id"] not in existing["GSE"]:
        existing["GSE"][gse["id"]] = gse
    for gsmid in accessions["GSM"]:
        if gsmid["id"] not in existing["GSM"]:
            existing["GSM"][gsmid["id"]] = gsmid
    for el in accessions["SRR"]:
        for srrid in el:
            if srrid["id"] not in existing["SRR"]:
                existing["SRR"][srrid["id"]] = el
    write_accessions(existing)


def read_runs() -> List[str]:
    filepath = f"{Config.PROJ_ROOT}/runs.tsv"
    if os.path.exists(filepath):
        with open(filepath, mode="r") as f:
            return f.read().split("\n")
    else:
        return []


def append_runs(gsm_ids: List[str]):
    runs = read_runs()
    for gsm_id in gsm_ids:
        if gsm_id not in runs:
            if gsm_id != "" or gsm_id != None:
                runs.append(gsm_id)
    with open(f"{Config.PROJ_ROOT}/runs.tsv", mode="w") as f:
        f.write("\n".join(runs))
