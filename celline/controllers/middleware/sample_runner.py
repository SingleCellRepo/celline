from argparse import ArgumentParser
from typing import Any, Dict, List, Union

from celline.utils.exceptions import InvalidJobException
from celline.utils.typing import NullableString


class SampleRunner:
    def __init__(self, options: List[str], argparser: ArgumentParser) -> None:
        argparser.add_argument("-s", "--samplename", type=str)
        self.default_sample_name: NullableString = argparser.parse_args(
            options).samplename
        pass
