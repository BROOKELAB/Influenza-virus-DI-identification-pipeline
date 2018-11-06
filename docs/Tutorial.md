# Introduction
The mechanisms and consequences of defective interfering particle (DIP) formation during influenza A virus (IAV) infection remain poorly understood. The development of next generation sequencing (NGS) technologies have made it possible to identify large numbers of DIP-associated sequences, providing a powerful tool to better understand their biological relevance. 

However, NGS approaches pose numerous technical challenges, including the precise identification and mapping of deletion junctions in the presence of frequent mutation and base-calling errors, and the potential for numerous experimental and computational artifacts. 

We developed an Illumina-based sequencing framework and bioinformatics pipeline capable of generating highly accurate and reproducible profiles of DIP-associated junction sequences.  This tutorial will illustrate the use of this framework with real data. The first part will focus on DIP detection and the second part will focus on DIP-junction comparison.


# Sample preparation and sequencing

Sample 6E: Details will be provided by Fadi

Sample 11E: Details will be provided by Fadi

## download these fastq files from our page

The files with paired reads in fastq format are available for download from:
(some-data-hosting-place/testdata/raw-seq)


# Genome preparation


## get the fasta files of the flu genomes

download site of PR8 genome : https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=183764

download site of Cal07 : https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=1970186

## padding the genomes  to make ViReMa happy

ref-simple-Cal07.fasta  becomes ref-padded-Cal07.fasta

modified_PR8_ref.fasta becomes modified_PR8_ref_padded.fasta


## index the genomes with bowtie2 for the alignemnt step

<pre>
module load Bowtie2/2.3.2
bowtie2-build ref-simple-Cal07.fasta bowtie2-2.3.2-index/Cal07
bowtie2-build modified_PR8_ref.fasta bowtie2-2.3.2-index/modified_PR8
</pre>

## index the genomes with bowtie for the DI detection step with ViReMa

<pre>
module load Bowtie/1.2.0
bowtie-build ref-padded-Cal07.fasta bowtie-1.2.0-index/Cal07_padded
bowtie-build modified_PR8_ref_padded.fasta bowtie-1.2.0-index/modified_PR8_ref_padded
</pre>

## download the genomes from our page

The flu genomes in fasta format and the corresponding index files are available for download from:
(some-data-hosting-place/testdata/genomes)

# Running the pipeline 

## Installation instructions: 

Add a link to README.md

## Prepare a configuration file for the run.

Add a link to the config.file







