#! /usr/bin/env python3

"""PC-Relate"""

import TopmedPipeline
import subprocess
import sys
import os
from argparse import ArgumentParser
from copy import deepcopy

description = """
PC-Relate with the following steps:
1) Calculate ISAF betas
2) Calculate kinship in all sample blocks in parallel
3) Correct kinship estimates
"""

parser = ArgumentParser(description=description)
parser.add_argument("config_file", help="configuration file")
args = parser.parse_args()

configfile = args.config_file

configdict = TopmedPipeline.readConfig(configfile)
configdict = TopmedPipeline.directorySetup(configdict, subdirs=["config", "data", "logs", "plots"])


job = "pcrelate_beta"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["out_prefix"] = configdict["data_prefix"] + "_isaf_beta"
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
subprocess.run(cmd, shell=True)




job = "pcrelate"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["beta_file"] = configdict["data_prefix"] + "_isaf_beta.RData"
config["out_prefix"] = configdict["data_prefix"]
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

# define sample blocks
n_blocks = int(configdict.setdefault("n_sample_blocks", "1"))
if n_blocks > 1:
    blocks = [(i,j) for i in range(1, n_blocks+1) for j in range(i, n_blocks+1)]
    block_range = "1-" + str(len(blocks))
else:
    block_range = "1"

cmd = f'Rscript R/{job}.R {configfile} --segment {block_range} --version 2.12.1'
subprocess.run(cmd, shell=True)




job = "pcrelate_correct"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["pcrelate_prefix"] = configdict["data_prefix"]
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
subprocess.run(cmd, shell=True)




job = "kinship_plots"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["kinship_file"] = configdict["data_prefix"] + "_pcrelate.RData"
config["kinship_method"] = "pcrelate"
config["out_file_all"] = configdict["plots_prefix"] + "_kinship_all.pdf"
config["out_file_cross"] = configdict["plots_prefix"] + "_kinship_cross.pdf"
config["out_file_study"] = configdict["plots_prefix"] + "_kinship_study.pdf"
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
subprocess.run(cmd, shell=True)



