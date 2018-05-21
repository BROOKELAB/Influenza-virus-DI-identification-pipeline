#!/usr/bin/env nextflow
/*
* USAGE: nextflow run myscript.nf -qs 8
* Note that "-qs" is similar to "#PBS -t" and will only run a specified # of jobs at a time.
* This script creates hard links to data that exists in nextflows work directory.
*/

/*
 * Set parameter values here. Only change the values within quotations
 * Many of the values already present will be okay to use, but make sure the pathes
 * are correct for your dataset.
*/

/*Path to project folder*/
projectPath = "/home/groups/hpcbio_shared/cbrooke_lab"

/* Paths to bowtie indices */
bowtie2_index = file("$projectPath/data/genome/bowtie2-2.3.2-index/modified_PR8*")


/* Path to raw fastq files */
rawDataPath = "$projectPath/src/2and44"
Channel
    .fromFilePairs("$rawDataPath/*_R{1,2}_001.fastq", flat: true)
    .ifEmpty {error "Cannot find any reads matching: ${params.reads}"}
    .set {reads}

/*Biocluster options. List memory in gigabytes like in suggestions below*/
myQueue = 'normal'
trimMemory = '15'
trimCPU = '6'
bowtie2Mem = '15'
bowtie2CPU = '6'


/*Module versions*/
trimMod = 'Trimmomatic/0.36-Java-1.8.0_121'
trimVersion = '0.36' /*Put the version here only*/
fastqcMod = 'FastQC/0.11.5-Java-1.8.0_92'
bowtie2Mod = 'Bowtie2/2.3.1-IGB-gcc-4.9.4'

/*
* Trimming options. Change trimming options here and note that $trimVersion is used to make sure
* the version is called consistently.
*/
trimOptions = 'ILLUMINACLIP:$EBROOTTRIMMOMATIC/adapters/TruSeq3-PE-2.fa:2:15:10 LEADING:28 TRAILING:28 MINLEN:30'

/* Alignment & Counting options */
scoreMin = 'L,0,-0.01' /* This is the value for --score-min */

/*Output paths*/
trimPath = "$projectPath/results/Aug2017-real-nextflow/trimmomatic"
fastqcPath = "$projectPath/results/Aug2017-real-nextflow/fastqc_trim"
alignPath = "$projectPath/results/Aug2017-real-nextflow/bowtie2"


/*
* Step 1. Trimming
* WARNING: considers '1' a valid exit status to get around wrapper error
*/

process trimmomatic {
    executor 'slurm'
    cpus trimCPU
    queue myQueue
    memory "$trimMemory GB"
    module trimMod
    publishDir trimPath, mode: 'link'
    validExitStatus 0,1

    input:
    set val(id), file(read1), file(read2) from reads

    output:
    set val(id), "${read1.baseName}.qualtrim.paired.fastq", "${read2.baseName}.qualtrim.paired.fastq" into fastqChannel
    set val(id), "${read1.baseName}.qualtrim.paired.fastq", "${read2.baseName}.qualtrim.paired.fastq" into catChannel
    file "*.trimmomatic.log"
    file "*.qualtrim.unpaired.fastq"
    stdout trim_out

    """
    java -jar \$EBROOTTRIMMOMATIC/trimmomatic-${trimVersion}.jar PE \
    -threads $trimCPU -phred33 -trimlog ${id}.trimmomatic.log ${read1} ${read2} \
    ${read1.baseName}.qualtrim.paired.fastq ${read1.baseName}.qualtrim.unpaired.fastq \
    ${read2.baseName}.qualtrim.paired.fastq ${read2.baseName}.qualtrim.unpaired.fastq $trimOptions
    """
}


/*
* Step 2. FASTQC of trimmed reads
*/
process runFASTQC {
    executor 'slurm'
    cpus 1
    queue myQueue
    memory '2 GB'
    module fastqcMod
    publishDir fastqcPath, mode: 'link'

    input:
    set pair_id, file(read1), file(read2) from fastqChannel

    output:
    file "*.html"
    file "*.zip"

    """
    fastqc -o ./ --noextract ${read1}
    fastqc -o ./ --noextract ${read2}
    """
}

/*
* Step 3. Combine FASTQ pairs
*/

process combineFASTQ {
    executor 'slurm'
    queue myQueue
    publishDir trimPath, mode: 'link'

    input:
    set pair_id, file(read1), file(read2) from catChannel

    output:
    file  "*_both.fq" into bowtie2_channel


    """
    cat ${read1} ${read2} > ${pair_id}_both.fq
        """
}

/*
* Step 4. Bowtie2 alignment
*/

process runbowtie2 {
    executor 'slurm'
    cpus bowtie2CPU
    queue myQueue
    memory "$bowtie2Mem GB"
    module "$bowtie2Mod"
    publishDir alignPath, mode: 'link'


    input:
    file bowtie2_index
    file in_cat from bowtie2_channel

    output:
        file "*_unaligned.fq"
        file "*.sam"
        file "*_aligned.fq"

    """

    bowtie2 -p $bowtie2CPU -x $projectPath/data/genome/bowtie2-2.3.1-index/ref-simple-Cal07.fasta -U ${in_cat} --score-min $scoreMin \
    --al ${in_cat.baseName}_aligned.fq --un ${in_cat.baseName}_unaligned.fq > ${in_cat.baseName}.sam

    """
}

