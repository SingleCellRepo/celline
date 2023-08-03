from __future__ import annotations
from typing import List, NamedTuple, Callable, Union, Dict, Optional, Any
import uuid
from functools import partial
import time
from celline.middleware.shell import Shell
import queue
import threading
import subprocess
from celline.server import ServerSystem


class ThreadObservable:
    """
    ## ThreadObservable class handles multiple shell scripts execution using threads.

    Attributes:
        `ObservableShell`: NamedTuple representing a shell script to be observed.

    Note:
        If you are calling this class from Jupyter Notebook, remember to call the `watch` function
        to ensure all the scripts get executed.
    """

    class ObservableShell:
        """
        ## Observable shell which used in thread observable
        """

        script_path: str
        then: Callable[[str], None]
        catch: Callable[[str], None]
        job: Optional[Shell._Job] = None

        def __init__(
            self,
            script_path: str,
            then: Callable[[str], Optional[Any]],
            catch: Callable[[str], Optional[Any]],
        ):
            self.script_path = script_path
            self.then = then
            self.catch = catch
            self.job = None

    _jobs: int = 1
    wait_for_complete: bool = True
    __running_jobs: Dict[str, ObservableShell] = {}
    __queue: queue.Queue = queue.Queue()
    __lock: threading.Lock = threading.Lock()

    @classmethod
    def set_jobs(cls, njobs: int):
        """
        #### Set numbre of jobs
        """
        ThreadObservable._jobs = njobs
        return cls

    @classmethod
    @property
    def njobs(cls) -> int:
        """
        #### Numbre of jobs
        """
        return cls._jobs

    @classmethod
    def call_shell(
        cls,
        shell_ctrl: Union[List[str], List[ObservableShell]],
    ):
        """
        #### Execute shell scripts using threads.

        Args:
            `shell_ctrl<Union[List[str], List[ObservableShell]]>`: List of shell scripts or observable shell objects to be executed.\n
            `job_type<Shell.JobType -optional>`: Type of job execution (single-threaded or multi-threaded). Defaults to Shell.JobType.MultiThreading.
        """

        job_type = ServerSystem.job_system

        def handler(
            _hased_id: str,
            defaultcall: Optional[Callable[[str], None]] = None,
            arg: Optional[str] = None,
        ):
            with cls.__lock:
                if _hased_id in cls.__running_jobs:
                    cls.__running_jobs.pop(_hased_id)
            if defaultcall is not None and arg is not None:
                defaultcall(arg)

        for shell in shell_ctrl:
            hashedid = str(uuid.uuid4())
            if isinstance(shell, str):
                with cls.__lock:
                    cls.__running_jobs[hashedid] = ThreadObservable.ObservableShell(
                        shell,
                        lambda _, h_id=hashedid: handler(h_id),
                        lambda _, h_id=hashedid: handler(h_id),
                    )
                    cls.__queue.put(hashedid)
            else:
                # 'then'と'catch'が存在することを確認する
                if hasattr(shell, "then") and hasattr(shell, "catch"):
                    with cls.__lock:
                        cls.__running_jobs[hashedid] = ThreadObservable.ObservableShell(
                            shell.script_path,
                            lambda out, h_id=hashedid, s=shell: handler(
                                h_id, s.then, out
                            ),
                            lambda err, h_id=hashedid, s=shell: handler(
                                h_id, s.catch, err
                            ),
                        )
                        cls.__queue.put(hashedid)
                else:
                    raise ValueError(
                        "'shell' object must have 'then' and 'catch' attributes"
                    )

        def get_first():
            with cls.__lock:
                if cls.__queue.empty():
                    return None
                first_key = cls.__queue.get()
                first_value = cls.__running_jobs[first_key]
                return first_value

        def thenHandler(output: str, script: ThreadObservable.ObservableShell):
            script.then(output)
            next_script = get_first()
            if next_script is not None:
                Shell.execute(next_script.script_path, job_type).then(
                    partial(thenHandler, script=next_script)
                ).catch(lambda reason: catchHandler(reason, next_script))

        def catchHandler(reason: str, script: ThreadObservable.ObservableShell):
            script.catch(reason)
            next_script = get_first()
            if next_script is not None:
                Shell.execute(next_script.script_path, job_type).then(
                    partial(thenHandler, script=next_script)
                ).catch(lambda reason: catchHandler(reason, next_script))

        # 最初のnjobs個のスクリプトを実行
        for _ in range(min(ThreadObservable._jobs, len(cls.__running_jobs))):
            script = get_first()
            if script is not None:
                script.job = Shell.execute(script.script_path, job_type)
                script.job.then(partial(thenHandler, script=script)).catch(
                    partial(catchHandler, script=script)
                )
        cls.watch()
        return cls

    @classmethod
    def watch(cls):
        """
        #### Watch all running jobs.
        Continues to check until all the jobs are done.
        """
        try:
            # while True:
            while not cls.__queue.empty() or cls.__running_jobs:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(
                "\nKeyboard interrupt received. Attempting to terminate running jobs."
            )
            for hashed_id, observable_shell in cls.__running_jobs.items():
                script = observable_shell.script_path
                job = cls.__running_jobs.get(hashed_id, None)
                if job:
                    # if the job is running under PBS system
                    if job.job is not None:
                        if (
                            job.job.job_system == ServerSystem.JobType.PBS
                            and job.job.job_id
                        ):
                            with subprocess.Popen(
                                f"qdel {job.job.job_id}",
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                            ) as p:
                                p.wait()
                            print(f"├─ Terminating PBS job: {job.job.job_id}")
                        else:
                            # if the job is not under PBS, we simply terminate it
                            job.job.process.terminate()
                            print(f"├─ Terminating shell script: {script}")
            print("└─ Exit.")
        return cls

    @classmethod
    def wait(cls):
        """
        #### Wait for the currently running jobs to finish.
        Continues to check until the number of running jobs is less than `_jobs`.
        """
        try:
            while len(cls.__running_jobs) >= cls._jobs:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(
                "\nKeyboard interrupt received. Attempting to terminate running jobs."
            )
            for hashed_id, observable_shell in cls.__running_jobs.items():
                script = observable_shell.script_path
                job = cls.__running_jobs.get(hashed_id, None)
                if job:
                    # if the job is running under PBS system
                    if job.job is not None:
                        if (
                            job.job.job_system == ServerSystem.JobType.PBS
                            and job.job.job_id
                        ):
                            with subprocess.Popen(
                                f"qdel {job.job.job_id}",
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                            ) as p:
                                p.wait()
                            print(f"├─ Terminating PBS job: {job.job.job_id}")
                        else:
                            # if the job is not under PBS, we simply terminate it
                            job.job.process.terminate()
                            print(f"├─ Terminating shell script: {script}")
            print("└─ Exit.")
        return cls
