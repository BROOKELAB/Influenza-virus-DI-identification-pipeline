# Workflow of the pipeline

![Alt text](../docs/workflow.jpg?raw=true "Workflow")

The first steps are done manually: Sample collection, fluidigm library preparation and sequencing in an Illumina platform.
The nextflow pipeline performs steps three thorugh five and generates DIPs.
Finally, the comparative analysis can be performed with programs provided here

# Sample collection, fluidigm library preparation and sequencing

![Alt text](../docs/IAV_sample_prep.jpg?raw=true "SamplePreparation")


## download these fastq files from our page

Our fastq files are paired-ended reads. These files have been demultiplexed and sorted by primer.

- Total paired reads in 6E: 505,962  Read length between 35-250
- Total paired read in 11E: 434,035  Read length between 35-250

They are available for download from:  (some-data-hosting-place/testdata/raw-seq)

Create a folder called *data/raw-seq* and copy these fastq files to that folder

<pre>

# create a new folder for these input files

mkdir -p data/raw-seq/runE-Cal07

# go to that folder

cd data/raw-seq/runE-Cal07

# download the files

wget some-data-hosting-place/testdata/raw-seq/* 

</pre>

## or DIY: 

Sample 6E: Details will be provided by Fadi

Sample 11E: Details will be provided by Fadi

# Genome preparation

## download the genomes from our page

The flu genomes in fasta format and the corresponding index files are available for download from:
(some-data-hosting-place/testdata/genomes)

Create a folder called *data/genomes* and copy all files files to that folder

<pre>

# create a new folder called genomes inside the folder data
mkdir -p data/genomes

# go to that folder

cd data/genomes

# download the files

wget some-data-hosting-place/testdata/genomes/*

</pre>


## or DIY:

- get the fasta files of the flu genomes

download site of PR8 genome : https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=183764

download site of Cal07 : https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=1970186

- pad the genomes  to make ViReMa happy

ref-simple-Cal07.fasta  becomes ref-padded-Cal07.fasta

modified_PR8_ref.fasta becomes modified_PR8_ref_padded.fasta


- index the genomes with bowtie2 for the alignemnt step

<pre>
module load Bowtie2/2.3.2
bowtie2-build ref-simple-Cal07.fasta bowtie2-2.3.2-index/Cal07
bowtie2-build modified_PR8_ref.fasta bowtie2-2.3.2-index/modified_PR8
</pre>

- index the genomes with bowtie for the DI detection step with ViReMa

<pre>
module load Bowtie/1.2.0
bowtie-build ref-padded-Cal07.fasta bowtie-1.2.0-index/Cal07_padded
bowtie-build modified_PR8_ref_padded.fasta bowtie-1.2.0-index/modified_PR8_ref_padded
</pre>


# Running the pipeline 

## Installation instructions: 

Please follow this link: ![Installation Instructions](../README.md)

## Configure some parameters

- Trimmomatic trimming parameters can be adjusted to work with your own datasets.
- Bowtie2 alignment parameters can be tweaked to increase alignment accuracy.
- ViReMa parameters can be tweaked to increase DIP detection accuracy.

![Alt text](../docs/benchmarks.jpg?raw=true "Benchmarks")

The results of our benchmarks with synthetic and real datasets are shown above 
and demonstrate that the following values work well for Trimmomatic, bowtie2 and ViReMa:

<pre>
Trimmomatic 'ILLUMINACLIP:$TRIMMOMATICPATH/adapters/TruSeq3-PE-2.fa:2:15:10 SLIDINGWINDOW:3:20 LEADING:28 TRAILING:28 MINLEN:75'
bowtie2  --score-min  'L,0,-0.3' 
ViReMa --MicroInDel 20
ViReMa --N  1
ViReMa --X  8
ViReMa --defuzz 3
</pre>

However, you do not have to take our word for it. Simply change the values in the configuration file.
One such configuration file is provided here: ![runE-Cal07-setup3.conf](conf/runE-Cal07-setup3.conf).

Additional information that can also be specified inside the configuration file rather than at the command line include 

- input and output folders
- path to reference genome
- cluster resources such as memory and CPUs

It is important to put in the same input folder all fastq files that are going to be analyzed together by the same pipeline and with the same parameters. 

To run the pipeline type these commands:

<pre>

# load the Nextflow module

module load Nextflow

# run the pipeline

nextflow run    -c  conf/runE-Cal07-setup3.conf    full-pipeline-customizable-v2.nf

</pre>

## Examine the results

You should see FOUR folders with results as shown here
















