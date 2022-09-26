from argparse import ArgumentParser
import asyncio
from typing import List

from celline.jobs.jobs import JobSystem
from celline.ncbi.srr import SRR
from celline.plugins.collections.generic import ListC
from celline.plugins.reflection.module import BindingFlags, Module
from celline.plugins.reflection.type import typeof
from celline.utils.exceptions import InvalidArgumentException
from celline.utils.typing import NullableString


class AddController:
    run_id: str

    def __init__(self, options: List[str]) -> None:
        if len(options) < 1:
            raise InvalidArgumentException("Please specify run id")
        self.run_id = options[0]
        if not (self.run_id.startswith("SRR") | self.run_id.startswith("GSM")):
            raise InvalidArgumentException("Run ID should SRR ID or GSM ID.")
        pass

    def call(self) -> None:
        asyncio.get_event_loop().run_until_complete(
            SRR.add(self.run_id))


class DumpController:
    def __init__(self) -> None:
        pass

    def call(self, jobsystem: JobSystem, nthread: int, cluster_server_name: NullableString) -> None:
        SRR.dump(
            jobsystem=jobsystem,
            max_nthread=nthread,
            cluster_server_name=cluster_server_name
        )
        return


class CountController:
    def __init__(self) -> None:
        pass

    def call(self, jobsystem: JobSystem, each_nthread: int, nthread: int, cluster_server_name: NullableString) -> None:
        SRR.count(
            jobsystem=jobsystem,
            each_nthread=each_nthread,
            max_nthread=nthread,
            cluster_server_name=cluster_server_name
        )
        return
