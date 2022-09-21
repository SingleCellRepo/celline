#!/bin/bash

## Target exec directory
read -e -p "Installation target directory? " install_dir
if [ -z "$install_dir" ]; then
    echo "Cannot install to empty directory"
    exit 1
fi
install_dir=$(cd "$(dirname "$install_dir")" && pwd)/$(basename "$install_dir")
if ! [[ -d $install_dir ]]; then
    echo "Could not find directory: $install_dir"
    exit 1
fi

install_dir="${install_dir}/celline"
rm -rf "${install_dir}"

declare -a arr=("test1" "test2" "test3")
bash ./multi_selection.sh "${arr[*]}"
result=$(cat "./sel_res.txt")
rm "./sel_res.txt"
echo "${result[@]}"
