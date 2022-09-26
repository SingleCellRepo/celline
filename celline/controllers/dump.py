from typing import List

from celline.jobs.jobs import JobSystem
from celline.ncbi.srr import SRR
from celline.utils.typing import NullableString


class DumpController():
    def __init__(self) -> None:
        pass

    def call(self, jobsystem: JobSystem, nthread: int, cluster_server_name: NullableString) -> None:
        SRR.dump(
            jobsystem=jobsystem,
            max_nthread=nthread,
            cluster_server_name=cluster_server_name
        )
        return
