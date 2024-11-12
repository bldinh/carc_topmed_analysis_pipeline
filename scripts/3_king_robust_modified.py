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
1) KING robust using SNPRelate algorithm
"""

parser = ArgumentParser(description=description)
parser.add_argument("config_file", help="configuration file")
parser.add_argument("-n", "--ncores", default="8", help="number of cores to use [default %(default)s]")
args = parser.parse_args()

configfile = args.config_file
ncores = args.ncores

configdict = TopmedPipeline.readConfig(configfile)
configdict = TopmedPipeline.directorySetup(configdict, subdirs=["config", "data", "logs", "plots"])


job = "ibd_king"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["out_file"] = configdict["data_prefix"] + "_king_robust.gds"
configfile = configdict["config_prefix"] + "_" + job + ".config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
subprocess.run(cmd, shell=True)


job = "kinship_plots"
rscript = os.path.join("R", job + ".R")
config = deepcopy(configdict)
config["kinship_file"] = configdict["data_prefix"] + "_king_robust.gds"
config["kinship_method"] = "king"
config["out_file_all"] = configdict["plots_prefix"] + "_king_robust_kinship_all.pdf"
config["out_file_study"] = configdict["plots_prefix"] + "_king_robust_kinship_study.pdf"
configfile = configdict["config_prefix"] + "_" + job + "_robust.config"
TopmedPipeline.writeConfig(config, configfile)

cmd = f'Rscript R/{job}.R {configfile} --version 2.12.1'
subprocess.run(cmd, shell=True)

