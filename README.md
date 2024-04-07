# carc_topmed_analysis_pipeline
Adaptation of the [TOPMed analysis pipeline](https://github.com/UW-GAC/analysis_pipeline) to run on CARC at USC

Split into multiple pipelines:
- Generate PCs and GRM from array data
- Convert imputed data to GDS format
- Fit null model with PCs and GRM as covariates and test variants
