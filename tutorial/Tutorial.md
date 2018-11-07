# Workflow of the pipeline

![Alt text](../docs/workflow.jpg?raw=true "Workflow")

The first steps are done manually: Sample collection, fluidigm library preparation and sequencing in an Illumina platform.
The nextflow pipeline performs steps three thorugh five and generates DIPs.
Finally, the comparative analysis can be performed with programs provided here

# Sample collection, fluidigm library preparation and sequencing

![Alt text](../docs/IAV_sample_prep.jpg?raw=true "SamplePreparation")


## download these fastq files from our page

The files with paired reads in fastq format are available for download from:
(some-data-hosting-place/testdata/raw-seq)

## or DIY: 

Sample 6E: Details will be provided by Fadi

Sample 11E: Details will be provided by Fadi

# Genome preparation

## download the genomes from our page

The flu genomes in fasta format and the corresponding index files are available for download from:
(some-data-hosting-place/testdata/genomes)

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

- Bowtie2 alignment parameters can be tweaked to increase alignment accuracy.
- ViReMa parameters can be tweaked to increase DIP detection accuracy.

![Alt text](../docs/benchmarks.jpg?raw=true "Benchmarks")

Our benchmarks with synthetic and real datasets show that these values for bowtie2 and ViReMa increase accuracy of the pipeline

<pre>
bowtie2  --score-min  'L,0,-0.3' 
ViReMa --MicroInDel 20
ViReMa --N  1
ViReMa --X  8
ViReMa --defuzz 3
</pre>

Create a configuration file where you can specify paths to input and output folders, cluster resources, and parameter values.
One such configuration file is provided here: ![runE-Cal07-setup3.conf](conf/runE-Cal07-setup3.conf)











