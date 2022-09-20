from enum import Enum
import os
import re
from typing import Any, Dict


class Jobs:
    @staticmethod
    def build(template_path: str, replace_params: Dict[str, Any]):
        """
        Build job script
        """
        if not os.path.isfile(template_path):
            raise FileNotFoundError(
                f"Could not find template file: {template_path}")
        target_sh = []
        with open(template_path, mode="r") as template:
            for line in template.readlines():
                for param in replace_params:
                    line = re.sub(
                        f'@{param}@', f"{replace_params[param]}", line, 10)
                target_sh.append(line)
        return str("\n".join(target_sh))


class JobSystem(Enum):
    default_bash = 1
    nohup = 2
    PBS = 3
