#!/bin/bash -f
#PBS -S /bin/bash
#PBS -l nodes=1:ppn=<nthread>:<cluster_server>
#PBS -q <cluster_server>
#PBS -N <jobname>
#PBS -j eo
#PBS -m ae
#PBS -e <logpath>

## Check command ##
source "$HOME/.bashrc"
commands=("cellranger")
for command in "${commands[@]}"; do
  if command -v "$command" >/dev/null 2>&1; then
    echo "[CHECK] $command: Resolved."
  else
    echo "[CHECK] $command: Could not resolve."
    exit 1
  fi
done
##################

cd <dist_dir>
rm -rf "./counted"
cellranger count\
    --id=counted \
    --fastqs=<fq_path> \
    --sample=<sample_id> \
    --transcriptome=<transcriptome> \
    --no-bam --localcores <nthread>