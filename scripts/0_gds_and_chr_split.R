library(SeqArray)
library(SeqVarTools)
library(foreach)
library(doParallel)

args <- commandArgs(trailingOnly = TRUE)  #1 indexed
prefix <- args[1]
numCores <- args[2]

bed.fn <- paste0(prefix, ".bed")
bim.fn <- paste0(prefix, ".bim")
fam.fn <- paste0(prefix, ".fam")

out.gdsfn <- paste0(prefix, ".gds")

seqBED2GDS(bed.fn, fam.fn, bim.fn, out.gdsfn)

## Split GDS by CHR

cl <- makeCluster(strtoi(numCores))
registerDoParallel(cl)
foreach(i=1:22, .packages = "SeqArray") %dopar% {
    gds.full <- seqOpen(out.gdsfn)
    chr <- seqGetData(gds.full, "chromosome")
    var.id <- seqGetData(gds.full, "variant.id")

    seqSetFilter(gds.full, variant.id = var.id[which(chr == i)])
    seqExport(gds.full, out.fn = paste0(prefix, ".chr", i, ".gds"))
    seqSetFilter(gds.full)
    seqClose(gds.full)
}


# Session Information
sessionInfo()
