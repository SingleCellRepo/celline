from argparse import ArgumentParser
from typing import Any, Dict, List, Union

from celline.utils.exceptions import InvalidJobException
from celline.utils.typing import NullableString


class ThreadRunner:
    def __init__(self, options: List[str], argparser: ArgumentParser) -> None:
        argparser.add_argument("-n", "--nthread", type=int)
        self.nthread: int = argparser.parse_args(
            options).nthread
        pass
