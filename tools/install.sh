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

read -e -p "Installation target directory? " install_dir
abspath abs_install_dir ${install_dir/"~"/$HOME}
echo "Install to: $abs_install_dir"
echo "using $(which python)"
mkdir -p "$abs_install_dir/celline" & cd "$abs_install_dir/celline"
poetry env use "$(which python)"
python -m venv .venv
echo "instaling poetry"
pip install inquirer
pip install tqdm
poetry run python tools/install.py "$(pwd)" "$abs_install_dir" "$HOME"
