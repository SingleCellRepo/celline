#!/bin/bash -f
#PBS -S /bin/bash
#PBS -l nodes=1:ppn=1:cosmos
#PBS -q cosmos
#PBS -N dump
#PBS -j eo
#PBS -m ae
#PBS -e /mnt/work1/yuyasato/Projects/lib/celline/test/jobs/auto/0_dump/1663657626.9768677/logs/dump_cluster_0.log

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE150202/0_dumped/GSM4543351/fastqs/rep3" || exit
scfastq-dump SRR11746187
mv SRR11746187_3.fastq.gz GSM4543351_S1_L001_I1_001.fastq.gz
mv SRR11746187_1.fastq.gz GSM4543351_S1_L001_R1_001.fastq.gz
mv SRR11746187_2.fastq.gz GSM4543351_S1_L001_R2_001.fastq.gz

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE150202/0_dumped/GSM4543351/fastqs/rep2" || exit
scfastq-dump SRR11746186
mv SRR11746186_3.fastq.gz GSM4543351_S1_L001_I1_001.fastq.gz
mv SRR11746186_1.fastq.gz GSM4543351_S1_L001_R1_001.fastq.gz
mv SRR11746186_2.fastq.gz GSM4543351_S1_L001_R2_001.fastq.gz

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE150202/0_dumped/GSM4543351/fastqs/rep1" || exit
scfastq-dump SRR11746185
mv SRR11746185_3.fastq.gz GSM4543351_S1_L001_I1_001.fastq.gz
mv SRR11746185_1.fastq.gz GSM4543351_S1_L001_R1_001.fastq.gz
mv SRR11746185_2.fastq.gz GSM4543351_S1_L001_R2_001.fastq.gz

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE150202/0_dumped/GSM4543351/fastqs/rep0" || exit
scfastq-dump SRR11746184
mv SRR11746184_3.fastq.gz GSM4543351_S1_L001_I1_001.fastq.gz
mv SRR11746184_1.fastq.gz GSM4543351_S1_L001_R1_001.fastq.gz
mv SRR11746184_2.fastq.gz GSM4543351_S1_L001_R2_001.fastq.gz

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE183852/0_dumped/GSM5572774/fastqs/rep0" || exit
scfastq-dump SRR15835850
mv SRR15835850_1.fastq.gz GSM5572774_S1_L001_R1_001.fastq.gz
mv SRR15835850_2.fastq.gz GSM5572774_S1_L001_R2_001.fastq.gz
