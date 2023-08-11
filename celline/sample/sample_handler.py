import os

from typing import Final, Dict

from celline.config import Config

import toml
class SampleResolver:
    __samples: Dict[str, str] = {}
    __called = False

    @classmethod
    @property
    def samples(cls):
        SAMPLE_PATH: Final[str] = f"{Config.PROJ_ROOT}/samples.toml"
        if not cls.__called and os.path.isfile(SAMPLE_PATH):
            with open(SAMPLE_PATH, mode="r", encoding="utf-8") as f:
                cls.__samples = toml.load(f)
            cls.__called = True
        return cls.__samples