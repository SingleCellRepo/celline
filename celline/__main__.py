import asyncio
import sys
from typing import List

from celline.ncbi.srr import SRR
from celline.tests.test import Test
from celline.utils.config import Config, Setting
from celline.utils.help import Help


def pull_n_option(list_op: List[str], n: int):
    if n >= len(list_op):
        raise IndexError("Invalid option. Please reference celline help")
    return list_op[n]


if __name__ == '__main__':
    Config.initialize(
        exec_root_path=sys.argv[1],
        proj_root_path=sys.argv[2]
    )
    Setting.read()
    cmd = sys.argv[3]
    options = sys.argv[4:]
    if cmd == "add":
        run_id = pull_n_option(options, 0)
        asyncio\
            .get_event_loop()\
            .run_until_complete(
                SRR.add(run_id)
            )
    elif cmd == "dump":
        print("Dumping")
    elif (cmd == "help") | (cmd == "-h"):
        Help.show()
    elif cmd == "test":
        Test.entry()
