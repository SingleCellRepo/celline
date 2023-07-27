#!/bin/bash -f
#PBS -S /bin/bash
#PBS -l nodes=1:ppn=1:<cluster_server>
#PBS -q <cluster_server>
#PBS -N <jobname>
#PBS -j eo
#PBS -m ae
#PBS -e <logpath>

source "$HOME/.bashrc"
raw_matrix_path=<raw_matrix_path>
<py_path> "<exec_root>/template/hook/py/preprocess_scrublet.py" $raw_matrix_path <output_doublet_path>
<r_path> "<exec_root>/template/hook/R/FilterGenes.R" $raw_matrix_path <output_qc_path> <log_path>