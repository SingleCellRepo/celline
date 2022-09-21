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
if hash poetry 2>/dev/null; then
    INSTALL_POETRY=false
fi

bash "${source_loc}/tools/multi_selection.sh" "${selection[*]}"
result=$(cat "./sel_res.txt")
rm "./sel_res.txt"

echo "${result[@]}" | xargs -n 1 | grep -E "^HumanReferenceGenome$" >/dev/null
if [ $? -eq 0 ]; then
    cd "${install_dir}/genomes" || exit
    wget https://cf.10xgenomics.com/supp/cell-exp/refdata-gex-GRCh38-2020-A.tar.gz -O "${install_dir}/genomes/refdata-gex-GRCh38-2020-A.tar.gz"
    tar -zxvf sratoolkit.3.0.0-centos_linux64.tar.gz
    rm sratoolkit.3.0.0-centos_linux64.tar.gz
else
    echo " does not exist."
fi

# echo "${result[@]}"
# if [ $INSTALL_POETRY ]; then
#     curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
# fi

####################
# declare -a arr=("test1" "test2" "test3")
# bash ./multi_selection.sh "${arr[*]}"
# result=$(cat "./sel_res.txt")
# rm "./sel_res.txt"
# echo "${result[@]}"
