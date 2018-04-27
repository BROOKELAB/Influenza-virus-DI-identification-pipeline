#!/bin/bash
#SBATCH -N 1
#SBATCH -c 1
#SBATCH -p normal
#SBATCH --mem=48G
#SBATCH -J archive

DIR=/home/groups/hpcbio_shared/cbrooke_lab/test-project

if [ -z "$DIR" ]; then
    echo "Must specify a directory"
fi

cd $SLURM_SUBMIT_DIR

module load pigz/2.3.4-IGB-gcc-4.9.4
module load Perl/5.24.1-IGB-gcc-4.9.4

perl DARPA-project/src/Brooke-DARPA/prep_for_archive_brooke.pl -d $DIR
