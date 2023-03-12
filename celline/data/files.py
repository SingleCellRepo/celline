from __future__ import annotations
from celline.config import Config
import yaml
from typing import Dict, List, Union, Optional
import os
import pandas as pd
from pprint import pprint


def read_accessions() -> Dict[str, Dict]:
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


def read_runs() -> pd.DataFrame:
    filepath = f"{Config.PROJ_ROOT}/runs.tsv"
    if os.path.exists(filepath):
        return pd.read_csv(filepath, sep="\t")
    else:
        return pd.DataFrame(columns=["gsm_id", "sample_name"])


def append_runs(gsm_id: str, sample_name: str):
    filepath = f"{Config.PROJ_ROOT}/runs.tsv"
    runs = read_runs()
    if runs.pipe(lambda df: df[df.gsm_id == gsm_id]).index.size == 0:
        runs = pd.concat(
            [
                runs,
                pd.DataFrame(
                    index=[0], data={"gsm_id": gsm_id, "sample_name": sample_name}
                )
            ]
        )
    runs.set_index("gsm_id").to_csv(filepath, sep="\t")
