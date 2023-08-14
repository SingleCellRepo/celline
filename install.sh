# micromamba config append channels anaconda
# micromamba config append channels conda-forge
# micromamba config append channels bioconda
# micromamba create -n celline python=3.10.0 pandas numba scipy scrublet toml inquirer polars tqdm pysradb varname rich multipledispatch ipykernel jupyter notebook scanpy pyarrow -y
# micromamba activate celline
# pip install PypeR
# python -m ipykernel install --user --name celline --display-name "Python (celline)"
#!/bin/bash

# micromambaをインストールするための関数
install_micromamba() {
    if ! command -v micromamba &>/dev/null; then
        echo "micromambaが見つかりません。インストールを開始します。"
        wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest | tar -xvj bin/micromamba --strip-components=1
        ./micromamba shell init -s "$shell" -p ~/micromamba
        source "$shell_rc_file"
    fi
}

# pyenv.yamlを読み込み、micromambaを使ってパッケージをインストールする関数
install_packages_from_yaml() {
    local yaml_file=$1
    local name version channel

    while IFS=" " read -r key value; do
        case "$key" in
        "- name:") name="$value" ;;
        "version:") version="$value" ;;
        "channel:")
            channel="$value"
            # もし全ての値が読み込まれたらインストールを開始する
            echo "Installing $name=$version from $channel"
            micromamba install "$name=$version" -c "$channel"
            ;;
        esac
    done <"$yaml_file"
}

# スクリプトのメイン部分
main() {
    shell=$(basename "$SHELL")
    shell_rc_file="${HOME}/.${shell}rc"
    source "${shell_rc_file}"

    # install_micromamba
    install_packages_from_yaml "pyenv.yaml"
}

main
