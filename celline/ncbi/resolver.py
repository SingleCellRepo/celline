import os
from typing import List

from pandas import DataFrame

from celline.utils.config import Config


class RuntableResolver:
    @staticmethod
    def has_error(runtable: DataFrame, target_runid: str):
        if target_runid.startswith("SRR"):
            identity = "run_id"
        elif target_runid.startswith("GSM"):
            identity = "gsm_id"
        else:
            return True
        return runtable[runtable[identity] ==
                        target_runid]["dumped_filepath"].str.contains("None").any()

    @staticmethod
    def get_all_error_dfs(runtable: DataFrame) -> List[str]:
        error_dfs = runtable[runtable["dumped_filepath"].str.contains(
            "None")].drop_duplicates()
        if error_dfs.size == 0:
            return []
        return error_dfs["gsm_id"].drop_duplicates().tolist()

    @staticmethod
    def validate(runtable: DataFrame):
        gsms = RuntableResolver.get_all_error_dfs(runtable)
        for gsm in gsms:
            print(f"[ERROR] Error detected in {gsm}. None data appearing")
        if len(gsms) != 0:
            quit()
