#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=2
#SBATCH --ntasks=1

#SBATCH --array=1

#SBATCH --time=2-00:00:00
#SBATCH --mem=100gb


#SBATCH --job-name=1_pipeline
#SBATCH --output=logs/1_pipeline.out
#SBATCH --error=logs/1_pipeline.err

threads=2
PLINK=
module load r


#
# Parameters to change
#

# expects data to start off in PLINK format (.bim, .fam, .bed) and split by chr



scriptsdir=scripts #default name path to the scripts folder, without trailing "/"

outdir=data
mergeinput=$outdir/plinkfmt_mergefile.txt #file to write chromosome-separated plink fp to
preqcfolder=$outdir/plinkfmt_merged_gwas #directory to create and output the merged plink to
preqcplinkprefix=$preqcfolder/some.prefix.preqc #prefix for merged plink

#for "qc" plink output
outfolder=$outdir/plinkfmt_maf01_geno01
plinkprefix=$outfolder/some.prefix.maf01.geno01
configprefix=config.some.prefix.geno01.maf01 #prefix for all config files that will be written

rm -f $mergeinput
touch $mergeinput
mkdir -p $preqcfolder
mkdir -p $outfolder

for i in {1..22};do
    #for LOCO but not used at the moment:
    #[ "$i" -eq $SLURM_ARRAY_TASK_ID ] && continue
    #echo data/initial_megagda_geno01_maf01_plink/dropchr$i.megagdatmimputed >> $mergeinput

    echo /path/to/plink/data/prefix.chr$i >> $mergeinput
done

$PLINK --merge-list $mergeinput --make-bed --out $preqcplinkprefix
$PLINK  --bfile $preqcplinkprefix --make-bed  --maf .01 --geno .01 --out $plinkprefix

#
# End parameter section
#


#
# Write all configs
#


# ld config file
ldconfig=$configprefix"-1-ld-prune.config"
ldprefix=$configprefix'_1-ld-prune'
ldgds=$plinkprefix'-1-ld-pruned.gds'
echo out_prefix \"$ldprefix\" > $ldconfig
echo gds_file \"$plinkprefix'.chr .gds'\" >> $ldconfig
echo subset_gds_file \"$ldgds\" >> $ldconfig

# king 1 config file
king1config=$configprefix"-2-king_initial.config"
kingprefix=$configprefix'_2-king-initial'
echo out_prefix \"$kingprefix\" > $king1config
echo gds_file \"$ldgds\" >> $king1config
echo bed_file \"$configprefix'-initial_BED'\" >> $king1config

# king 2 config file
king2config=$configprefix"-3-king_robust.config"
echo out_prefix \"$configprefix'_3-king-robust'\" > $king2config
echo gds_file \"$ldgds\" >> $king2config

# pcair 1 config file
pcair1config=$configprefix"-4-pcair-round1.config"
echo out_prefix \"$configprefix'_pcair-round1'\" > $pcair1config
echo gds_file \"$ldgds\" >> $pcair1config
echo full_gds_file \"$plinkprefix'.chr .gds'\" >> $pcair1config
echo kinship_file \"data/$configprefix'_2-king-initial_king_ibdseg_Matrix.RData'\" >> $pcair1config
echo divergence_file \"data/$configprefix'_3-king-robust_king_robust.gds'\" >> $pcair1config

# pcrelate 1 config file
pcrelate1config=$configprefix"-5-pcrelate-round1.config"
echo out_prefix \"$configprefix'_pcrelate-round1'\" > $pcrelate1config
echo gds_file \"$ldgds\" >> $pcrelate1config
echo pca_file \"data/$configprefix'_pcair-round1_pcair.RData'\" >> $pcrelate1config
echo n_pcs 4 >> $pcrelate1config
echo variant_block_size 1024 >> $pcrelate1config
echo sample_include_file NA >> $pcrelate1config

# pcair 2 config file
pcair2config=$configprefix"-6-pcair-round2.config"
echo out_prefix \"$configprefix'_pcair-round2'\" > $pcair2config
echo gds_file \"$ldgds\" >> $pcair2config
echo full_gds_file   \"$plinkprefix'.chr .gds'\" >> $pcair2config
echo kinship_file \"data/$configprefix'_pcrelate-round1_pcrelate_Matrix.RData'\" >> $pcair2config
echo divergence_file \"data/$configprefix'_3-king-robust_king_robust.gds'\" >> $pcair2config

# pcrelate 2 config file
pcrelate2config=$configprefix"-7-pcrelate-round2.config"
echo out_prefix \"$configprefix'_pcrelate-round2'\" > $pcrelate2config
echo gds_file \"$ldgds\" >> $pcrelate2config
echo pca_file \"data/$configprefix'_pcair-round2_pcair.RData'\" >> $pcrelate2config
echo n_pcs 4 >> $pcrelate2config
echo variant_block_size 1024 >> $pcrelate2config
echo sample_include_file NA >> $pcrelate2config

#
# Run various scripts
#

# 0 plink to GDS - chrom from PLINK does not have "chr" before chromosome number
echo '\nRunning 0\n'
Rscript $scriptsdir/0_gds_and_chr_split.R $plinkprefix $threads

# 1 ld step
echo '\nRunning 1\n'
python3 $scriptsdir/1_ld_pruning.py $ldconfig --workers $threads

# 2 king 1
echo '\nRunning 2\n'
python3 $scriptsdir/2_king_modified.py $king1config --ncores $threads

# 3 king 2
echo '\nRunning 3\n'
python3 $scriptsdir/3_king_robust_modified.py $king2config --ncores $threads

# 4 pcair 1
echo '\nRunning 4\n'
python3 $scriptsdir/4_pcair_modified.py $pcair1config --ncores $threads

# 5 pcrelate 1
echo '\nRunning 5\n'
python3 $scriptsdir/5_pcrelate_modified.py $pcrelate1config

# 6 pcair 2
echo '\nRunning 6\n'
python3 $scriptsdir/4_pcair_modified.py $pcair2config --ncores $threads

# 7 pcrelate 2
echo '\nRunning 7\n'
python3 $scriptsdir/5_pcrelate_modified.py $pcrelate2config


