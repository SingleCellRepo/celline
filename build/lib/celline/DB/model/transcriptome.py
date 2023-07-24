import os
from typing import NamedTuple, Type
from celline.DB.dev.model import BaseModel


class Transcriptome(BaseModel):
    class Schema(NamedTuple):
        species: str
        built_path: str

    def set_class_name(self) -> str:
        return __class__.__name__

    def set_schema(self) -> Type[Schema]:
        return Transcriptome.Schema

    @classmethod
    def search_path(cls, species: str):
        obj = Transcriptome()
        target = obj.get(Transcriptome.Schema, lambda d: d.species == species)
        if len(target) > 0:
            return target[0].built_path
        return None

    @classmethod
    def add_path(cls, species: str, built_path: str):
        obj = Transcriptome()
        if not os.path.isdir(built_path):
            print(f"If built_path is not exist. {built_path}")
        if cls.search_path(species) is not None:
            print(f"Transcriptome of {species} is already exists.")
            return
        obj.add_schema(Transcriptome.Schema(species=species, built_path=built_path))
