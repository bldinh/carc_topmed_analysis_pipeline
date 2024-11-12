#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1

#SBATCH --array=1-22

#SBATCH --time=2-00:00:00
#SBATCH --mem=20gb

#SBATCH --account=rohs_108
#SBATCH --partition=oneweek

#SBATCH --job-name=2_gds_conversion
#SBATCH --output=logs/2/chr%a.out
#SBATCH --error=logs/2/chr%a.err


#all of the following may not be used
module purge
module load usc/8.3.0
module load cmake
module load openblas/0.3.8
module load r
module load gsl/2.5
module load pandoc


#
#Paths/filenames to modify
#

vcf=/path/to/your/vcf/file.chr$SLURM_ARRAY_TASK_ID.vcf.gz
gdsfile=/path/to/output/gds/to/.chr$SLURM_ARRAY_TASK_ID.gds

#
#End section to modify
#

#Create GDS file from VCF
Rscript _convert_imputedvcf_to_gds.R --outgds $gdsfile --vcf $vcf






