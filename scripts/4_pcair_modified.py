#! /usr/bin/env python3

"""PC-AiR"""

import TopmedPipeline
import subprocess
import sys
import os
from argparse import ArgumentParser
from copy import deepcopy

description = """
PCA with the following steps:
1) Find unrelated sample set
2) (optional) Select SNPs with LD pruning using unrelated samples
3) PCA (using unrelated set, then project relatives)
4) SNV-PC correlation
"""

parser = ArgumentParser(description=description)
parser.add_argument("config_file", help="configuration file")
parser.add_argument("--ld_pruning", action="store_true", default=False, help="run LD pruning of variants prior to PCA")
parser.add_argument("-c", "--chromosomes", default="1-22", help="range of chromosomes [default %(default)s]")
parser.add_argument("-n", "--ncores", default="1-8", help="number of cores to use; either a number (e.g, 1) or a range of numbers (e.g., 1-4) [default %(default)s]")
args = parser.parse_args()

configfile = args.config_file
ld = args.ld_pruning
chromosomes = args.chromosomes
ncores = args.ncores

configdict = TopmedPipeline.readConfig(configfile)
configdict = TopmedPipeline.directorySetup(configdict, subdirs=["config", "data", "logs", "plots"])


job = "find_unrelated"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["out_related_file"] = configdict["data_prefix"] + "_related.RData"
config["out_unrelated_file"] = configdict["data_prefix"] + "_unrelated.RData"
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
subprocess.run(cmd, shell=True)

if ld:
    job = "ld_pruning"
    rscript = os.path.join("R", job + ".R")
    config = deepcopy(configdict)
    config["sample_include_file"] = configdict["data_prefix"] + "_unrelated.RData"
    config["out_file"] = configdict["data_prefix"] + "_pruned_variants_chr .RData"
    configfile = configdict["config_prefix"] + "_" + job + ".config"
    TopmedPipeline.writeConfig(config, configfile)

    for chrom in range(1,22+1):
        cmd = f'Rscript R/{job}.R {configfile} --chromosome {chrom} --version 2.12.1'
        subprocess.run(cmd, shell=True)

    job = "combine_variants"
    rscript = os.path.join("R", job + ".R")
    config = dict()
    config["chromosomes"] = TopmedPipeline.parseChromosomes(chromosomes)
    config["in_file"] = configdict["data_prefix"] + "_pruned_variants_chr .RData"
    config["out_file"] = configdict["data_prefix"] + "_pruned_variants.RData"
    configfile = configdict["config_prefix"] + "_" + job + ".config"
    TopmedPipeline.writeConfig(config, configfile)

    cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
    subprocess.run(cmd, shell=True)


## could split pca_byrel script into two parts: pca on unrelated, then project relatives
## could start pca_corr once first part is done
## but probably not worth it

job = "pca_byrel"
rscript = os.path.join("R", job + ".R")

config = deepcopy(configdict)
config["related_file"] = configdict["data_prefix"] + "_related.RData"
config["unrelated_file"] = configdict["data_prefix"] + "_unrelated.RData"
if ld:
    config["variant_include_file"] = configdict["data_prefix"] + "_pruned_variants.RData"
config["out_file"] = configdict["data_prefix"] + "_pcair.RData"
config["out_file_unrel"] = configdict["data_prefix"] + "_pcair_unrel.RData"
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
subprocess.run(cmd, shell=True)


## config needs both sample and subject annotation (or merge them ahead of running pipeline)

job = "pca_plots"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["pca_file"] = configdict["data_prefix"] + "_pcair.RData"
config["out_file_scree"] = configdict["plots_prefix"] + "_pca_scree.pdf"
config["out_file_pc12"] = configdict["plots_prefix"] + "_pca_pc12.pdf"
config["out_file_parcoord"] = configdict["plots_prefix"] + "_pca_parcoord.pdf"
config["out_file_pairs"] = configdict["plots_prefix"] + "_pca_pairs.png"
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
subprocess.run(cmd, shell=True)


## want to run pca_corr on more variants than in LD pruned set, but not all variants
## select a random set of ~10% of variants, where numbers are proportional by chromosome
## will need to include full GDS files in config as well as LD pruned. could be per-chromosome.
job = "pca_corr_vars"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
build = configdict.setdefault("genome_build", "hg38")
config["segment_file"] = os.path.join("segments_" + build + ".txt")
config["gds_file"] = configdict["full_gds_file"]
config["pca_file"] = configdict["data_prefix"] + "_pcair.RData"
if ld:
    config["variant_include_file"] = configdict["data_prefix"] + "_pruned_variants.RData"
config["out_file"] = configdict["data_prefix"] + "_pcair_corr_variants_chr .RData"
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

for chrom in range(1,22+1):
    cmd = f'Rscript R/{job}.R {configfile} --chromosome {chrom} --version 2.12.1'
    subprocess.run(cmd, shell=True)

job = "pca_corr"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["gds_file"] = configdict["full_gds_file"]
config["pca_file"] = configdict["data_prefix"] + "_pcair_unrel.RData"
config["variant_include_file"] = configdict["data_prefix"] + "_pcair_corr_variants_chr .RData"
config["out_file"] = configdict["data_prefix"] + "_pcair_corr_chr .gds"
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

# single core only
for chrom in range(1,22+1):
    cmd = f'Rscript R/{job}.R {configfile} --chromosome {chrom} --version 2.12.1'
    subprocess.run(cmd, shell=True)

job = "pca_corr_plots"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["chromosomes"] = TopmedPipeline.parseChromosomes(chromosomes)
config["corr_file"] = configdict["data_prefix"] + "_pcair_corr_chr .gds"
config["out_prefix"] = configdict["plots_prefix"] + "_pcair_corr"
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
subprocess.run(cmd, shell=True)

