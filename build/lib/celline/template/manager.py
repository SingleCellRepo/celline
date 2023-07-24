from typing import NamedTuple
import re


class TemplateManager:
    @staticmethod
    def replace_from_file(file_path: str, structure: NamedTuple, replaced_path: str):
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()

        for field in structure._fields:
            data = re.sub(f"<{field}>", getattr(structure, field), data)

        with open(replaced_path, "w", encoding="utf-8") as file:
            file.write(data)
