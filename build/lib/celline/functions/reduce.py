from typing import TYPE_CHECKING, Optional, Callable, Final, Dict, List, NamedTuple
import subprocess
import rich
import os

from celline.functions._base import CellineFunction
from celline.resources import Resources
from celline.template import TemplateManager
from celline.server import ServerSystem
from celline.config import Setting, Config
from celline.middleware import ThreadObservable
from rich.progress import track

if TYPE_CHECKING:
    from celline import Project


class Reduce(CellineFunction):
    FILES_TO_KEEP: Final = [
        "outs/filtered_feature_bc_matrix.h5",
        "outs/molecule_info.h5",
        "outs/web_summary.html",
        "_log",
        "outs/filtered_feature_bc_matrix/matrix.mtx.gz",
        "outs/filtered_feature_bc_matrix/features.tsv.gz",
        "outs/filtered_feature_bc_matrix/barcodes.tsv.gz",
    ]

    def call(self, project: "Project"):
        for sample in track(
            Resources.all_samples(),
            description="Processing reducing files...",
        ):
            target_path = sample.path.resources_sample_counted
            if os.path.exists(target_path):
                for foldername, subfolders, filenames in os.walk(
                    target_path, topdown=False
                ):
                    for filename in filenames:
                        rel_path = os.path.relpath(
                            os.path.join(foldername, filename), target_path
                        )
                        if rel_path not in Reduce.FILES_TO_KEEP:
                            os.remove(os.path.join(foldername, filename))
                    for subfolder in subfolders:
                        full_subfolder_path = os.path.join(foldername, subfolder)
                        if not os.listdir(
                            full_subfolder_path
                        ):  # Check if directory is empty
                            os.rmdir(full_subfolder_path)
        return project
