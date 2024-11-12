#! /usr/bin/env python3

"""Identity By Descent"""

import TopmedPipeline
import subprocess
import sys
import os
from argparse import ArgumentParser
from copy import deepcopy

description = """
Identity by Descent with the following steps:
1) Convert GDS to BED for use with KING
2) KING --ibdseg to get initial kinship estimates
3) Convert KING output to sparse matrix
"""

parser = ArgumentParser(description=description)
parser.add_argument("config_file", help="configuration file")
parser.add_argument("-n", "--ncores", default="8", help="number of cores to use [default %(default)s]")
args = parser.parse_args()

configfile = args.config_file
ncores = args.ncores

configdict = TopmedPipeline.readConfig(configfile)
configdict = TopmedPipeline.directorySetup(configdict, subdirs=["config", "data", "logs", "plots"])


job = "gds2bed"

rscript = os.path.join("R", job + ".R")

# include all samples in BED
config = deepcopy(configdict)
config["sample_include_file"] = "NA"
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
subprocess.run(cmd, shell=True)

## this swaps alleles to make KING --ibdseg happy about reading the file
job = "plink_make-bed"

bedprefix = configdict["bed_file"]
arglist = ["--bfile", bedprefix, "--make-bed", "--out", bedprefix]

cmd = f'/scratch1/bldinh/programs/plink --bfile {bedprefix} --make-bed --out {bedprefix}'
subprocess.run(cmd, shell=True)

## when input and output files have same name, plink renames input with "~"


job = "king_ibdseg"

bedfile = configdict["bed_file"] + ".bed"
outprefix = configdict["data_prefix"] + "_king_ibdseg"
arglist = ["-b", bedfile, "--cpus", ncores, "--ibdseg", "--prefix", outprefix]

cmd = f'/project/chia657_28/programs/king2.2.5 -b {bedfile} --cpus {ncores} --ibdseg --prefix {outprefix}'
subprocess.run(cmd, shell=True)


# gzip output
kingfile = outprefix + ".seg"
cmd = f'gzip -f {kingfile}'
subprocess.run(cmd, shell=True)
kingfile = kingfile + ".gz"


job = "kinship_plots"

rscript = os.path.join("R", job + ".R")

config = deepcopy(configdict)
config["kinship_file"] = kingfile
config["kinship_method"] = "king_ibdseg"
config["out_file_all"] = configdict["plots_prefix"] + "_king_ibdseg_kinship_all.pdf"
config["out_file_cross"] = configdict["plots_prefix"] + "_king_ibdseg_kinship_cross.pdf"
config["out_file_study"] = configdict["plots_prefix"] + "_king_ibdseg_kinship_study.pdf"
configfile = configdict["config_prefix"] + "_" + job + "_ibdseg.config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
subprocess.run(cmd, shell=True)


job = "king_to_matrix"

rscript = os.path.join("R", job + ".R")

config = deepcopy(configdict)
config["king_file"] = kingfile
config["kinship_method"] = "king_ibdseg"
config["out_prefix"] = configdict["data_prefix"] + "_king_ibdseg_Matrix"
configfile = configdict["config_prefix"] + "_" + job + "_ibdseg.config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
subprocess.run(cmd, shell=True)

