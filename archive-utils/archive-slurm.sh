#!/bin/bash
#SBATCH -N 1
#SBATCH -c 1
#SBATCH -p normal
#SBATCH --mem=60G
#SBATCH -J archive
#SBATCH --mail-user=jholmes5@illinois.edu

DIR=/home/groups/hpcbio_shared/cbrooke_lab/DARPA-project

if [ -z "$DIR" ]; then
    echo "Must specify a directory"
fi

cd $SLURM_SUBMIT_DIR

#module load pigz/2.3.4-IGB-gcc-4.9.4
module load Perl/5.24.1-IGB-gcc-4.9.4

perl /home/groups/hpcbio_shared/cbrooke_lab/Brooke-DARPA/archive-utils/prep_for_archive_brooke.pl -d $DIR
