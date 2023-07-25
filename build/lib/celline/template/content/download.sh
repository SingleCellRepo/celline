#!/bin/bash -f
#PBS -S /bin/bash
#PBS -l nodes=1:ppn=<nthread>:<cluster_server>
#PBS -q <cluster_server>
#PBS -N <jobname>
#PBS -j eo
#PBS -m ae
#PBS -e <logpath>

## Check command ##
source "~/.bashrc"
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

##Functions#######
get_median_length() {
    zcat $1 | awk '{if(NR%4==2) {print length($0)}}' | sort -n | awk '{
        count++; length_sum+=$1; length_array[count]=$1
    } END {
        if(count%2) {
            print length_array[int(count/2)+1]
        } else {
            print (length_array[count/2]+length_array[count/2+1])/2
        }
    }'
}
###################
filetype="<filetype>"
sample_id="<sample_id>"

mkdir -p "<download_target>" && cd "<download_target>"

if [ "$filetype" = "bam" ]; then
    wget "<download_source>" -O "$sample_id.bam"
    cellranger bamtofastq --nthreads=<nthread> "$sample_id.bam" "./fastqs"

elif [ "$filetype" = "fastq" ]; then
    parent_dir="$(pwd)/fastqs"
    if [ ! -d "fastqs" ]; then
        mkdir -p "fastqs"
        cd "fastqs"
    fi
    IFS=',' read -ra run_ids <<< "<run_ids_str>"
    for run_id in "${run_ids[@]}"; do
        mkdir -p "$run_id"
        cd "$run_id"
        # if the number of file starting with "${sample_id}_S1_L001" and ending with "fastq.gz" is less than 2
        #TODO: ここが上手く動いてません
        # if [ $(ls ${sample_id}_S1_L001*.fastq.gz 2> /dev/null | wc -l) -lt 2 ]; then
        #     # remove recursively
        #     cd ..
        #     rm -rf "$run_id"
        #     continue
        # fi
        cd "$parent_dir"
        fastq-dump --split-files --origfmt --gzip "$run_id"
        input_fastqs=($(ls ${run_id}*.fastq.gz))
        # 配列の長さによるリードインデックスの定義
        read_indices=("R2" "R1" "I2" "I1")
        if [ ${#input_fastqs[@]} -eq 3 ]; then
            read_indices=("R2" "R1" "I1")
        elif [ ${#input_fastqs[@]} -eq 2 ]; then
            read_indices=("R2" "I1")
        fi
        # リード長の中央値とファイル名の連想配列の作成
        declare -A file_median_lengths
        for file in "${input_fastqs[@]}"; do
            median_length=$(get_median_length $file)
            file_median_lengths["$median_length"]=$file
        done
        # 中央値をソート
        sorted_medians=($(for k in "${!file_median_lengths[@]}"; do echo $k; done | sort -nr))
        # ファイルの改名
        for i in "${!sorted_medians[@]}"; do
            read_index=${read_indices[$i]}
            original_file=${file_median_lengths[${sorted_medians[$i]}]}
            new_file="${sample_id}_S1_L001_${read_index}_001.fastq.gz"
            mv $original_file $new_file
            echo "$original_file renamed to $new_file"
        done
    done
else
    echo "[ERROR] Input should be 'bam' or 'fastqs'"
    exit 1
fi
