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

function write_alias() {
    if [ "$SHELL" = "/usr/bin/bash" ] || [ "$SHELL" = "/bin/bash" ]; then
        if grep "source ~/.sc_alias" ~/.bashrc >/dev/null; then
            echo ">> alias skipped".
        else
            echo 'source ~/.sc_alias' >>~/.bashrc
        fi
    elif [ "$SHELL" = "/usr/bin/zsh" ] || [ "$SHELL" = "/bin/zsh" ]; then
        if grep "source ~/.sc_alias" ~/.zshrc >/dev/null; then
            echo ">> alias skipped".
        else
            echo 'source ~/.sc_alias' >>~/.zshrc
        fi
    else
        echo "Unrecognized shell ($SHELL)."
        echo "Please write 'source ~/.sc_alias' to your startup script."
    fi
}

write_alias
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
echo "Installing..."
rsync -ah "${source_loc}" "${install_dir}" --exclude '__pycache__/' --exclude '.git/' --exclude 'test/' --exclude '.vscode/' --exclude '*.ipynb' --exclude '.mypy_cache/' --exclude 'README.md' --exclude 'tools/'

echo "export PATH="\""$install_dir"/celline/bin:'$PATH"' >~/.sc_alias
chmod +x "$install_dir/celline/bin/celline"
chmod +x "$install_dir/celline/bin/scfastq-dump"
###############################

## Variables
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
fi

### TODO Write mouse ref genome
echo "${result[@]}" | xargs -n 1 | grep -E "^MouseReferenceGenome$" >/dev/null
if [ $? -eq 0 ]; then
    cd "${install_dir}/genomes" || exit
    wget https://cf.10xgenomics.com/supp/cell-exp/refdata-gex-mm10-2020-A.tar.gz -O "${install_dir}/genomes/refdata-gex-mm10-2020-A.tar.gz"
    tar -zxvf refdata-gex-mm10-2020-A.tar.gz
    rm refdata-gex-mm10-2020-A.tar.gz
    cd "${install_dir}/celline" || exit
fi

echo "${result[@]}" | xargs -n 1 | grep -E "^PoetryRequirement$" >/dev/null
if [ $? -eq 0 ]; then
    curl -sSL https://install.python-poetry.org | python3 -
fi

echo "${result[@]}" | xargs -n 1 | grep -E "^SRAtoolkit$" >/dev/null
if [ $? -eq 0 ]; then
    mkdir -p "${sratoolpath}"
    cd ${sratoolpath} || exit
    wget https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/3.0.0/sratoolkit.3.0.0-centos_linux64.tar.gz
    tar -zxvf sratoolkit.3.0.0-centos_linux64.tar.gz
    rm sratoolkit.3.0.0-centos_linux64.tar.gz
    echo "export PATH="\""${sratoolpath}"/sratoolkit.3.0.0-centos_linux64/bin:'$PATH"' >>~/.sc_alias
fi

cd "${install_dir}/celline" || exit
echo "using $(which python)"
poetry env use "$(which python)"
python -m venv .venv
poetry install
cd "${install_dir}/celline" || exit
poetry run python celline/initializer/initialize.py static addref "${install_dir}/celline" "Homosapiens" "${install_dir}/genomes/refdata-gex-GRCh38-2020-A"
poetry run python celline/initializer/initialize.py static addref "${install_dir}/celline" "Musmusculus" "${install_dir}/genomes/refdata-gex-mm10-2020-A"

echo "Successful to install"
