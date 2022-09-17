import sys
from pandas import DataFrame
from cellpline.ncbi.srr import SRR
from cellpline.utils.exceptions import NCBIException
from cellpline.utils.config import Config
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
