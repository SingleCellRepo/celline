from typing import (
    List,
    Dict,
    TypeVar,
    Generic,
    Final,
    Type,
    NamedTuple,
    get_type_hints,
    Callable,
)
from celline.utils.exceptions import NullPointException
import polars as pl

# from celline.config import Config
from abc import ABCMeta, abstractmethod
from celline.utils.serialization import serialize, deserialize
import os
import yaml


class BaseRelation(metaclass=ABCMeta):
    class Schema(NamedTuple):
        notoverrided: str

    __schema: Schema

    def __init__(self) -> None:
        self.__class_name = self.set_class_name()
        self.schema = self.set_schema()
        self.EXEC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.PATH = f"{self.EXEC_ROOT}/DB/{self.__class_name}.yaml"
        if os.path.isfile(self.PATH):
            with open(self.PATH, mode="r") as f:
                self.__schema = deserialize(yaml.safe_load(f), BaseRelation.Schema)
            self.df = pl.read_parquet(self.PATH)
        self.__schema = 

    @abstractmethod
    def set_class_name(self) -> str:
        return __class__.__name__

    @abstractmethod
    def set_schema(self) -> Type[Schema]:
        return BaseModel.Schema

    def flush(self):
        return self
