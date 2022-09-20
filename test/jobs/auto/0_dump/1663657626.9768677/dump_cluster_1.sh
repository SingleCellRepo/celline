#!/bin/bash -f
#PBS -S /bin/bash
#PBS -l nodes=1:ppn=1:cosmos
#PBS -q cosmos
#PBS -N dump
#PBS -j eo
#PBS -m ae
#PBS -e /mnt/work1/yuyasato/Projects/lib/celline/test/jobs/auto/0_dump/1663657626.9768677/logs/dump_cluster_1.log

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE183852/0_dumped/GSM5572774/fastqs/rep1" || exit
scfastq-dump SRR15835851
mv SRR15835851_1.fastq.gz GSM5572774_S1_L002_R1_001.fastq.gz
mv SRR15835851_2.fastq.gz GSM5572774_S1_L002_R2_001.fastq.gz

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE183852/0_dumped/GSM5572774/fastqs/rep2" || exit
scfastq-dump SRR15835852
mv SRR15835852_1.fastq.gz GSM5572774_S1_L003_R1_001.fastq.gz
mv SRR15835852_2.fastq.gz GSM5572774_S1_L003_R2_001.fastq.gz

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE183852/0_dumped/GSM5572774/fastqs/rep3" || exit
scfastq-dump SRR15835853
mv SRR15835853_1.fastq.gz GSM5572774_S1_L004_R1_001.fastq.gz
mv SRR15835853_2.fastq.gz GSM5572774_S1_L004_R2_001.fastq.gz

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE183852/0_dumped/GSM5572776/fastqs/rep0" || exit
scfastq-dump SRR15835858
mv SRR15835858_1.fastq.gz GSM5572776_S8_L001_R1_001.fastq.gz
mv SRR15835858_2.fastq.gz GSM5572776_S8_L001_R2_001.fastq.gz

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE183852/0_dumped/GSM5572776/fastqs/rep1" || exit
scfastq-dump SRR15835859
mv SRR15835859_1.fastq.gz GSM5572776_S8_L002_R1_001.fastq.gz
mv SRR15835859_2.fastq.gz GSM5572776_S8_L002_R2_001.fastq.gz

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE183852/0_dumped/GSM5572776/fastqs/rep2" || exit
scfastq-dump SRR15835860
mv SRR15835860_1.fastq.gz GSM5572776_S8_L003_R1_001.fastq.gz
mv SRR15835860_2.fastq.gz GSM5572776_S8_L003_R2_001.fastq.gz

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE183852/0_dumped/GSM5572776/fastqs/rep3" || exit
scfastq-dump SRR15835861
mv SRR15835861_2.fastq.gz GSM5572776_S8_L004_R2_001.fastq.gz
mv SRR15835861_1.fastq.gz GSM5572776_S8_L004_R1_001.fastq.gz

cd "/mnt/work1/yuyasato/Projects/lib/celline/test/GSE129788/0_dumped/GSM3722100/bam" || exit
wget https://sra-pub-src-1.s3.amazonaws.com/SRR8895030/YX1L.bam.1
mv YX1L.bam.1 GSM3722100.bam
mv YX1L.bam.1 GSM3722100.bam
