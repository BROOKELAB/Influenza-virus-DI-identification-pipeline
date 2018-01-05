#!/bin/bash
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -J archive

DIR=/home/groups/hpcbio_shared/cbrooke_lab/

if [ -z "$DIR" ]; then
    echo "Must specify a directory"
fi

cd $SLURM_SUBMIT_DIR

module load pigz/2.3.4-IGB-gcc-4.9.4
#module load perl/5.24.1
module load Perl/5.24.1-IGB-gcc-4.9.4

perl /home/a-m/jholmes5/bin/perl/prep_for_archive-slurm.pl -d $DIR
