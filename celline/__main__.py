import sys
from celline.config import Config, Setting
from celline.app.functions import FunctionManager

if __name__ == "__main__":
    cmd = sys.argv[3]
    options = sys.argv[4:]
    Config.initialize(exec_root_path=sys.argv[1], proj_root_path=sys.argv[2])
    Setting.initialize()
    # Genome.initialize()
    FunctionManager.call(sys.argv[3:])
