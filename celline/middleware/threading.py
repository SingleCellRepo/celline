from __future__ import annotations
from typing import List, NamedTuple, Callable, Union, Dict, Optional
import uuid
from functools import partial
import time
from celline.middleware.shell import Shell
import queue
import threading


class ThreadObservable:
    """
    ## ThreadObservable class handles multiple shell scripts execution using threads.

    Attributes:
        `ObservableShell`: NamedTuple representing a shell script to be observed.

    Note:
        If you are calling this class from Jupyter Notebook, remember to call the `watch` function
        to ensure all the scripts get executed.
    """

    class ObservableShell(NamedTuple):
        """
        ## Observable shell which used in thread observable
        """

        script_path: str
        then: Callable[[str], None]
        catch: Callable[[str], None]

    _nthread: int = 1
    wait_for_complete: bool = True
    __running_jobs: Dict[str, ObservableShell] = {}
    __queue: queue.Queue = queue.Queue()
    __lock: threading.Lock = threading.Lock()

    @classmethod
    def set_nthread(cls, nthread: int):
        """
        #### Set numbre of thread
        """
        ThreadObservable._nthread = nthread
        return cls

    @classmethod
    @property
    def nthread(cls) -> int:
        """
        #### Numbre of thread
        """
        return cls._nthread

    @classmethod
    def call_shell(
        cls,
        shell_ctrl: Union[List[str], List[ObservableShell]],
        job_type: Shell.JobType = Shell.JobType.MultiThreading,
    ):
        """
        #### Execute shell scripts using threads.

        Args:
            `shell_ctrl<Union[List[str], List[ObservableShell]]>`: List of shell scripts or observable shell objects to be executed.\n
            `job_type<Shell.JobType -optional>`: Type of job execution (single-threaded or multi-threaded). Defaults to Shell.JobType.MultiThreading.
        """

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

        # 最初のnthread個のスクリプトを実行
        for _ in range(min(ThreadObservable._nthread, len(cls.__running_jobs))):
            script = get_first()
            if script is not None:
                Shell.execute(script.script_path, job_type).then(
                    partial(thenHandler, script=script)
                ).catch(partial(catchHandler, script=script))
        return cls

    @classmethod
    def watch(cls):
        """
        #### Watch and print all running jobs.
        Continues to check until all the jobs are done.
        """
        try:
            while not cls.__queue.empty() or cls.__running_jobs:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Ctrl+Cが押されました。プログラムを終了します。")
        return cls
