#!/bin/bash
#PBS -S /bin/bash
#PBS -l nodes=1:ppn=1:%cluster_server/
#PBS -q %cluster_server/
#PBS -N BatchCorrection
#PBS -j eo
#PBS -m ae
#PBS -e %logpath/

if [ -e "$HOME/.bashrc" ]; then
    source "$HOME/.bashrc"
fi
if [ -e "$HOME/.zshrc" ]; then
    zsh "$HOME/.zshrc"
fi
raw_matrix_path="%raw_matrix_path/"
%py_path/ "%exec_root//template/hook/py/batch_correlation.py" $raw_matrix_path %output_doublet_path/