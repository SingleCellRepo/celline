import scipy.io as sio
import scgen
import scanpy
import sys
import os

from celline.config import Config

h5ad_path: str = sys.argv[1]
output_dir: str = sys.argv[2]

adata = scanpy.read_h5ad(h5ad_path)
os.makedirs(f"{Config.PROJ_ROOT}/cache", exist_ok=True)
scgen.SCGEN.setup_anndata(adata, batch_key="project", labels_key="scpred_prediction")
model = scgen.SCGEN(adata)
model.save(f"{Config.PROJ_ROOT}/cache/model_perturbation_prediction.pt", overwrite=True)
model.train(
    max_epochs=100, batch_size=32, early_stopping=True, early_stopping_patience=25
)
model.save(f"{Config.PROJ_ROOT}/cache/model_perturbation_prediction.pt", overwrite=True)
corrected_adata = model.batch_removal()
os.makedirs(output_dir, exist_ok=True)
sio.mmwrite(f"{output_dir}/corrected.mtx", corrected_adata.X)
