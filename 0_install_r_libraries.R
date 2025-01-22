install.packages("devtools")
    devtools::install_github("igraph/rigraph")
install.packages("Matrix")
install.packages("mgcv")

if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install(version = "3.20", ask=F)
BiocManager::install("GENESIS")
