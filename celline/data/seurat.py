import os

from typing import Optional

import pyper as pr
import pandas as pd
import polars as pl
import numpy as np


from celline.config import Setting, Config
from celline.data.ggplot import ggplot
from celline.utils.r_wrap import as_r_bool, as_r_NULL, as_r_nullablestr


class Seurat:
    r: pr.R

    def __init__(self, seurat_path: str, via_seurat_disk: bool) -> None:
        if not os.path.isfile(seurat_path):
            raise FileNotFoundError(
                f"Could not find seurat file: {seurat_path}. Please try consider identifier (file name), or using seurat_from_rawpath"
            )
        print(f"Using R: {Setting.r_path}")
        self.r = pr.R(RCMD=Setting.r_path, use_pandas=True)
        self.r.assign("h5seurat_path", f"{seurat_path}")
        # log = r.run(f'source("{Config.EXEC_ROOT}/celline/data/hook/loadSeurat.R"')
        self.r("pacman::p_load(Seurat, SeuratDisk, tidyverse)")
        print("Loading seurat")
        if via_seurat_disk:
            self.r("seurat <- SeuratDisk::LoadH5Seurat(h5seurat_path)")
        else:
            self.r("seurat <- readRDS(h5seurat_path)")
        print("--> Done!")

    @property
    def metadata(self) -> pl.DataFrame:
        _metadata = pd.DataFrame(
            self.r.get('seurat@meta.data %>% tibble::rownames_to_column("cell")')
        )
        for col in _metadata.columns:
            if _metadata[col].apply(lambda x: isinstance(x, bytes)).any():
                _metadata[col] = _metadata[col].str.decode("utf-8")
        return pl.from_pandas(_metadata.convert_dtypes())

    def DimPlot(
        self,
        group_by: Optional[str] = "seurat_clusters",
        split_by: Optional[str] = None,
        pt_size: Optional[int] = None,
    ):
        if group_by is None:
            group_by = "NULL"
        if split_by is None:
            split_by = "NULL"

        log = self.r(
            f'plt <- DimPlot(seurat, group.by = "{group_by}", split.by = {as_r_nullablestr(split_by)}, pt.size = {as_r_NULL(pt_size)})'
        )
        print(log[1:])
        return ggplot(self.r)
