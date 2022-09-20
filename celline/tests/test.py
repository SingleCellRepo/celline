import sys

import toml  # type: ignore

from celline.ncbi.srr import SRR
from celline.utils.config import Config
from celline.utils.exceptions import NCBIException
from celline.utils.directory import Directory


class Test:
    @staticmethod
    def entry():
        Directory.initialize()
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
