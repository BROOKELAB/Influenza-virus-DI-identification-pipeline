#!/usr/bin/env nextflow
/*
* USAGE: nextflow run myscript.nf -qs 8
* Note that "-qs" is similar to "#SLURM --array=##%8" and will only run a specified # of jobs at a time.
* This script creates hard links to data that exists in nextflows work directory.
*/

/*
 * Set parameter values here. Only change the values within quotations
 * Many of the values already present will be okay to use, but make sure the pathes
 * are correct for your dataset.
*/

/*Path to project folder*/
projectPath = "/home/groups/hpcbio_shared/cbrooke_lab/DARPA-project/"

/* Paths to bowtie indices */
pr8_index = "${projectPath}/data/genome/bowtie-1.2.0-index/modified_PR8_ref_padded"
cal07_index = "${projectPath}/data/genome/bowtie-1.2.0-index/Cal07_padded"

viremaApp = "${projectPath}/apps/ViReMa_with_Fuzz"

/* Path to raw fastq files */
rawDataPath = "${projectPath}/results/Dec2017-runC_organized"
pr8reads = Channel.fromPath("${rawDataPath}/PR8/bowtie2/S*/*_unaligned.fq")
cal07reads = Channel.fromPath("${rawDataPath}/Cal07/bowtie2/S*/*_unaligned.fq")

/*Biocluster options. List memory in gigabytes like in suggestions below*/
myQueue = 'normal'
viremaMem = '60'
viremaCPU = '6'

/*Module versions*/
bowtie1Mod = 'Bowtie/1.2.0-IGB-gcc-4.9.4'
pythonMod = 'Python/2.7.13-IGB-gcc-4.9.4'
perlMod = 'Perl/5.24.1-IGB-gcc-4.9.4'


/* Alignment & Counting options */
micro = '20' /* The minimum length of microindels */
defuzz = '3' /* If a start position is fuzzy, then its reported it at the 3' end (3), 5' end (5), or the center of fuzzy region (0). */
mismatch = '0' /* This is the value of --N in ViReMa */

/*Output paths*/
pr8Path = "${projectPath}/results/Mar2017-Fuzz-virema/runC/PR8"
cal07Path = "${projectPath}/results/Mar2017-Fuzz-virema/runC/Cal07"

/*
* Step 1a. ViReMa on PR8 samples
*/
process runViremaPR8 {
    executor 'slurm'
    cpus viremaCPU
    queue myQueue
    memory "$viremaMem GB"
    module "${bowtie1Mod}:${pythonMod}"
    publishDir pr8Path, mode: 'link'

    input:
    file unalign from pr8reads

    output:
    file "*.results"
    file "*Virus_Recombination_Results.txt" into virema_sum
    file "*tions.txt"
    file "*UnMapped*.txt"
    file "*Single*.txt"
    file "*_rename.fq"

    """
    awk '{print (NR%4 == 1) ? "@1_" ++i : \$0}' $unalign >  ${unalign.baseName}_rename.fq
    
    python ${viremaApp}/ViReMa.py --MicroInDel_Length $micro -DeDup --Defuzz $defuzz \
    --N $mismatch --Output_Tag $unalign.baseName -ReadNamesEntry --p $viremaCPU \
    $pr8_index ${unalign.baseName}_rename.fq ${unalign.baseName}.results

    """
}

/*
* Step 1b. ViReMa on Cal07 samples
*/
process runViremaCal07 {
    executor 'slurm'
    cpus viremaCPU
    queue myQueue
    memory "$viremaMem GB"
    module "${bowtie1Mod}:${pythonMod}"
    publishDir cal07Path, mode: 'link'

    input:
    file unalign from cal07reads

    output:
    file "*.results"
    file "*Virus_Recombination_Results.txt" into virema_sumb
    file "*tions.txt"
    file "*UnMapped*.txt"
    file "*Single*.txt"
    file "*_rename.fq"

    """
    awk '{print (NR%4 == 1) ? "@1_" ++i : \$0}' $unalign >  ${unalign.baseName}_rename.fq

    python ${viremaApp}/ViReMa.py --MicroInDel_Length $micro -DeDup --Defuzz $defuzz \
    --N $mismatch --Output_Tag $unalign.baseName -ReadNamesEntry --p $viremaCPU \
    $cal07_index ${unalign.baseName}_rename.fq ${unalign.baseName}.results

    """
}


/*
* Step 3. ViReMa Summary of results (w/ perl scripts)
*/
process runSummaryPR8 {
    executor 'slurm'
    queue myQueue
    memory "$viremaMem GB"
    module perlMod
    publishDir pr8Path, mode: 'link'

    input:
    file in_file from virema_sum

    output:
    file "*.par5*"

    """
    perl ${projectPath}/src/Brooke-DARPA/parse-recomb-results-Fuzz.pl -d 5 -i $in_file -o ${in_file.baseName}.par5
    """
}

/*
* Step 4. ViReMa Summary of results (w/ perl scripts)
*/
process runSummaryCal07 {
    executor 'slurm'
    queue myQueue
    memory "$viremaMem GB"
    module perlMod
    publishDir cal07Path, mode: 'link'

    input:
    file in_cal07 from virema_sumb

    output:
    file "*.par5*"

    """
    perl ${projectPath}/src/Brooke-DARPA/parse-recomb-results-Fuzz.pl -d 5 -i $in_cal07 -o ${in_cal07.baseName}.par5
    """
}
