# Influenza-virus-DI-identification-pipeline

# DESCRIPTION

The mechanisms and consequences of defective interfering particle (DIP) formation during influenza A virus (IAV) infection remain poorly understood. The development of next generation sequencing (NGS) technologies have made it possible to identify large numbers of DIP-associated sequences, providing a powerful tool to better understand their biological relevance. 

However, NGS approaches pose numerous technical challenges, including the precise identification and mapping of deletion junctions in the presence of frequent mutation and base-calling errors, and the potential for numerous experimental and computational artifacts. 

We developed an Illumina-based sequencing framework and bioinformatics pipeline capable of generating highly accurate and reproducible profiles of DIP-associated junction sequences.  The pipeline is linux-based. This tutorial will illustrate the use of this framework with real data. The first part will focus on DIP detection and the second part will focus on DIP-junction comparison.

We have published a manuscript describing this framework here: DOI:10.1128/JVI.00354-19 

# WORKFLOW OF THE PIPELINE

![Alt text](docs/workflow.jpg?raw=true "Workflow")

The first two steps are done manually: Sample collection, fluidigm library preparation and sequencing in an Illumina platform.
The pipeline performs steps three thorugh five and generates DIPs.
Finally, the last comparative analysis step can be performed by running the programs that also come with this pipeline.

# DEPENDENCIES

This pipeline expects the following tools/languages to be installed as *linux modules* (http://modules.sourceforge.net/) and be available in your path:

- <b>Nextflow</b>    tested with version 19.07.0 ( download page https://github.com/nextflow-io/nextflow/releases )
- <b>Trimmomatic</b> tested with version 0.38 ( download page https://github.com/timflutre/trimmomatic )
- <b>fastp</b>       tested with version 0.20.0 ( download page https://github.com/OpenGene/fastp )
- <b>MultiQC</b>     tested with version 1.7 ( download page https://github.com/ewels/MultiQC )
- <b>seqtk</b>       tested with version 1.2 ( download page https://github.com/lh3/seqtk )
- <b>FastQC</b>      tested with version 0.11.5  ( download page https://www.bioinformatics.babraham.ac.uk/projects/fastqc/ )
- <b>Bowtie2</b>     tested with 2.3.2 ( download page  http://bowtie-bio.sourceforge.net/bowtie2/index.shtml )
- <b>Bowtie</b>      tested with version 1.2.0 ( download page http://bowtie-bio.sourceforge.net/index.shtml )
- <b>Python</b>      tested with version 2.7.13 ( download page https://www.python.org/downloads/ )
- <b>Perl</b>        tested with version 5.24.1  ( download page https://www.perl.org/ )
- <b>ViReMa</b>      tested with ViReMa-with-fuzz ( included in this repo )
- <b>Java</b>        tested with version 1.8.0_152-b16 ( download page https://www.java.com/en/download/help/linux_x64_install.xml )

# INSTALLATION INSTRUCTIONS

- Install all dependencies first. You may need to have root access to install some of these tools/languages on a cluster.
- Install NextFlow by running the following commands:

<pre>

# Make sure that Java v1.7+ is installed:
java -version

# Install Nextflow
curl -fsSL get.nextflow.io | bash

# Add Nextflow binary to your PATH:
mv nextflow ~/bin

# OR make a system-wide installation (root user)
sudo mv nextflow /usr/local/bin

</pre>

- Do not forget to launch the 'hello world' nextflow pipeline (as per https://www.nextflow.io/) to make sure it works fine.
- Install this pipeline: The pipeline itself does not need installation. Simply copy this repo to a local folder and nextflow should be able to run it


# RUNNING THE PIPELINE

- This pipeline expects each sample of viral RNA to be made up of short Illumina reads (single-end or paired-end). We tested the pipeline with avian flu strains.
- The sample(s) to be analyzed by this pipeline must be placed together in the same folder and must have a similar file naming patter; for example, all files should end in fastq | fq | fastq.gz | fq.gz
- Prepare a configuration file.  Some examples of configuration files are provided in the folder <b>new-config-files/</b>
- To run the pipeline type this command at the prompt: 

<pre>
nextflow -c config.file full-pipeline-customizable-v3.nf
</pre>

Execution progress messages will be printed to the screen like this:

<pre>
N E X T F L O W  ~  version 19.07.0
Launching `../full-pipeline-customizable-v3.nf` [compassionate_swanson] - revision: e787d00a80
===================================
DIP-pipeline  ~  version 3.0
===================================
Reference      : /somepath/genome/all_h9n2.fasta
Reads          : /somepath/data/raw-seq-tiny/*.fq
Data Type      : Single-End
Read prep tool : fastp
fastp version  : fastp/0.20.0-IGB-gcc-4.9.4
autodetect adapter: true
Forward adapter seq: false
Reverse adapter seq: false
trim Ns        : true
bowtie2 version: Bowtie2/2.3.2-IGB-gcc-4.9.4
bowtie2 aln options: L,0,-0.3
bowtie1 version: Bowtie/1.2.0-IGB-gcc-4.9.4
ViRema path    : /somepath/apps/ViReMa_with_Fuzz
ViRema micro   : 20
ViRema defuzz  : 3
ViRema mismatch: 1
ViRema --X option: 8
scripts dir    : /somepath/src
Output dir     : /somepath/results/pilot-w-tiny
Working dir    : /somepath/src/work
Current home   : /somepath/userid
Current user   : userid
Current path   : /somepath/src/
E-mail Address : userid@somedomain.edu
=========================================
[skipped  ] process > bowtie2Index_genome (all_h9n2.fasta)   [100%] 1 of 1, stored: 1 ✔
[skipped  ] process > bowtie1Index_genome (all_h9n2.fasta)   [100%] 1 of 1, stored: 1 ✔
[bd/6e389c] process > readPrep_fastp (reads: pooled_HVP2-... [100%] 7 of 7, cached: 7 ✔
[ad/6f44e1] process > readPrep_MultiQC_fastp                 [100%] 1 of 1, cached: 1 ✔
[fb/16a204] process > runbowtie2 (pooled_HVP2-tiny-1M)       [100%] 7 of 7, cached: 7 ✔
[d7/d105ce] process > runVirema (pooled_HVP2-tiny-1M)        [100%] 7 of 7, cached: 7 ✔
[cf/fd2d1d] process > calcSummary (pooled_HVP2-tiny-1M)      [100%] 7 of 7, cached: 7 ✔
[skipping] Stored process > bowtie1Index_genome (all_h9n2.fasta)
[skipping] Stored process > bowtie2Index_genome (all_h9n2.fasta)
[DIP-pipeline] COMPLETED. Sent summary e-mail to userid@somedomain.edu


</pre>

# OUTPUTS

Nextflow generates two folders to keep track of execution progress. You can delete them once the execution ends successfully. They are called <i>.nextflow/ </i> and <i>work/ </i>

The actual results of the pipeline are placed in these folders:

- <b>read-preparation/</b>  contains the results of QC, filter and trim of the raw reads with Trimmomatic or with fastp
- <b>fastqc/</b>       contains the results of FastQC on  raw and trimmed reads
- <b>align/</b>      contains the results of aligning the trimmed reads to the genome with Bowtie2
- <b>virema/</b>       contains the results of running ViReMa on the unaligned reads to detect DIP-associated deletion junctions. Each sample will have several files with intermediary and final results. The final results are the files ending in <i> *.par </i>  <i> *.par5 </i> or <i> *par.50 </i>



# DOWNSTREAM ANALYSIS: COMPUTE SUMMARY MATRIX

If you want to compare the DIP results of two or more samples together on a per-segment level, then follow these steps to generate a comparison matrix

- Create a folder
- For each sample that you want to compare copy the <i>*.par</i> file to this folder
- Run the analysis with this command: 

<pre>
perl  CreateMatrix_DI_VarDepth.pl -d outputdir -o outputfile.tsv -f 1 -v cutoff.txt
</pre>


Where <i> cutoff.txt </i> is a file with variable read support cutoff values.

If this cutoff file is NOT available, then run the analysis with this command: 

<pre>
perl  CreateMatrix_DI_VarDepth.pl -d outputdir -o outputfile.tsv -f 1 -m 5
</pre>
  
Where <i> -m 5 </i> is a fixed read support value of 5

# DOWNSTREAM ANALYSIS: Fuzz values

The program <i>parse-recomb-results-Fuzz.pl</i> summarizes the results given in the Virus_Recombination_Results.txt file produced by ViReMa. This takes Fuzz factor values into account as well.

To run the program type:

<pre>

perl parse-recomb-results-Fuzz.pl -d 5 -i $infile -o $outfile

where:
-d <value> to specify the minimum depth needed to retain a DI
-i <file>  must be a Virus_Recombination_Results.txt generated by ViReMa
-o <file>  output file 

</pre>


# PERFORMANCE ISSUES

The performance of ViRema depends on many factors, the two main ones are the size of the input file of <b>unaligned reads</b> and the amount of compute resources (CPUs and memory) that are allocated to the process.

Large input files have a detrimental effect on the performance of ViRema; in fact, very large input files will break the tool as it will eventually starve for memory.

The most likely causes of large files of <b>unaligned reads</b>  are: 
- a) the viral genome has many structural features that regular aligners like bowtie cannot cope with, 
- b) the original file of raw reads has extremely high coverage, 20,000x or higher, 
- c) the sample has RNA from other sources like the host

ViRema was written to address the scenario in a); it has a hard time with the other two scenarios. We address these last two cases by downsampling the file of unaligned reads. You can specify how many reads to downsample to in the configuration file.

<d>How much coverage is recommended - i.e. how many reads should my input file have?</d> Unfortunately we have not found a published ViRema benchmark that would address this question directly. However, our empirical tests show tha a coverage between 1,000x and 10,000x works fine; whereas a coverage of 20,000x or higher has a detrimental effect of performance.

# LICENSE


This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>

# CITATIONS



