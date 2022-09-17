import sys
from pandas import DataFrame
from celline.ncbi.srr import SRR
from celline.utils.exceptions import NCBIException
from celline.utils.config import Config
import toml


class Test:
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
