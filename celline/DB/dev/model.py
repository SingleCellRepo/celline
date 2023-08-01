from __future__ import annotations
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
    Optional,
    get_origin,
    get_args,
)
from celline.utils.exceptions import NullPointException
import polars as pl

# from celline.config import Config
from abc import ABCMeta, abstractmethod
import os

from pprint import pprint
from polars import Expr

## Type vars #############
T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")
T8 = TypeVar("T8")
##########################


class Primary(Generic[T]):
    """As primary key"""

    def __init__(self, value: T = None):
        self._value = value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._value

    def __set__(self, instance, value: T):
        instance.__dict__[self] = value


class MultiplePrimaryKeysError(Exception):
    pass


class NoPrimaryKeyError(Exception):
    pass


class BaseModel(metaclass=ABCMeta):
    class Schema(NamedTuple):
        notoverrided: str

    df: pl.DataFrame
    __class_name: str = ""
    schema: Type[Schema]
    PATH: Final[str]
    EXEC_ROOT: Final[str]

    def __init__(self) -> None:
        # if (self.__class_name == "") | (self.schema == DBBase.Scheme.notoverrided):
        #     raise LookupError(
        #         "Please override __class_name and schema variable in your custom DB."
        #     )
        self.__class_name = self.set_class_name()
        self.schema = self.set_schema()
        self.EXEC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.PATH = f"{self.EXEC_ROOT}/DB/{self.__class_name}.parquet"
        if os.path.isfile(self.PATH):
            self.df = pl.read_parquet(self.PATH)
        else:
            self.df = pl.DataFrame(
                {},
                schema={name: t for name, t in get_type_hints(self.Schema).items()},
            )
            self.df.write_parquet(self.PATH)

    @abstractmethod
    def set_class_name(self) -> str:
        return __class__.__name__

    @abstractmethod
    def set_schema(self) -> Type[Schema]:
        return BaseModel.Schema

    # @overload
    # def get(
    #     self,
    #     col1: T1,
    #     col2: T2,
    #     col3: T3,
    #     col4: T4,
    #     col5: T5,
    #     col6: T6,
    #     col7: T7,
    #     col8: T8,
    # ) -> Tuple[
    #     List[T1], List[T2], List[T3], List[T4], List[T5], List[T6], List[T7], List[T8]
    # ]:
    #     ...

    # def get(
    #     self,
    #     col1: T1,
    #     col2: Optional[T2] = None,
    #     col3: Optional[T3] = None,
    #     col4: Optional[T4] = None,
    #     col5: Optional[T5] = None,
    #     col6: Optional[T6] = None,
    #     col7: Optional[T7] = None,
    #     col8: Optional[T8] = None,
    # ) -> Tuple[
    #     Optional[List[T1]],
    #     Optional[List[T2]],
    #     Optional[List[T3]],
    #     Optional[List[T4]],
    #     Optional[List[T5]],
    #     Optional[List[T6]],
    #     Optional[List[T7]],
    #     Optional[List[T8]],
    # ]:
    #     t1: Optional[List[T1]] = None
    #     t2: Optional[List[T2]] = None
    #     t3: Optional[List[T3]] = None
    #     t4: Optional[List[T4]] = None
    #     t5: Optional[List[T5]] = None
    #     t6: Optional[List[T6]] = None
    #     t7: Optional[List[T7]] = None
    #     t8: Optional[List[T8]] = None
    #     for name in self.schema._fields:
    #         if getattr(self.schema, name) == col1:
    #             t1 = self.df.get_column(name).to_list()
    #         if getattr(self.schema, name) == col2:
    #             t2 = self.df.get_column(name).to_list()
    #         if getattr(self.schema, name) == col3:
    #             t3 = self.df.get_column(name).to_list()
    #         if getattr(self.schema, name) == col4:
    #             t4 = self.df.get_column(name).to_list()
    #         if getattr(self.schema, name) == col5:
    #             t5 = self.df.get_column(name).to_list()
    #         if getattr(self.schema, name) == col6:
    #             t6 = self.df.get_column(name).to_list()
    #         if getattr(self.schema, name) == col7:
    #             t7 = self.df.get_column(name).to_list()
    #         if getattr(self.schema, name) == col8:
    #             t8 = self.df.get_column(name).to_list()
    #     return (
    #         t1,
    #         t2,
    #         t3,
    #         t4,
    #         t5,
    #         t6,
    #         t7,
    #         t8,
    #     )

    def as_schema(
        self, schema_def: Type[T], df: Optional[pl.DataFrame] = None
    ) -> List[T]:
        if df is None:
            df = self.df

        type_hints = get_type_hints(schema_def)

        data = df.to_pandas().itertuples(index=False)
        return [
            schema_def(
                *(
                    Primary(val) if get_origin(type_hint) is Primary else val
                    for val, type_hint in zip(t, type_hints.values())
                )
            )
            for t in data
        ]

    def get(self, target_schema: Type[T], filter_func: Callable[[T], bool]) -> List[T]:
        type_hints = get_type_hints(target_schema)

        data = self.df.to_pandas().itertuples(index=False)
        result: List[T] = []
        for schema_each in [
            target_schema(
                *(
                    val if get_origin(type_hint) is Primary else val
                    for val, type_hint in zip(t, type_hints.values())
                )
            )
            for t in data
        ]:
            if filter_func(schema_each):
                result.append(schema_each)
        return result
        # tname = ""
        # for name in self.schema._fields:
        #     if getattr(self.schema, name) == filter_col:
        #         tname = name
        #         break
        # if tname == "":
        #     raise NullPointException(
        #         "Plptr is unknown. Please designate ***.Scheme.***"
        #     )
        # target_column: List = []
        # for column in self.df.get_column(tname).to_list():
        #     if filter_func(column):
        #         target_column.append(column)
        # # target_df = self.df.filter(pl.col(tname).is_in(target_column))
        # # self.schema(target_df)
        # return [
        #     self.schema(*row)
        #     for row in self.df.filter(pl.col(tname).is_in(target_column))
        #     .to_pandas()
        #     .itertuples(index=False)
        # ]  # type: ignore

    def plptr(self, col) -> pl.Expr:
        """Returns a pointer to the column that applies to col."""
        tname = ""
        for name in self.schema._fields:
            if getattr(self.schema, name) == col:
                tname = name
                break
        if tname == "":
            raise NullPointException(
                "Plptr is unknown. Please designate ***.Scheme.***"
            )
        return pl.col(tname)

    def as_dataframe(self, schema_instance: NamedTuple) -> pl.DataFrame:
        type_hints = get_type_hints(schema_instance)
        for field, type_hint in type_hints.items():
            if get_origin(type_hint) is Primary:
                type_hints[field] = get_args(type_hint)[0]  # Replace Primary[T] with T

        return pl.DataFrame(
            {
                field: [getattr(schema_instance, field)]
                for field in schema_instance._fields
            },
            schema=type_hints,
        )

    # def add_schema(self, schema_instance: NamedTuple):
    #     newdata = self.as_dataframe(schema_instance)
    #     self.df = pl.concat([self.df, newdata])
    #     self.flush()
    #     return self.as_schema(self.schema, newdata)[0]

    def add_schema(self, schema_instance: NamedTuple, force_update: bool = True):
        primary_fields = [
            field
            for field in schema_instance._fields
            if get_origin(get_type_hints(schema_instance)[field]) is Primary
        ]
        if not primary_fields:
            raise NoPrimaryKeyError("No primary key found.")

        if len(primary_fields) > 1:
            raise MultiplePrimaryKeysError("Multiple primary keys found.")

        mask: Expr = pl.lit(True)
        if force_update:
            for primary_field in primary_fields:
                primary_val = getattr(schema_instance, primary_field)
                mask &= pl.col(primary_field) == primary_val

            if self.df.filter(mask).shape[0] > 0:
                self.df = self.df.filter(~mask)

        newdata = self.as_dataframe(schema_instance)
        self.df = pl.concat([self.df, newdata])
        self.flush()
        return self.as_schema(self.schema, newdata)[0]

    @property
    def type_schema(self) -> Dict[str, type]:
        return get_type_hints(self.schema)

    def flush(self):
        self.df.write_parquet(f"{self.EXEC_ROOT}/DB/{self.__class_name}.parquet")

    @property
    def stored(self) -> pl.DataFrame:
        return self.df


class Ref(Generic[T2]):
    """Set Reference"""
