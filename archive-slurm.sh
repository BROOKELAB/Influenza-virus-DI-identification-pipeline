#!/bin/bash
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -J archive


if [ -z "$DIR" ]; then
    echo "Must specify a directory"
fi

cd $SLURM_SUBMIT_DIR

module load pigz/2.3.4-IGB-gcc-4.9.4
module load perl/5.24.1

perl /home/groups/hpcbio/dev/HPCBio-Toolbox/archive-util/prep_for_archive.pl -d $DIR
