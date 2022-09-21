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

echo "Installing..."

rm -rf "${install_dir}/celline"
source_loc=$(dirname "$(
    cd "$(dirname "$0")" || exit
    pwd
)")
# cd "${source_loc}" || exit
rsync -ah "${source_loc}" "${install_dir}" --exclude '__pycache__/' --exclude '.git/' --exclude 'test/' --exclude '.vscode/' --exclude '*.ipynb' --exclude '.mypy_cache/' --exclude 'README.md' --exclude 'tools/'

# declare -a arr=("test1" "test2" "test3")
# bash ./multi_selection.sh "${arr[*]}"
# result=$(cat "./sel_res.txt")
# rm "./sel_res.txt"
# echo "${result[@]}"
