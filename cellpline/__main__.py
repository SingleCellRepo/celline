import sys
from cellpline.ncbi.srr import SRR
from cellpline.utils.help import Help
from cellpline.tests.test import Test
from cellpline.utils.config import Config, Setting


if __name__ == '__main__':
    Config.initialize(
        exec_root_path=sys.argv[1],
        proj_root_path=sys.argv[2]
    )
    Setting.read()
    cmd = sys.argv[3]
    options = sys.argv[4:]
    if cmd == "add":
        print("Adding")
    elif cmd == "dump":
        print("Dumping")
    elif cmd == "help":
        Help.show()
    elif cmd == "test":
        Test.entry()
