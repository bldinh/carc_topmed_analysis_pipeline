#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1

#SBATCH --array=1-22

#SBATCH --time=2-00:00:00
#SBATCH --mem=2gb

#SBATCH --job-name=3_parse_imputed_vcf
#SBATCH --output=logs/3/chr%a.out
#SBATCH --error=logs/3/chr%a.err

module load python

#paths for script 1
vcf=/path/to/your/imputed/vcf/chr$SLURM_ARRAY_TASK_ID.vcf.gz
snpidrsqfile=/path/to/write/output/file/to/chr$SLURM_ARRAY_TASK_ID.varidx.snpid.rsq.txt

python3 /project/chia657_28/users/bldinh/scripts/assoc_test_parse_imputed_vcf_for_rsq_and_snpid.py --vcf $vcf \
                                                                                                   --out $snpidrsqfile

