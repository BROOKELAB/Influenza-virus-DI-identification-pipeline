ViReMa Version 0.6
Last Modified: 6-6-14

Test Data - FHV (8 files)
- FHV_10k.txt		Contains ten thousand reads from the Flock House Virus Dataset: SRP013296
- FHV_Genome_padded.txt	Contains reference genes for Flock House Virus with long 3' terminal A residues.
- FHV_Genome_padded.*.ebwt 	These are the built index sequences for the FHV padded genome using Bowtie-Build v0.12.9

Compiler_Module.py
Module or Stand-alone script used to compile output results from ViReMa.py.  Runs from Command-line.

ConfigViReMa.py
This script carries the global variables used by both ViReMa.py and Compiler_Module.py

README.txt
Includes instructions to run ViReMa.

Updata_notes_ViReMa_0.6.txt
List of changes since 0.5.

ViReMa.py
Runs ViReMa (Viral-Recombination-Mapper) from commmand line.



Before you Start:

ViReMa is a simple python script and so should not require any special installation.  

ViReMa requires python version 2.7 and Bowtie version 0.12.9. ViReMa only uses modules packaged as a standard with Python version 2.7. 

Bowtie and Bowtie-Inspect must be in your $PATH.

Indexes for reference genomes must be built with Bowtie-Build. For maximum sensitivity, please add a terminal pad using 'A' nucleotides to the end of your genome sequence before creating virus reference indexes using Bowtie-Build.  This pad must be longer than the length of the reads being aligned.  Without these pads, ViReMa will fail to detect recombination events occuring at the edges of the viral genome. 



ViReMa is run from the command line:

>python ViReMa.py Virus_Index Input_Data Output_Data [args]


Example using test data:

>home/ViReMa0.1/python ViReMa.py Test_Data/FHV_Genome_padded Test_Data/FHV_10k.txt FHV_recombinations.txt --Seed 20 --MicroInDel_Length 5 


ViReMa will take read data and attempt to align it to the reference genomes (Virus first, Host second). If the Seed of the read successfully aligns to a reference genome, bowtie will continue to align the remaining nucleotides after the Seed.Alignment() will extract all the successfully aligned nucleotides and the remaining unaligned nucleotides will be written to a new temporary read file. If there is no succesful alignment, Alignment() will trim one nucleotide from the beginning of the read and report. Again, the remaining nucleotides will be written to a new temporary file which will be used for subsequent alignment.



Required arguments:

  Virus_Index		

Virus genome reference index key. e.g. FHV_Genome
Enter full path if the index is not in the current working directory, even when that index is stored in your Bowtie-0.12.9/indexes folder.  E.g.:  ../../Desktop/Bowtie-0.12.9/indexes/FHV_Genome


  Input_Data            

File containing single reads in FASTQ or FASTA format.


  Output_Data           

Destination file for results.  This is be saved in the current working directory.  



Optional arguments:


  -h, --help            

Show help message and exit


  --Host_Index          

Host genome reference index key, e.g.d_melanogaster_fb5_22  Enter full path if the index is not in the current working directory, even when that index is stored in your Bowtie-0.12.9/indexes folder. E.g.:  ../../Desktop/Bowtie-0.12.9/indexes/d_melanogaster_fb5_22   ViReMa will first attempt to align the seed to the provided virus genome reference index. However, if a mapping cannot be found, then ViReMa will then attempt to map the read to the host genome. In this manner, ViReMa will give preference to any mapping found in the virus genome, even if a better match may have been found in the host genome. If this is unsuitable for some applications, then the user will need to build a single reference index containing both the virus and host genome sequences together and then supply this to ViReMa as if it were the Virus_Index.


  --N                   

Number of mismatches tolerated in mapped seed and in mapped segments. Default is 1.


  --ThreePad 		

Number of nucleotides not allowed to have mismatches at 3' end of segment. Default is 5.


  --FivePad 		

Number of nucleotides not allowed to have mismatches at 5' end of segment. Default is 5.

  --X

Number of nucleotides not allowed to have mismatches at 3'  and 5' end of segment. Same as setting --FivePad and --ThreePad seperately.  Default is 5.  See Routh et al.

  --Seed 		

Number of nucleotides in the Seed region. Default is 25.

  --Host_Seed 		

Number of nucleotides in the Seed region when mapping to the Host Genome. Default is same as Seed value.

  -F                    

Select '-F' if data is in FASTA format fasta. Default is FASTQ.
	
  --Defuzz 		

Choose how to defuzz data: '5' to report at 5' end of  fuzzy region, '3' to report at 3' end, or '0' to report in centre of fuzzy region. Default is no fuzz handling.  Due to possible overlap between the Donor segments and the region immediatelty upstream of the acceptor segment, there may be ambiguity as to the position of the actual recombination event.  Due to the mapping algorithm that ViReMa uses, ViReMa will always push toward the 3' end of any ambiguity.  This can be corrected by finding any ambiguous nucleotides and adjusting accordingly.

  --MaxFuzz

Select maximum allowed length of fuzzy region. Recombination events with longer fuzzy regions will not be reported. Default is Seed Length.

  -DeDup                

Remove potential PCR duplicates. This will remove any identical entries in the initial report in the case that they are PCR duplicates.  With this option selected, all detected recombination events will be unique, meaning that highly populated recombination events have multiple unique reads that describe them. Default is 'off'.


  --MicroInDel_Length	

Size of MicroInDels - these are common artifacts of cDNA preparation. See Routh et al JMB 2012. Default size is 0.  Any recombination event that is a MicroInDel will be written out to a seperate file name Virus_MicroInsertions/Virus_MicroDeletions or Host_MicroInsertions/Host_MicroDeletions.  


  --Compound_Handling 	

Select this option for compound recombination event mapping. Enter number of nucleotides to map (must be less than Seed, and greater than MicroInDel). Default is off. Compound_Handling will determine whether trimmed nucleotides found between recombination sites are present between the donor and accpetor sites for these two recombination events. If so, they are assumed to have arisen due to multiple recombination events occuring within close proximity. This is only a good assumption in viral genomes (where the number if possible matches is low) and when there are sufficient nucleotides in the trimmed sequence.


  --Output_Tag 		

Enter a tag name that will be appended to the beginning of each output file. 


  --Output_Dir 		

Enter a directory name that all compiled output files will be saved in. ViReMa will check first to make sure that Dir does not already exist.  If it does, a time stamp will be appended after the name in order to prevent over-writing any data.


  --p 			

Enter number of available processors. Default is 1.  This value is passed to the Bowtie command to allow parallelisation of the Bowtie search.
(Not available in Windows version).

  --Chunk

Enter number of reads to process together.

  --Aligner

Enter Alignment Software: 'bwa', 'bowtie'. Default is bowtie.

  -No_Compile           

Select this option if you do not wish to compile the results file. Maybe useful when combining results from multiple datasets.  The output results file(s) can by compiled later by using the seperate Compiler_Module.py script.  All input options for this module are the same as for the main ViReMa.py script.  

  -BED

"Output recombination data into BED files."

This option will output the Virus and Host Recombination results into an ouput files called Virus_Recombination_Results.bed, Virus_MicroRecombination_Results.bed, Host_Recombination_Results.bed and Host_MicroRecombination_Results.bed, within a subdirectory called BED_Files in the output_directory specified by the user.  These are BED6 files (with version 0.5.1) and so can be read into, for example, the Interactive Genome Viewer (IGV).  Only intra-gene recombination are compatible with this format (with version 0.5.1).  Inter-gene recombinations will be handled using alternative BED formats in a later version.  BED files have with 'graphType=junctions' in the track name and so can be displayed similarly to splice junctions.

Will also write out a BEDGraph file illustrating conservation over virus genome as demonstrated in Figure 4, Routh et al NAR 2014 Jan 42(2):e11

  -Win

Select this option if running ViReMa from a Windows/Cygwin shell




Compilation_Module

ViReMa will automatically begin to Compile the results into multiple output files unless -No_Compile is selected.
To run this compilation module seperatly:

>python Compilation_Module.py Virus_Index Input_Data [args]

Here, the input data is the output data from ViReMa.py. All optional arguments are the same as for ViReMa.py

Example using Test_Data:

>home/ViReMa-0.1/Compiler_Module.py Test_Data/FHV_Genome_padded FHV_recombinations.txt --Output_Dir New_Results --Seed 20 --MicroInDel_Length 5 --Compound_Handling 10 --Defuzz 0



Output files: 

Insertions, MicroInsertions, MicroDeletions, Recombination_Results, Single_Alignments, Substitutions, UnMappedReads and Unknown_Recombinations. If both host and virus reference genomes are used, there will be one file for each reference genome, plus an extra file for virus-to-host recombinations. If multiple reads are present that contain the same recombination junction, then these are summed and reported together.


The results for each event are written as: ‘145_to_1103_#_1’, under a file-header that gives the gene names (e.g. @NewLibrary: FHVRNA1_to_FHVRNA2_ReverseStrand). The first field denotes the 5’ recombination breakpoint, the third field denotes the 3’ recombination breakpoint and the fifth field denotes the frequency with which this event was detected. If multiple reads are present that contain the same recombination junction, then these are summed and reported together; e.g.: ‘145_to_1103_#_453’.
