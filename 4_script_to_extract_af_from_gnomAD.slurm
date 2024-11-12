#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1

#SBATCH --array=1-22

#SBATCH --time=2-00:00:00
#SBATCH --mem=15gb

#SBATCH --job-name=4_parsegnomAD
#SBATCH --output=logs/4/gnomad_af_chr%a.out
#SBATCH --error=logs/4/gnomad_af_chr%a.err

module load python

#
# Parameters to change
#

outdir=gnomAD_af_files
mkdir -p $outdir

#from previous script (3)
rsq=/path/to/imputed/variant/idx/file/chr$SLURM_ARRAY_TASK_ID.varidx.snpid.rsq.txt
gnomadvcf=/project/chia657_28/datasets/public/gnomAD/r3.1.2/gnomad.genomes.v3.1.2.hgdp_tgp.chr$SLURM_ARRAY_TASK_ID.vcf.bgz
gnomadaffile=$outdir/gnomad.genomes.v3.1.2.hgdp_tgp.chr$SLURM_ARRAY_TASK_ID.af.txt
filteredgnomadaffile=$outdir/gnomad.genomes.v3.1.2.hgdp_tgp.chr$SLURM_ARRAY_TASK_ID.af.intersect.txt

#
# End section
#

python3 /project/chia657_28/users/bldinh/scripts/assoc_test_parse_gnomAD_vcf_for_AF.py --vcf $gnomadvcf \
                                                                                       --out $gnomadaffile

python3 /project/chia657_28/users/bldinh/scripts/assoc_test_parse_gnomAD_AF_for_intersect.py --rsqfile $rsq \
                                                                                             --affile $gnomadaffile \
                                                                                             --out $filteredgnomadaffile
