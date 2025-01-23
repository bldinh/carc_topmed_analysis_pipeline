# CARC TOPMed Analysis Pipeline
Adaptation of the [TOPMed analysis pipeline](https://github.com/UW-GAC/analysis_pipeline) to run on CARC at USC. Scripts may be modified versions of original scripts.

---

## Installation:

Use the `0_install_r_libraries.R` script to install the required libraries for GENESIS.

If there is an issue writing to `/usr/tmp`, creating (or editing) the **~/.Renviron** file can be used to change the tmp directory. e.g. the following can be run on the commandline:
```
mkdir /scratch1/[USERID]/tmp
echo TMP = /scratch1/[USERID]/tmp >> ~/.Renviron
echo TMPDIR = /scratch1/[USERID]/tmp >> ~/.Renviron
```

---

## Split into multiple pipelines:
- Generate files for analysis (current repository)
    - PCs and GRM from array data
    - Convert imputed data to GDS format
    - Parse gnomAD for continental AF
- Fit null model with PCs and GRM as covariates and test variants (separate)
    - The following may need to be added after the latest CARC upgrade (Jan. 2025) to run assocTestSingle (in `_assoc_test_autosomes.R`):
    - ```
      library(BiocParallel)
      register(SerialParam(), default = T)
      ```
