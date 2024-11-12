#! /usr/bin/env python3

"""LD Pruning"""

import concurrent.futures
import TopmedPipeline
import subprocess
import sys
import os
from argparse import ArgumentParser
from copy import deepcopy

description = """
LD pruning with the following steps:
1) Select variants with LD pruning
2) Combine selected variants from all chromosomes
3) Create GDS file with only pruned variants
"""

parser = ArgumentParser(description=description)
parser.add_argument("config_file", help="configuration file")
parser.add_argument("-c", "--chromosomes", default="1-22", help="range of chromosomes [default %(default)s]")
parser.add_argument("--workers", default=1, help="number of workers to use in parallel")
args = parser.parse_args()

configfile = args.config_file
chromosomes = args.chromosomes
workers = int(args.workers)

chrom_start = int(chromosomes.split('-')[0])
chrom_end = int(chromosomes.split('-')[1])

configdict = TopmedPipeline.readConfig(configfile)
configdict = TopmedPipeline.directorySetup(configdict, subdirs=["config", "data", "logs", "plots"])

def run_r_script_on_chr(script_chrom_tuple):
    script, subconfig, chrom = script_chrom_tuple
    print(script,chrom)
    cmd = f"Rscript R/{script}.R {subconfig} --chromosome {chrom} --version 2.12.1"
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def run_parallel(list_of_tuples):
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(run_r_script_on_chr, list_of_tuples)
        executor.shutdown()


job = "ld_pruning"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["out_file"] = configdict["data_prefix"] + "_pruned_variants_chr .RData"
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

ldprune_script_chrom_tuples = [(job,configfile,chrom) for chrom in range(chrom_start, chrom_end+1)]
run_parallel(ldprune_script_chrom_tuples)


job = "subset_gds"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["subset_gds_file"] = configdict["subset_gds_file"] + ".chr .tmp"
config["variant_include_file"] = configdict["data_prefix"] + "_pruned_variants_chr .RData"
config["sample_include_file"] = "NA"
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

subsetgds_script_chrom_tuples = [(job,configfile,chrom) for chrom in range(chrom_start, chrom_end+1)]
run_parallel(subsetgds_script_chrom_tuples)


job = "merge_gds"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["gds_file"] = configdict["subset_gds_file"] + ".chr .tmp"
config["merged_gds_file"] = configdict["subset_gds_file"]
config["chromosomes"] = TopmedPipeline.parseChromosomes(chromosomes)
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f"Rscript R/merge_gds.R {configdict['config_prefix']}_merge_gds.config --version 2.12.1"
subprocess.run(cmd, shell=True)


job = "check_merged_gds"
rscript = os.path.join("R", job + ".R")

mergegds_script_chrom_tuples = [(job,configfile,chrom) for chrom in range(chrom_start, chrom_end+1)]
run_parallel(mergegds_script_chrom_tuples)

# remove temporary files (per-chr subset)

#delete tmp files manually


