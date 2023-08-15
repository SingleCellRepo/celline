pacman::p_load(
    Seurat, scPred, SingleCellPipeline,
    tidyverse, SeuratDisk,
    doParallel
)
args <- commandArgs(trailingOnly = TRUE)
nthread <- args[1]
seurat_10x_file_path <- args[2]
celltype_path <- args[3]
dist_path <- args[3]
reference <-
    LoadH5Seurat(
        "../data/RefHS.h5seurat"
    )


reference <- getFeatureSpace(reference, "celltype")

cl <- makePSOCKcluster(30)
registerDoParallel(cl)
reference <- trainModel(reference, allowParallel = TRUE)
stopCluster(cl)

get_probabilities(reference) %>%
    tibble::rownames_to_column("cell") %>%
    write_tsv(
        "../data/human/probanility.tsv"
    )

ggsave(
    "../data/human/plot_probabilities.png",
    plot_probabilities(reference),
    width = 60,
    height = 60,
    units = "cm"
)
saveRDS(
    get_scpred(reference),
    "../data/RefHS.pred"
)
