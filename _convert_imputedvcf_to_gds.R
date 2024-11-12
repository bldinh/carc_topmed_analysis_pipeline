library(argparser)
library(GENESIS)
library(GWASTools)
library(SNPRelate)
library(SeqArray)
library(SeqVarTools)

#want to use ld pruned pcs, ldpruned grm with all imputed variants

argp <- arg_parser("assoc test on chromosome")
argp <- add_argument(argp, "--outgds", help="", type="character")
argp <- add_argument(argp, "--vcf", help="", type="character")
argv <- parse_args(argp)
outgds <- argv$outgds
vcffile <- argv$vcf

seqVCF2GDS(vcffile, outgds, fmt.import="DS")

