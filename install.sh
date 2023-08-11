#!/bin/zsh
micromamba config append channels anaconda
micromamba config append channels conda-forge
micromamba config append channels bioconda
micromamba create -n celline python=3.10.0 pandas numba scipy scrublet toml inquirer polars tqdm pysradb varname rich multipledispatch ipykernel jupyter notebook scanpy pyarrow -y
micromamba activate celline
pip install PypeR
python -m ipykernel install --user --name celline --display-name "Python (celline)"
