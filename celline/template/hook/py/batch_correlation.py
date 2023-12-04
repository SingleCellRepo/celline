import os
import sys

import scanpy
import scgen
import scipy
import scipy.io as sio
from scvi.data import setup_anndata

h5ad_path: str = sys.argv[1]
output_dir: str = sys.argv[2]

adata = scanpy.read_h5ad(h5ad_path)
os.makedirs(f"{output_dir}/cache", exist_ok=True)
setup_anndata(adata, batch_key="project", labels_key="scpred_prediction")
model = scgen.SCGEN(adata)
model.save(f"{output_dir}/cache/model_perturbation_prediction.pt", overwrite=True)
model.train(
    max_epochs=100, batch_size=32, early_stopping=True, early_stopping_patience=25
)
model.save(f"{output_dir}/cache/model_perturbation_prediction.pt", overwrite=True)
corrected_adata = model.batch_removal()
os.makedirs(output_dir, exist_ok=True)
if not scipy.sparse.issparse(corrected_adata.X):
    matrix = scipy.sparse.csr_matrix(corrected_adata.X)
    sio.mmwrite(f"{output_dir}/corrected.mtx", matrix, field="real", precision=3)
else:
    sio.mmwrite(
        f"{output_dir}/corrected.mtx", corrected_adata.X, field="real", precision=3
    )
