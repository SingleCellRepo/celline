import os
from typing import NamedTuple, Type, Optional
from celline.DB.dev.model import BaseModel, Primary
from pprint import pprint


class Transcriptome(BaseModel):
    class Schema(NamedTuple):
        species: Primary[str]
        built_path: str

    def set_class_name(self) -> str:
        return __class__.__name__

    def def_schema(self) -> Type[Schema]:
        return Transcriptome.Schema

    def search(self, acceptable_id: str, force_search=False) -> Optional[str]:
        target = self.get(Transcriptome.Schema, lambda d: d.species == acceptable_id)
        if len(target) > 0:
            return target[0].built_path
        return None


    def add_path(self, species: str, built_path: str, force_update=True):
        obj = Transcriptome()
        if not os.path.isdir(built_path):
            print(f"Built_path does not exist. {built_path}")
        if (self.search(species) is not None) and (not force_update):
            print(f"Transcriptome of {species} is already exists.")
            return
        obj.add_schema(Transcriptome.Schema(species=species, built_path=built_path))
