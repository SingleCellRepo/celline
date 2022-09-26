#!/bin/bash
realpath() {
    f=$@
    if [ -d "$f" ]; then
        base=""
        dir="$f"
    else
        base="/$(basename "$f")"
        dir=$(dirname "$f")
    fi
    dir=$(cd "$dir" && /bin/pwd)
    echo "$dir$base"
}

## Target exec directory
read -e -p "Installation target directory? " install_dir
if [ -z "$install_dir" ]; then
    echo "Cannot install to empty directory"
    exit 1
fi
install_dir=$(realpath "$install_dir")
if ! [[ -d $install_dir ]]; then
    echo "Could not find directory: $install_dir"
    exit 1
fi

## Install
echo "Cleaning up..."

rm -rf "${install_dir}/celline"
source_loc=$(dirname "$(
    cd "$(dirname "$0")" || exit
    pwd
)")
echo "Instaling..."
rsync -ah "${source_loc}" "${install_dir}" --exclude '__pycache__/' --exclude '.git/' --exclude 'test/' --exclude '.vscode/' --exclude '*.ipynb' --exclude '.mypy_cache/' --exclude 'README.md' --exclude 'tools/'
###############################

## Variables
declare INSTALL_POETRY=true
declare -a selection=()

## Ref genome installation
mkdir -p "${install_dir}/genomes"
if ! [[ -d "${install_dir}/genomes/refdata-gex-GRCh38-2020-A" ]]; then
    selection+=("HumanReferenceGenome")
fi
if ! [[ -d "${install_dir}/genomes/refdata-gex-mm10-2020-A" ]]; then
    selection+=("MouseReferenceGenome")
fi
if ! [[ -d "${install_dir}/SRA" ]]; then
    selection+=("SRAtoolkit")
fi
selection+=("PoetryRequirement")
bash "${source_loc}/tools/multi_selection.sh" "${selection[*]}"
result=$(cat "./sel_res.txt")
rm "./sel_res.txt"

cd "${install_dir}/celline" || exit

echo "${result[@]}" | xargs -n 1 | grep -E "^HumanReferenceGenome$" >/dev/null
if [ $? -eq 0 ]; then
    cd "${install_dir}/genomes" || exit
    wget https://cf.10xgenomics.com/supp/cell-exp/refdata-gex-GRCh38-2020-A.tar.gz -O "${install_dir}/genomes/refdata-gex-GRCh38-2020-A.tar.gz"
    tar -zxvf refdata-gex-GRCh38-2020-A.tar.gz
    rm refdata-gex-GRCh38-2020-A.tar.gz
    cd "${install_dir}/celline" || exit
    poetry addref "Homosapiens" "${install_dir}/genomes/refdata-gex-GRCh38-2020-A"
fi

### TODO Write mouse ref genome
echo "${result[@]}" | xargs -n 1 | grep -E "^MouseReferenceGenome$" >/dev/null
if [ $? -eq 0 ]; then
    cd "${install_dir}/genomes" || exit
    wget https://cf.10xgenomics.com/supp/cell-exp/refdata-gex-GRCh38-2020-A.tar.gz -O "${install_dir}/genomes/refdata-gex-GRCh38-2020-A.tar.gz"
    tar -zxvf refdata-gex-GRCh38-2020-A.tar.gz
    rm refdata-gex-GRCh38-2020-A.tar.gz
    cd "${install_dir}/celline" || exit
    poetry addref "Musmusculus" "${install_dir}/genomes/refdata-gex-GRCh38-2020-A"
fi

echo "${result[@]}" | xargs -n 1 | grep -E "^PoetryRequirement$" >/dev/null
if [ $? -eq 0 ]; then
    curl -sSL https://install.python-poetry.org | python3 -
    poetry install
fi

echo "Successful to install"
