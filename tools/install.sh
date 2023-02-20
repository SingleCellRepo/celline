#!/bin/bash

abspath() {
  case $2 in
    /*) set -- "$1" "$2/" "" ;;
    *) set -- "$1" "${3:-$PWD}/$2/" ""
  esac

  while [ "$2" ]; do
    case ${2%%/*} in
      "" | .) set -- "$1" "${2#*/}" "$3" ;;
      ..) set -- "$1" "${2#*/}" "${3%/*}" ;;
      *) set -- "$1" "${2#*/}" "$3/${2%%/*}"
    esac
  done
  eval "$1=\"/\${3#/}\""
}

relpath() {
  set -- "$1" "$2" "${3:-$PWD}"
  abspath "$@"
  eval "set -- \"\$1\" \"\${$1}\" \"\$3\""
  abspath "$1" "$3"
  eval "set -- \"\$1\" \"\$2\" \"\${$1}\" \"\""

  [ _"$2" = _"$3" ] && eval "$1=./" && return 0

  while [ "$3" ]; do
    eval "$1=\$3 && [ ! \"\$2\" = \"\${2#\"\${$1}\"}\" ]" && break
    set -- "$1" "$2" "${3%/*}" "../$4"
  done

  eval "$1=\$3/ && $1=\$4\${2#\"\${$1}\"}"
}

current_path="$(pwd)"
install_py_path="$(pwd)/tools/install.py"

read -e -p "Installation target directory? " install_dir
abspath abs_install_dir ${install_dir/"~"/$HOME}
echo "Install from: $current_path"
echo "Install to: $abs_install_dir"
mkdir -p "$abs_install_dir/celline" & cd "$abs_install_dir/celline"
# poetry env use "$(which python)"
# python -m venv .venv
# echo "instaling poetry"
pip install inquirer
pip install tqdm
python "${install_py_path}" "${current_path}" "$abs_install_dir" "$HOME"
