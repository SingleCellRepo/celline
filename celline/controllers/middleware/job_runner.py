from argparse import ArgumentParser
from typing import Any, Dict, List, Union

from celline.jobs.jobs import JobSystem
from celline.utils.exceptions import (InvalidJobException,
                                      InvalidJobSystemException)
from celline.utils.typing import NullableString


class JobRunner:
    def __init__(self, options: List[str], argparser: ArgumentParser) -> None:
        argparser.add_argument("-j", "--job", type=str)
        jobstr: NullableString = argparser.parse_args(options).job
        if jobstr is None:
            self.usejob = False
            self.jobsystem = JobSystem.default_bash
            self.servername = ""
        else:
            self.usejob = True
            if not "@" in jobstr:
                raise InvalidJobException(
                    "Please specify server name like [JobSystem]@[ServerName]")
            __jobs = jobstr.split("@")
            all_jobsystems = [jsys.name for jsys in JobSystem]
            if __jobs[0] not in all_jobsystems:
                raise InvalidJobException(
                    f"Could not specify the jobsystem: {__jobs[0]}")
            self.jobsystem = JobSystem(__jobs[0])
            self.servername = __jobs[1]
            del __jobs
        pass
