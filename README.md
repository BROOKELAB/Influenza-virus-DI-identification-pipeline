# Influenza-virus-DI-identification-pipeline
Repo for Chris Brooke's DARPA project

DESCRIPTION
------------------------------


LICENSE
------------------------------

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>

CITATIONS
------------------------------



DEPENDENCIES
------------------------------

This program expects the following tools/languages to be installed as modules and be available in your path:

- Nextflow    tested with version 0.27.3 ( download page https://github.com/nextflow-io/nextflow/releases?after=v0.29.0-RC1 )
- Trimmomatic tested with version 0.36 ( download page https://github.com/timflutre/trimmomatic)
- FastQC      tested with version 0.11.5  ( download page https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
- Bowtie2     tested with 2.3.2 ( download page  http://bowtie-bio.sourceforge.net/bowtie2/index.shtml)
- Bowtie      tested with version 1.2.0 ( download page http://bowtie-bio.sourceforge.net/index.shtml)
- Python      tested with version 2.7.13 ( download page https://www.python.org/downloads/)
- Perl        tested with version 5.24.1  ( download page https://www.perl.org/ )
- ViReMa      tested with ViReMa-with-fuzz ( included in this repo )


INSTALLATION INSTRUCTIONS
------------------------------
- Install all dependencies first. You may need to have root access to install some of these tools/languages on a cluster.
- Do not forget to launch the 'hello world' nextflow pipeline (as per https://www.nextflow.io/) to make sure it works fine.
- Make a copy of this repo


INDEXING THE GENOME(S)
------------------------------
Each genome needs TWO indices, one for Bowtie and one for Bowtie2

- Run this command to index the genome for Bowtie: <i>bowtie-build genome.fasta genome </i>
- Run this command to index the genome for Bowtie2: <i>bowtie2-build genome.fasta genome </i>

RUNNING THE PROGRAM
------------------------------
This pipeline expects each sample to be made up of paired reads of viral RNA.
The sample(s) to be analyzed by this pipeline must be placed together in the same folder.
Prepare a configuration file. Some examples of configuration files are provided in the folder customizable-pipeline-config-files

To run the pipeline type this command: <i> nextflow -c config.file full-pipeline-customizable-v2.nf </i>



OUTPUTS
------------------------------

Nextflow generates two folders to keep track of execution progress. You can delete them once the execution ends successfully. They are called <i>.nextflow/ </i> and <i>work/ </i>

The actual results are placed in these folders: 
- <b>trimmomatic/</b>  contains the results of QC, filter and trim of the raw reads with Trimmomatic
- <b>fastqc_trim/</b>  contains the results of FastQC on the trimmed reads
- <b>bowtie2/</b>      contains the results of aligning the trimmed reads to the genome with Bowtie2
- <b>virema/</b>       contains the results of running ViReMa on the unaligned reads to detect DIP-associated deletion junctions. Each sample will have several files with intermediary and final results. The final results are the files ending in <i> *.par </i>  <i> *.par5 </i> or <i> *par.50 </i>



DOWNSTREAM ANALYSIS: COMPUTE SUMMARY MATRIX
------------------------------
If you want to compare the DIP results of two or more samples together on a per-segment level, then follow these steps to generate a comparison matrix

- Create a folder
- For each sample that you want to compare copy the <i>*.par</i> file to this folder
- Run the analysis with this command: 

  <i>perl  CreateMatrix_DI_VarDepth.pl -d outputdir -o outputfile.tsv -f 1 -v cutoff.txt </i>

Where <i> cutoff.txt </i> is a file with variable read support cutoff values.

If this file is NOT available, then run the analysis with this command: 

  <i>perl  CreateMatrix_DI_VarDepth.pl -d outputdir -o outputfile.tsv -f 1 -m 5 </i>
  
Where <i> -m 5 </i> is a fixed read support value of 5
