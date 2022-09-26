import argparse
import asyncio
import sys
from typing import Any, List

from celline.controllers.add import AddController
from celline.controllers.dump import DumpController
from celline.controllers.middleware.job_runner import JobRunner
from celline.controllers.middleware.sample_runner import SampleRunner
from celline.controllers.middleware.thread_runner import ThreadRunner
from celline.jobs.jobs import Jobs, JobSystem  # type:ignore
from celline.ncbi.genome import Genome
from celline.ncbi.srr import SRR
from celline.plugins.collections.generic import ListC
from celline.plugins.reflection.activator import Activator
from celline.plugins.reflection.module import Module
from celline.plugins.reflection.type import (BindingFlags, DictionaryC,
                                             KeyValuePair, TypeC, typeof)
from celline.test.test import Test
from celline.utils.config import Config, Setting
from celline.utils.exceptions import InvalidArgumentException
from celline.utils.help import Help


class ControllerManager:
    t_obj: ListC[KeyValuePair[TypeC, Any]]
    commands: ListC[KeyValuePair[str, KeyValuePair[TypeC, Any]]]

    @staticmethod
    def initialize():
        ControllerManager.t_obj = (
            Module.GetModules(dirs="celline/controllers")
            .Select(lambda module: module.GetTypes().First())
            .Where(
                lambda t: not t.IsAbstract
                & (t.BaseType.FullName == "celline.controllers.controller+Controller")
            )
            .Select(lambda t: KeyValuePair(t, Activator.CreateInstance(t)))
        )
        ControllerManager.commands = ControllerManager.t_obj.Select(
            lambda t: KeyValuePair(
                key=str(t.Key.GetProperty("command").GetValue(t.Value)), value=t
            )
        )


if __name__ == "__main__":
    cmd = sys.argv[3]
    options = sys.argv[4:]
# TODO: Future work, generalize these codes with abstract
    # Config.initialize(exec_rot_path=sys.argv[1], proj_root_path=sys.argv[2])
    # Setting.initialize()
    # Genome.initialize()
    # ControllerManager.initialize()
    # if not ControllerManager.commands.Contains(cmd):
    #     raise InvalidArgumentException(f"Could not found {cmd}")
    # target_command = (
    #     ControllerManager.commands.Where(lambda t_obj: t_obj.Key == cmd).First().Value
    # )
    # target_command.Key.GetMethod("call").Invoke(target_command.Value, options)o
    argparser = argparse.ArgumentParser(description='argument')
    job_runner = JobRunner(options, argparser)
    default_sample_runner = SampleRunner(options, argparser)
    thread_runner = ThreadRunner(options, argparser)
    if cmd == "add":
        AddController(options=options).call(
            default_sample_runner.default_sample_name)
    elif cmd == "dump":
        DumpController().call(
            jobsystem=job_runner.jobsystem,
            nthread=thread_runner.nthread,
            cluster_server_name=job_runner.servername
        )
    # SRR.dump(
    #     jobsystem=JobSystem.default_bash,
    #     max_nthread=1,
    #     cluster_server_name="cosmos",
    # )
    # elif cmd == "addref":
    #     print(pull_n_option(options, 0))
