import sys

import toml  # type: ignore

from celline.ncbi.srr import SRR
from celline.utils.config import Config
from celline.utils.exceptions import NCBIException


class Test:
    @staticmethod
    def entry():
        with open(f"{Config.PROJ_ROOT}/setting.toml", mode="r") as f:
            print(toml.load(f))
        # print(
        #     DataFrame(
        #         index=["TEST", "TEST2"],
        #         data={
        #             "Data1": 100,
        #             "Data2": 200
        #         }
        #     ).to_dict()
        # )
        # print(
        #     vars(SRR())
        # )
