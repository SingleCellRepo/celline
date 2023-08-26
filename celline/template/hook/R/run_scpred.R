pacman::p_load(
    Seurat, tidyverse,
    SeuratDisk, scPred
)
args <- commandArgs(trailingOnly = TRUE)
all_sample_path <- unlist(strsplit(args[1], split = ","))
reference_seurat <- args[2]
reference_celltype <- args[3]
dist_dir <- unlist(strsplit(args[4], split = ","))

all_sample_path_resolved <- c()
for (target_sample_path in all_sample_path) {
    if (!file.exists(target_sample_path)) {
        message(
            paste0(
                "[ERROR!] Cound not resolved: ",
                target_sample_path,
                ". Skip"
            )
        )
    } else {
        all_sample_path_resolved <- c(
            all_sample_path_resolved, target_sample_path
        )
    }
}
message(reference_seurat)
reference <-
    readRDS(reference_seurat)
reference@misc$scPred <- readRDS(reference_celltype)

count <- 1
for (target_sample_path in all_sample_path_resolved) {
    message(
        paste0(
            "@ Predicting ", count, "/", length(all_sample_path_resolved), "\n",
            "└ ( ", target_sample_path, " )"
        )
    )
    predicted_file <- paste0(dist_dir[count], "/celltype_predicted.tsv")
    runquery <- !file.exists(predicted_file)
    if (runquery) {
        query <-
            Read10X_h5(target_sample_path) %>%
            CreateSeuratObject() %>%
            NormalizeData() %>%
            scPredict(reference) %>%
            RunUMAP(reduction = "scpred", dims = 1:30)
        query@meta.data %>%
            tibble::rownames_to_column("cell") %>%
            arrange(scpred_prediction) %>%
            dplyr::select(cell, scpred_prediction) %>%
            write_tsv(predicted_file)
    }
    count <- count + 1
}
