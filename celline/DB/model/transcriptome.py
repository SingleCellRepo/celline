import os
from typing import NamedTuple, Type
from celline.DB.dev.model import BaseModel, Primary
from pprint import pprint


class Transcriptome(BaseModel):
    class Schema(NamedTuple):
        species: Primary[str]
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
    def add_path(cls, species: str, built_path: str, force_update=True):
        obj = Transcriptome()
        if not os.path.isdir(built_path):
            print(f"Built_path does not exist. {built_path}")
        if (cls.search_path(species) is not None) and (not force_update):
            print(f"Transcriptome of {species} is already exists.")
            return
        # pprint(
        #     [
        #         d.species
        #         for d in obj.get(Transcriptome.Schema, lambda d: d.species != "")
        #     ]
        # )
        # TODO: 追加しているはずなのにNot foundになるのなーぜなーぜ？
        obj.add_schema(Transcriptome.Schema(species=species, built_path=built_path))
