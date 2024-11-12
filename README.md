# CARC TOPMed Analysis Pipeline
Adaptation of the [TOPMed analysis pipeline](https://github.com/UW-GAC/analysis_pipeline) to run on CARC at USC. Scripts may be modified versions of original scripts.

Split into multiple pipelines:
- Generate files for analysis (current repository)
    - PCs and GRM from array data
    - Convert imputed data to GDS format
    - Parse gnomAD for continental AF
- Fit null model with PCs and GRM as covariates and test variants (separate)
