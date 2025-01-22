# CARC TOPMed Analysis Pipeline
Adaptation of the [TOPMed analysis pipeline](https://github.com/UW-GAC/analysis_pipeline) to run on CARC at USC. Scripts may be modified versions of original scripts.

Installation:

Use the `0_install_r_libraries.R` script to install the required libraries for GENESIS.

The following may be needed to change the tmp directory:


Create ~/.Renviron file with the following:

    TMP = /scratch1/[USERID]/tmp
    TMPDIR = /scratch1/[USERID]/tmp



Split into multiple pipelines:
- Generate files for analysis (current repository)
    - PCs and GRM from array data
    - Convert imputed data to GDS format
    - Parse gnomAD for continental AF
- Fit null model with PCs and GRM as covariates and test variants (separate)
