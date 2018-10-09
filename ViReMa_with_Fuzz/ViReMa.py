##      Copyright (c) 2013-2014 Andrew Laurence Routh
##      
##      Permission is hereby granted, free of charge, to any person obtaining a copy
##      of this software and associated documentation files (the "Software"), to deal
##      in the Software without restriction, including without limitation the rights
##      to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
##      copies of the Software, and to permit persons to whom the Software is
##      furnished to do so, subject to the following conditions:
##      
##      The above copyright notice and this permission notice shall be included in
##      all copies or substantial portions of the Software.
##      
##      THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
##      IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
##      FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
##      AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
##      LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
##      OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
##      THE SOFTWARE.
##
##      ----------------------------------------------------------------------------------------
print '\n-------------------------------------------------------------------------------------------'
print 'ViReMa Version 0.9 - written by Andrew Routh'
print 'Last modified 31/01/2014'
print '-------------------------------------------------------------------------------------------'
##      ----------------------------------------------------------------------------------------

import time
start = time.time()
from subprocess import call
from re import findall
import argparse
from Compiler_Module import *
import ConfigViReMa as cfgvars
from os import makedirs
from os.path import exists
import sys

##      -------------------------------------------------------------------------------------------
##      Take arguments from command line, and send them to the config file for cross-module access
##      -------------------------------------------------------------------------------------------

if __name__ =='__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument("Virus_Index", help="Virus genome reference index key. e.g. FHV_Genome")
        parser.add_argument("--Host_Index", help="Host genome reference index key, e.g. d_melanogaster_fb5_22")
        parser.add_argument("Input_Data", help= "File containing single reads in FASTQ format")
        parser.add_argument("Output_Data", help= "Destination file for results")
	parser.add_argument("--N", help= "Number of mismatches tolerated in mapped seed and in mapped segments. Default is 1.")
	parser.add_argument("--Seed", help="Number of nucleotides in the Seed region. Default is 25.")
	parser.add_argument("--ThreePad", help="Number of nucleotides not allowed to have mismatches at 3' end of segment. Default is 5.")
	parser.add_argument("--FivePad", help="Number of nucleotides not allowed to have mismatches at 5' end of segment. Default is 5.")
	parser.add_argument("--X", help="Number of nucleotides not allowed to have mismatches at 3' end and 5' of segment. Overrides seperate ThreePad and FivePad settings. Default is 5.")
        parser.add_argument("--Host_Seed", help="Number of nucleotides in the Seed region when mapping to the Host Genome. Default is same as Seed value.")
        parser.add_argument("-F", action='store_true', help="Select '-F' if data is in FASTA format fasta. Default is FASTQ.")
        parser.add_argument("--Defuzz", help="Choose how to defuzz data:  '5' to report at 5' end of fuzzy region, '3' to report at 3' end, or '0' to report in centre of fuzzy region. Default is no fuzz handling (similar to choosing Right - see Routh et al).")
        parser.add_argument("--MaxFuzz", help="Select maximum allowed length of fuzzy region. Recombination events with longer fuzzy regions will not be reported. Default is Seed Length.")
	parser.add_argument("-DeDup", action='store_true', help="Remove potential PCR duplicates. Default is 'off'.")
        parser.add_argument("-ReadNamesEntry", action='store_true', help="Append Read Names contributing to each compiled result. Default is off.")
        parser.add_argument("--MicroInDel_Length", help= "Size of MicroInDels - these are common artifacts of cDNA preparation.  See Routh et al JMB 2012. Default size is 0)")
        parser.add_argument("--Compound_Handling", help= "Select this option for compound recombination event mapping (see manual for details). Enter number of nucleotides to map (must be less than Seed, and greater than number of nts in MicroInDel). Default is off.")
        parser.add_argument("--Output_Tag", help= "Enter a tag name that will be appended to end of each output file.")
        parser.add_argument("--Output_Dir", help= "Enter a directory name that all compiled output files will be saved in.")
        parser.add_argument("--p", help= "Enter number of available processors. Default is 1.")
        parser.add_argument("--Chunk", help= "Enter number of reads to process together.")
	parser.add_argument("--Aligner", help="Enter Alignment Software: 'bwa', 'bowtie'. Default is bowtie.")
        parser.add_argument("-No_Compile", action='store_true', help= "Select this option if you do not wish to compile the results file into.  Maybe useful when combining results from different datasets.")
        parser.add_argument("-BED", action='store_true', help= "Output recombination data into BED files.")
        parser.add_argument("-CoVaMa", action='store_true', help= "Make CoVaMa output data.")
        parser.add_argument("-Nomm", action='store_true', help= "Select this option if running ViReMa from a Windows/Cygwin shell.")
        args = parser.parse_args()

        cfgvars.Lib1 = str(args.Virus_Index)
        if args.Host_Index:
                cfgvars.Lib2 = str(args.Host_Index)
        else:
                cfgvars.Lib2 = None
        cfgvars.File1 = str(args.Input_Data)
        if not exists(str(args.Output_Data)):
                        cfgvars.File2 = str(args.Output_Data)
        else:
                        print "Output File already exists!  Appending time to directory name to prevent overwrite."
                        cfgvars.File2 = str(args.Output_Data) + str(int(time.time()))
        if args.F:	
		cfgvars.ReadType = '-f'
	else: 
		cfgvars.ReadType = '-q'
        if args.Seed:
                cfgvars.Seed = int(args.Seed)
        else:
                cfgvars.Seed = 25
	if args.N:
		cfgvars.Mismatches = int(args.N)
	else:
		cfgvars.Mismatches = 1
        if args.Compound_Handling:
                cfgvars.Compound_Handling = str(args.Compound_Handling)
        else:
                cfgvars.Compound_Handling = ''
        if args.MicroInDel_Length:
                cfgvars.MicroInDel_Length = int(args.MicroInDel_Length)
        else:
                cfgvars.MicroInDel_Length = 0
	if args.ThreePad:
		cfgvars.ThreePad = int(args.ThreePad)
	else:
		cfgvars.ThreePad = 5
	if args.FivePad:
		cfgvars.FivePad = int(args.FivePad)
	else:
		cfgvars.FivePad = 5
	if args.X:
                cfgvars.FivePad = int(args.X)
                cfgvars.ThreePad = int(args.X)
        else:
                pass
        if args.p:
                cfgvars.Threads = str(args.p)
        else:
                cfgvars.Threads = '1'
        if args.Output_Tag:
                cfgvars.FileTag = str(args.Output_Tag) + "_"
        else:
                cfgvars.FileTag = ''
        if args.Defuzz == '3':
		cfgvars.Defuzz = 'Right'
	elif args.Defuzz == '5':
		cfgvars.Defuzz = 'Left'
	elif args.Defuzz == '0':
		cfgvars.Defuzz = 'Centre'
        else:
                cfgvars.Defuzz = False
        if args.MaxFuzz:
                cfgvars.MaxFuzz = int(args.MaxFuzz)
        else:
                cfgvars.MaxFuzz = cfgvars.Seed
	if args.DeDup:
                cfgvars.DeDup = True
        else:
                cfgvars.DeDup = False
        if args.ReadNamesEntry:
                cfgvars.ReadNamesEntry = True
        else:
                cfgvars.ReadNamesEntry = False
        if args.Aligner == 'bwa':
		cfgvars.Aligner = 'bwa'
	else: 
		cfgvars.Aligner = 'bowtie'
        if args.Chunk:
                cfgvars.Chunk = str(args.Chunk)
        else:
                cfgvars.Chunk = False
        if args.Host_Seed:
                if int(args.Host_Seed) < cfgvars.Seed:
                        cfgvars.Host_Seed = cfgvars.Seed
                else:
                        cfgvars.Host_Seed = int(args.Host_Seed)
        else:
                cfgvars.Host_Seed = cfgvars.Seed
        if args.No_Compile:
                cfgvars.Compile = False
        else:
                cfgvars.Compile = True
        if args.Nomm:
                cfgvars.Nomm = True
        else:
                cfgvars.Nomm = False
        if args.BED:
                cfgvars.BED = True
        else:
                cfgvars.BED = False
        CommandLineEntry = str(sys.argv)
        Report = open(cfgvars.File2,"a")
        Report.write(cfgvars.Lib1 + '\n')
        Report.write(CommandLineEntry + '\n')
        Report.close()
        
##      ----------------------------------------------------------------------------------------
##      Function Countreads will determine the number of complete reads in the given input file.
##      ----------------------------------------------------------------------------------------

def Countreads(File, ReadType):
        with open(File, 'r') as CountReadsIn:
        	NumberofReads = 0
        	for line in CountReadsIn:
                	if ReadType == "Q":
                        	NumberofReads += 0.25
                	elif ReadType == "F":
                        	NumberofReads += 0.5
        return int(NumberofReads)

##      ------------------------------------------------------------------------------------------------------------
##      For each read aligned and output to the temporary SAM file, the function FindReadMapping() will extract
##      data for any succesfully aligning portions of the read, and then write to a new TEMPREADS file any remaining
##      nucleotides that will be mapped in a subsequent alignment iteration. The mapping data is then summarised and
##      returned to functions Alignment() for compiling.
##      ------------------------------------------------------------------------------------------------------------

def FindReadMapping(output, CurrentSeed, Seed):
        if output[2] != '*':
                if len(output[9]) < Seed:    
		#output[9] is the query sequence
                        return "TOOSMALL", "U", "*", "*", output[9], "N"
                else:
			MismatchTag = [i[5:] for i in output if 'MD:Z:' in i][0]
			Align = findall(r"[^\W\d_]+|\d+", MismatchTag)	
			#output[12] is the default mismatches field in bowtie
			flag = bin(int(output[1]))
			#This is the bitwise FLAG from the standard .SAM format.  A flag of '4' means the read is unmapped.
                        if len(flag) > 6 and flag[-5] == '1':		
			#A flag of '16' means the read mapped to the reference in the reverse direction and so needs to be reverse complented to regain to the original read
                                Align = Align[::-1]
                                output[9] = Rev_Comp(output[9])
                                Direction = '_RevStrand_'
                        else:
                                Direction = '_'       
                        if int(Align[0]) <= cfgvars.FivePad:
                                        #Here, a mismatched nucleotide has occcurred too near the 5' end of the mapped read.
                                        #Consequently, this read will be trimmed as if it has not aligned.
                                        #If there is a good mapping, it will be found in a subsequent iteration.
                                        Code = '%sX' % (output[9][0])
                                        if len(output[9][1:]) >= Seed:
                                                return "NONE", Code, "*", "*", str(len(output[9][1:])), "Y", output[9], output[10],
                                        else:
                                                return "NONE", Code, "*", "*", output[9][1:], "N", output[9], output[10]
                        else:
					#Here, we find the number of mapped nucleotides including allowed mismatches (note, mismatches are not allowed at the ends of a segment as determined by the 'ThreePad' and 'FivePad' variables
                                        if cfgvars.Mismatches >= 2 and len(Align) > 3 and int(Align[4]) >= cfgvars.ThreePad:
						#Means if two mismatches are allowed, and if two mismatches are found, and if none of these mismatches are disqualifying
                                        	if Align[2] == '0':
							#Means there are two adjacent but allowed mismatches
							Code = '%sM2X%sM' % (Align[0], Align[4])
						else:
							#Means there are two non-adjacent and allowed mismatches
							Code = '%sM1X%sM1X%sM' % (Align[0], Align[2], Align[4])
					        MappedLength = int(Align[0]) + int(Align[2]) + int(Align[4]) + 2
						#Length of the three mapped sections plus the mismatches
                                        elif cfgvars.Mismatches >= 1 and len(Align) > 1 and int(Align[2]) >= cfgvars.ThreePad:
						#Means if one mismatch is allowed, and if one mismatch is found and it is not disqualifying
                                                MappedLength = int(Align[0]) + int(Align[2]) + 1
						Code = '%sM1X%sM' % (Align[0], Align[2])
                                        else:
						#Means no mismatches were found
                                                MappedLength = int(Align[0])
						Code = '%sM' % (str(MappedLength))
					if int(MappedLength) < CurrentSeed:
                                                #After accounting for disallowed mismatches, the remaining mapped nucleotides are now shorter than the required Seed Length
                                                #Therefore, there is no confident mapping.
                                                Code = '%sX' % (output[9][0])
                                                if len(output[9][1:]) >= Seed:
                                                        return "NONE", Code, "*", "*", str(len(output[9][1:])), "Y", output[9], output[10],
                                                else:
                                                        return "NONE", Code, "*", "*", output[9][1:], "N", output[9], output[10]
                                        else:
                                                if Direction == '_RevStrand_':
                                                        #output[3] is the 1-based leftmost position of the clipped alignment from the .SAM format
                                                        output[3] = str(int(output[3]) + len(output[9]) - 1)
                                                        if cfgvars.Mismatches >= 2 and len(Align) > 3 and int(Align[4]) >= cfgvars.ThreePad:
                                                        #Means if two mismatches are allowed, and if two mismatches are found, and if none of these mismatches are disqualifying
                                                                if Align[2] == '0':
                                                                        #Means there are two adjacent but allowed mismatches
                                                                        Alignment = output[3] + Direction + str(int(output[3]) - int(Align[0]) + 1) + '\t' + output[9][int(Align[0]):int(Align[0]) + 2] + '\t' + output[2] + '\t' + str(int(output[3]) - int(Align[0]) - 2) + Direction + str(int(output[3]) - MappedLength + 1)
                                                                        #This is for Reverse Strand. So, this means: mapping of first section + \t + identity of two allowed and adjacent mismatching nucleotides + \t + mapping of last section.
                                                                else:
                                                                        #Means there are two non-adjacent and allowed mismatches
                                                                        Alignment = output[3] + Direction + str(int(output[3]) - int(Align[0]) + 1) + '\t' + output[9][int(Align[0])] + '\t' + output[2] + '\t' + str(int(output[3]) - int(Align[0]) - 1) + Direction + str(int(output[3]) - int(Align[0]) - int(Align[2])) + '\t' + output[9][(int(Align[0]) + int(Align[2]) + 1)] + "\t" + output[2] + '\t' + str(int(output[3]) - int(Align[0]) - int(Align[2]) - 2) + Direction + str(int(output[3]) - MappedLength + 1)
                                                                        #This is for Reverse Strand. This means: mapping of first section + \t + identity of allowed mismatching nucleotide + \t + mapping of second section + \t + identity of second allowed mismatching nucleotide + \t + mapping of third section
                                                        elif cfgvars.Mismatches >= 1 and len(Align) > 1 and int(Align[2]) >= cfgvars.ThreePad:
                                                                #Means if one mismatch is allowed, and if one mismatch is found and it is not disqualifying
                                                                Alignment = output[3] + Direction + str(int(output[3]) - int(Align[0]) + 1) + '\t' + output[9][int(Align[0])] + '\t' + output[2] + '\t' + str(int(output[3]) - int(Align[0]) - 1) + Direction + str(int(output[3]) - MappedLength + 1)
                                                                #This is for Reverse Strand. So, this means: mapping of first section + \t + identity of allowed mismatching nucleotides + \t + mapping of last section.
                                                        else:
                                                                #Means no mismatches were found
                                                                Alignment = output[3] + Direction + str(int(output[3]) - MappedLength + 1)
                                                                #This is Reverse Strand. So, this means: mapping of whole read.
                                                else:
                                                        if cfgvars.Mismatches >= 2 and len(Align) > 3 and int(Align[4]) >= cfgvars.ThreePad:
                                                        #Means if two mismatches are allowed, and if two mismatches are found, and if none of these mismatches are disqualifying
                                                                if Align[2] == '0':
                                                                        #Means there are two adjacent but allowed mismatches
                                                                        Alignment = output[3] + Direction + str(int(output[3]) + int(Align[0]) - 1) + '\t' + output[9][int(Align[0]):int(Align[0]) + 2] + '\t' + output[2] + '\t' + str(int(output[3]) + int(Align[0]) + 2) + Direction + str(MappedLength + int(output[3]) - 1)
                                                                        #This means: mapping of first section + \t + identity of two allowed and adjacent mismatching nucleotides + \t + mapping of last section.
                                                                else:
                                                                        #Means there are two non-adjacent and allowed mismatches
                                                                        Alignment = output[3] + Direction + str(int(output[3]) + int(Align[0]) - 1) + '\t' + output[9][int(Align[0])] + '\t' + output[2] + '\t' + str(int(output[3]) + int(Align[0]) + 1) + Direction + str(int(Align[0]) + int(Align[2]) + int(output[3])) + '\t' + output[9][(int(Align[0]) + int(Align[2]) + 1)] + '\t' + output[2] + '\t' + str(int(output[3]) + int(Align[0]) + int(Align[2]) + 2) + Direction + str(MappedLength + int(output[3]) - 1)
                                                                        #This means: mapping of first section + \t + identity of allowed mismatching nucleotide + \t + mapping of second section + \t + identity of second allowed mismatching nucleotide + \t + mapping of third section
                                                        elif cfgvars.Mismatches >= 1 and len(Align) > 1 and int(Align[2]) >= cfgvars.ThreePad:
                                                                #Means if one mismatch is allowed, and if one mismatch is found and it is not disqualifying
                                                                Alignment = output[3] + Direction + str(int(output[3]) + int(Align[0]) - 1) + '\t' + output[9][int(Align[0])] + '\t' + output[2] + '\t' + str(int(output[3]) + int(Align[0]) + 1) + Direction + str(MappedLength + int(output[3]) - 1)
                                                                #This means: mapping of first section + \t + identity of allowed mismatching nucleotides + \t + mapping of last section.
                                                        else:
                                                                #Means no mismatches were found
                                                                Alignment = output[3] + Direction + str(MappedLength + int(output[3]) - 1)
                                                                #This means: mapping of whole read.
                                                if len(output[9][(MappedLength):]) >= Seed:
                                                        #Means there are still enough unmapped nucleotide remaining after mapped section to form a new seed
                                                        return "SOME", Code, output[2], Alignment, str(len(output[9][(MappedLength):])), "Y", output[9][(MappedLength):], output[10][(MappedLength):]
                                                else:
                                                        return "SOME", Code, output[2], Alignment, output[9][(MappedLength):], "N"
        else:
		#No mapping was found for this read during this alignment
                if len(output[9]) < Seed:
			#Read was too short.
                        return "TOOSMALL", "U", "*", "*", output[9], "N",
                else:
                        #Code = '%sX' % (output[9][0])
                        if len(output[9][1:]) >= Seed:
				#Read is still long enough for next iteration
                                return "NONE", '%sX' % (output[9][0]), "*", "*", str(len(output[9][1:])), "Y", output[9], output[10]
                        else:
				#Read is now too short for subsequent iterations.
                                return "NONE", '%sX' % (output[9][0]), "*", "*", output[9][1:], "N", output[9], output[10]
            
##      ----------------------------------------------------------------------------------------
##      Function Alignment() will take read data and attempt to align it to the reference genomes (Virus first, Host second).
##      Bowtie must be in your $PATH.
##      If the Seed of the read successfully aligns to a reference genome, bowtie will continue to align the remaining nucleotides after the Seed.
##      Alignment() will extract all the successfully aligned nucleotides and the remaining unaligned nucleotides will be written to a new temporary read file.
##      If there is no succesful alignment, Alignment() will trim one nucleotide from the beginning of the read and report.
##      Again, the remaining nucleotides will be written to a new temporary file which will be used for subsequent alignmen.
##      ----------------------------------------------------------------------------------------

def Alignment(ReadsIn, ReadType, Seed):
	####  Function AddToReportDict() adds details of any alignments, mismatches or trimmed nucleotide to temporary dictionary.
	####  Entries are annotated accordingly to the sequence read name, therefore read names MUST be unique.  Take care when using paired-end reads.
	def AddToReportDict(Dict, Namee):
		if Name in Dict:
			Dict[Namee] += [Mapping[0:5]]
		else:
			Dict[Namee] = [Mapping[0:5]]
	SamHeaders = ['@HD', '@SQ', '@RG', '@PG', '@CO']
	#Run Bowtie/BWA using Virus Genome.   Bowtie/BWA must be in your PATH.  Remove the --mm and -p options if operating in Windows or cygwin.
        if cfgvars.Aligner == 'bwa':
		with open('TEMPSAI1', 'w') as outfilesai:
			call(['bwa', 'aln', '-k', str(cfgvars.Mismatches), '-l', str(Seed), '-n', '10000', '-o', '0', '-t', cfgvars.Threads, cfgvars.Lib1, ReadsIn], stdout = outfilesai)
		with open('TEMPSAM1', 'w') as outfilesam:
			call(['bwa', 'samse', cfgvars.Lib1, 'TEMPSAI1', ReadsIn], stdout = outfilesam)
        else:
                if cfgvars.Nomm:
                        call(['bowtie', ReadType, '-n', str(cfgvars.Mismatches), '-l', str(Seed), '-e', '100000', '--quiet', '-p', cfgvars.Threads, '--best', '-S', '--sam-nohead', cfgvars.Lib1, ReadsIn, 'TEMPSAM1'])
                else:
                        call(['bowtie', ReadType, '-n', str(cfgvars.Mismatches), '-l', str(Seed), '-e', '100000', '--quiet', '--mm', '-p', cfgvars.Threads, '--best', '-S', '--sam-nohead', cfgvars.Lib1, ReadsIn, 'TEMPSAM1'])
        NumHostReads = 0
        with open('TEMPSAM1','r') as SAMIN1:
	        TempReads = open('TEMPREADS', 'w')
	        if cfgvars.Lib2:
			#If using two genomes, open a new file to write any reads that did not map to virus genome
	                HostAttemptReads = open("TEMPREADS2", "w")
	        else:
	                pass
	        for line in SAMIN1:
	                line = line.split('\t')
	                if line[2] != '*' and True not in [i[:5] == 'MD:Z:' for i in line]:  ####REMOVE THIS HACK LATER
                                print "WARNING, SAM entry contains mapping Data but no Mismatch Tag: Read ignored"
                                print line  
                        else:
                                Name = line[0]
                                if Name[:3] in SamHeaders:
                                        pass
                                else:
                                    Mapping = FindReadMapping(line, Seed, Seed)
                                    if Mapping[0] == "NONE":
                                        #No mapping to virus genone was found.  If a host genome is provided, write read out to new tempread file for an extra alignment
                                        if cfgvars.Lib2:
                                                if Mapping[5] == "Y":
                                                #'Y' is just a tag to say that the read has enough nucleotides remaining to be used in subsequent iterations.
                                                        if int(Mapping[4]) >= cfgvars.Host_Seed:
                                                                #Only write read to tempfile used for host alignment is that read is longer than the chosen Host_Seed length, otherwise, skip host alignment
                                                                #HostAttemptReads.write("@" + str(Name) + "\n" + str(Mapping[6]) + "\n+\n" +str(Mapping[7])+ "\n" )
                                                                HostAttemptReads.write("@%s\n%s\n+\n%s\n" % (str(Name), str(Mapping[6]), str(Mapping[7])) )
                                                                NumHostReads += 1
                                                        else:
                                                        #Proceed to next iteration without host mapping and trim first nucleotide
                                                                #TempReads.write("@" + str(Name) + "\n" + str(Mapping[6][1:]) + "\n+\n" + str(Mapping[7][1:])+ "\n" )
                                                                TempReads.write("@%s\n%s\n+\n%s\n" % (str(Name), str(Mapping[6][1:]), str(Mapping[7][1:])) )
                                                                AddToReportDict(ReportDict, Name)
                                                else:
                                                #'N' is just a tag to sat that the read is too short for subsequent iterations and so will not be written to the temp read file.
                                                        AddToReportDict(ReportDict, Name)
                                        else:
                                                if Mapping[5] == "Y":
                                                        #Proceed to next iteration without host mapping and trim first nucleotide
                                                        #TempReads.write("@" + str(Name) + "\n" + str(Mapping[6][1:]) + "\n+\n" + str(Mapping[7][1:])+ "\n" )
                                                        TempReads.write("@%s\n%s\n+\n%s\n" % (str(Name), str(Mapping[6][1:]), str(Mapping[7][1:])) )
                                                else:
                                                        pass
                                                AddToReportDict(ReportDict, Name)
                                    else:
                                        if Mapping[5] == "Y":
                                                #Proceed to next iteration without host mapping.
                                                #TempReads.write("@" + str(Name) + "\n" + str(Mapping[6]) + "\n+\n" + str(Mapping[7])+ "\n" )
                                                TempReads.write("@%s\n%s\n+\n%s\n" % (str(Name), str(Mapping[6]), str(Mapping[7])) )
                                        else:
                                                pass
                                                #'N' is just a tag to sat that the read is too short for subsequent iterations and so will not be written to the temp read file.
                                        AddToReportDict(ReportDict, Name)
        if cfgvars.Lib2:
                HostAttemptReads.close()
                if NumHostReads > 0:
                        #Run Bowtie/BWA using Host Genome.   Bowtie/BWA must be in your PATH.  Remove the --mm and -p options if operating in Windows or cygwin.  With a large host genome, this will dramatically increase runtime as the reference genome will have to be loaded into temporary memory with each iteration.
                        if cfgvars.Aligner == 'bwa':
                                with open('TEMPSAI2', 'w') as outfilesai:
                                        call(['bwa', 'aln', '-k', str(cfgvars.Mismatches), '-l', str(cfgvars.Host_Seed), '-n', '10000', '-o', '0', '-t', cfgvars.Threads, cfgvars.Lib1, ReadsIn], stdout = outfilesai)
                                with open('TEMPSAM2', 'w') as outfilesam:
                                        call(['bwa', 'samse', cfgvars.Lib1, 'TEMPSAI2', ReadsIn], stdout = outfilesam)
                        else:
                                if cfgvars.Nomm:
                                        call(['bowtie', '-q', '-n', str(cfgvars.Mismatches), '-l', str(cfgvars.Host_Seed), '-e', '100000', '--quiet', '-p', cfgvars.Threads, '--best', '-S', '--sam-nohead', cfgvars.Lib2, 'TEMPREADS2', 'TEMPSAM2'])
                                else:
                                        call(['bowtie', '-q', '-n', str(cfgvars.Mismatches), '-l', str(cfgvars.Host_Seed), '-e', '100000', '--quiet', '--mm', '-p', cfgvars.Threads, '--best', '-S', '--sam-nohead', cfgvars.Lib2, 'TEMPREADS2', 'TEMPSAM2'])
                        with open('TEMPSAM2', 'r') as SAMIN2:
                                for line in SAMIN2:
                                        line = line.split('\t')
                                        Name = line[0]
                                        if Name[:3] in SamHeaders:
                                                pass
                                        else:
                                            Mapping = FindReadMapping(line, cfgvars.Host_Seed, Seed)
                                            if Mapping[0] != "NONE":
                                                if Mapping[5] == "Y":
                                                        #TempReads.write("@" + str(Name) + "\n" + str(Mapping[6]) + "\n+\n" + str(Mapping[7]) + "\n" )
                                                        TempReads.write("@%s\n%s\n+\n%s\n" % (str(Name), str(Mapping[6]), str(Mapping[7])) )
                                                else:
                                                        pass
                                                AddToReportDict(ReportDict, Name)
                                            else:
                                                if Mapping[5] == "Y":
                                                        #TempReads.write("@" + str(Name) + "\n" + str(Mapping[6][1:]) + "\n+\n" + str(Mapping[7][1:])+ "\n" )
                                                        TempReads.write("@%s\n%s\n+\n%s\n" % (str(Name), str(Mapping[6][1:]), str(Mapping[7][1:])) ) 
                                                else:
                                                        pass
                                                AddToReportDict(ReportDict, Name)
                else:
                        pass
        TempReads.close()
                

##      ----------------------------------------------------------------------------------------
##      Function IterateAlignments() will call Bowtie and beging alignments starting with supplied input file
##	and continuing with the generated TEMPREAD files until there no reads left.
##	If providing a FASTA file, this get converted to a FASTQ file with uniform quality 
##	scores of PHRED == 30 after the first Bowtie iteration
##      ----------------------------------------------------------------------------------------

def IterateAlignments(File):
        if cfgvars.ReadType == '-f':
                print "%s reads in input file." % Countreads(File, 'F')
		Alignment(File, '-f', cfgvars.Seed)
	else:
                print "%s reads in input file." % Countreads(File, 'Q')
		Alignment(File, '-q', cfgvars.Seed)
        ReadsRemaining = Countreads('TEMPREADS', 'Q')
        print "%s reads remaining to be aligned after first iteration." % (ReadsRemaining)
        n = 1
        while ReadsRemaining > 0:
            n += 1
            Alignment('TEMPREADS', '-q', cfgvars.Seed)
            ReadsRemaining = Countreads('TEMPREADS', 'Q')
            print "%s reads remaining to be aligned after %s iterations." % (ReadsRemaining, n)
    
##      ----------------------------------------------------------------------------------------
##      ReportResults() Analyses the results from all the Bowtie calls and collates all the results 
##	for each read into a single output and writes this to the final Output file.
##      ----------------------------------------------------------------------------------------

def ReportResults():
        Report = open(cfgvars.File2,"a")
        for k in ReportDict:
            FinalAlignment = []
            FinalAlignment.append(k)
            Trimmednucs = ''
            Code = []
            for i in ReportDict[k]:
                if i[0] == "SOME":
                        if Trimmednucs:
                                FinalAlignment.append(Trimmednucs)
                                Code.append("%sU" % (str(len(Trimmednucs))))
                        else:
                                pass
                        FinalAlignment.append(i[2])
                        FinalAlignment.append(i[3])
                        Trimmednucs = ''
                        Code.append(i[1])
                elif i[0] == 'NONE':
                        Trimmednucs += i[1][:-1]
            	else:
			pass
            Trimmednucs += i[4]
            if len(Trimmednucs) > 0:
			FinalAlignment.append(Trimmednucs)
            		Code.append("%sU" % (str(len(Trimmednucs))))
            else:
                    pass
            #FinalAlignment.append(str(Code))
            #for i in FinalAlignment:
            #        Report.write("%s\t" % (i))
            [Report.write("%s\t" % (i)) for i in FinalAlignment]
            Code = "".join(Code)
            Report.write("%s\t\n" % (Code))
        Report.close()

##      ----------------------------------------------------------------------------------------
##      Run Modules
##      ----------------------------------------------------------------------------------------

if __name__ == '__main__':
        if cfgvars.Chunk:
                with open(cfgvars.File1, 'r') as MAINFILE:
                        ChunkNum = 0
                        Read = MAINFILE.readline()
                        while Read:
                                ChunkedReads = open('ChunkedReads', 'w')
                                ReadNum = 0
                                while ReadNum < int(cfgvars.Chunk):
                                        if Read:
                                                if cfgvars.ReadType == '-f':
                                                        ChunkedReads.write(Read)
                                                        ChunkedReads.write(MAINFILE.readline())
                                                else:
                                                        ChunkedReads.write(Read)
                                                        ChunkedReads.write(MAINFILE.readline())
                                                        ChunkedReads.write(MAINFILE.readline())
                                                        ChunkedReads.write(MAINFILE.readline())
                                                Read = MAINFILE.readline()
                                                ReadNum += 1
                                        else:
                                                ReadNum += 1
                                ChunkedReads.close()
                                ChunkNum += 1
                                ReportDict = {}
                                print "Begining alignments on Chunk Number %s" % ChunkNum
                                IterateAlignments('ChunkedReads')
                                print "Appending Results from Chunk Number %s to: " % ChunkNum, str(cfgvars.File2)
                                ReportResults()
        else:
                ReportDict = {}
                print "Begining alignments"
                IterateAlignments(cfgvars.File1)
                print "Reporting Results to: ", str(cfgvars.File2)
                ReportResults()
        if cfgvars.Compile:
                if cfgvars.Aligner =='bwa':
			cfgvars.RefsLib1, cfgvars.RefsLib2, cfgvars.Genes = ExtractRefDataBWA()
                else:
			cfgvars.RefsLib1, cfgvars.RefsLib2, cfgvars.Genes = ExtractRefData()
                if cfgvars.DeDup:
			UniquifyReport(cfgvars.File2, 'DeDuped_' + cfgvars.File2)
			cfgvars.File2 = 'DeDuped_' + cfgvars.File2
		else:
			pass
		print "Compiling Results and saving into individual outputs"
		if args.Output_Dir and cfgvars.Compile:
                        if not exists(str(args.Output_Dir)):
                                cfgvars.Output_Dir = str(args.Output_Dir) + '/'
                                makedirs(cfgvars.Output_Dir)
                        else:
                                print "Output Directory already exists!  Appending time to directory name to prevent overwrite."
                                cfgvars.Output_Dir = str(args.Output_Dir) + str(int(time.time())) + '/'
                                makedirs(cfgvars.Output_Dir)
                else:
                        cfgvars.Output_Dir = ''
                if cfgvars.BED:
                        if not exists(cfgvars.Output_Dir + 'BED_Files/'):
                                makedirs(cfgvars.Output_Dir + 'BED_Files/')
                        else:
                                makedirs(cfgvars.Output_Dir + 'BED_Files_' + str(int(time.time())) + '/')
                                print "WARNING: BED Folder already present in output directory!"
                else:
                        pass
                if args.CoVaMa:
                        cfgvars.CoVaMa = True
                        cfgvars.Named_Output = open(cfgvars.Output_Dir + cfgvars.FileTag + "CoVaMa_Output.txt", "w")
                else:
                        cfgvars.CoVaMa = False
                ResultsSort(cfgvars.File2)

finish = time.time()
print "Time to complete in seconds: ", int(finish - start)

##      ----------------------------------------------------------------------------------------
##      End
##      ----------------------------------------------------------------------------------------



