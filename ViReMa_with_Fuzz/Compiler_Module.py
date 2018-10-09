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
##      -------------------------------------------------------------------------------------------
if __name__ == '__main__':
    print '\n-------------------------------------------------------------------------------------------'
    print 'ViReMa_0.9 - Viral Recombination Mapper - Compilation Module, with CoVaMa Option'
    print 'Last modified Feb 2016'
    print '-------------------------------------------------------------------------------------------'

import ConfigViReMa as cfgvars
from re import finditer
import time

##      ------------------------------------------------------------------------------------------------------------
##      Compound_Handling_Script will determine whether trimmed nucleotides found between recombination
##      sites are present between the donor and accpetor sites for these two recombination events.
##      If so, they are assumed to have arisen due to multiple recombination events occuring within close proximity.
##      This is only a good assumption in viral genomes (where the number if possible matches is low) and
##      when there are sufficient nucleotides in the trimmed sequence. This number is set at the command line
##      wih the option: --Compound_Handling.  A default value of 10 is recommended.  This value must be
##      larger than the MicroInDel number.
##      ------------------------------------------------------------------------------------------------------------

def Compound_Handling_Script(Donor, DonorSite, Insertion, AcceptorSite, uDelDicts, RecDicts, ReadName):
                if "_RevStrand" in Donor:
                        DonorA = ">" + Donor[:-10]
                        Insertion = Rev_Comp(Insertion)
                        DonorSite, AcceptorSite = AcceptorSite, DonorSite
                else:
                        DonorA = ">" + Donor
                Frag = cfgvars.Genes[DonorA][int(DonorSite):int(AcceptorSite)]
                if Insertion in Frag:
                        Hits = [m.start() for m in finditer(Insertion, Frag)]
                        if len(Hits) == 1:
                                if "_RevStrand" in Donor:
                                        #Unique Compound Recombination Site Found
                                        NewAcceptorSite = str(int(Hits[0]) + int(DonorSite) + 1)
                                        if int(NewAcceptorSite) - int(DonorSite) - 1 <= cfgvars.MicroInDel_Length:
                                                AddToDict(Donor, Donor, NewAcceptorSite, DonorSite, uDelDicts, ReadName)
                                        else:
                                                AddToDict(Donor, Donor, NewAcceptorSite, DonorSite, RecDicts, ReadName)
                                        NewDonorSite = str(int(Hits[0]) + int(DonorSite) + len(Insertion) + 1) 
                                        if int(AcceptorSite) - int(NewDonorSite) - 1 <= cfgvars.MicroInDel_Length:              
                                                AddToDict(Donor, Donor, AcceptorSite, NewDonorSite, uDelDicts, ReadName)
                                        else:
                                                AddToDict(Donor, Donor, AcceptorSite, NewDonorSite, RecDicts, ReadName)
                                else:
                                        #Unique Compound Recombination Site Found
                                        NewAcceptorSite = str(int(Hits[0]) + int(DonorSite) + 1)
                                        if int(NewAcceptorSite) - int(DonorSite) - 1 <= cfgvars.MicroInDel_Length:
                                                AddToDict(Donor, Donor, DonorSite, NewAcceptorSite, uDelDicts, ReadName)
                                        else:
                                                AddToDict(Donor, Donor, DonorSite, NewAcceptorSite, RecDicts, ReadName)
                                        NewDonorSite = str(int(Hits[0]) + int(DonorSite) + len(Insertion) + 1) 
                                        if int(AcceptorSite) - int(NewDonorSite) - 1 <= cfgvars.MicroInDel_Length:              
                                                AddToDict(Donor, Donor, NewDonorSite, AcceptorSite, uDelDicts, ReadName)
                                        else:
                                                AddToDict(Donor, Donor, NewDonorSite, AcceptorSite, RecDicts, ReadName)
                                return "HIT"
                
##      ----------------------------------------------------------------------------------------------------------
##      UniquifyReport() removes identical results.  Reads giving identical results may be PCR duplicates.  
##      Similarly, finding unique multiple unique reads over single recombination junctions validates recombinant
##      ----------------------------------------------------------------------------------------------------------

def UniquifyReport(FileIn, FileOut):
        print "Removing potential PCR duplicates..."
        TempSet = set()
        Dict = []
        n = 0
        with open(FileIn, 'r') as InputData:
                CLE = str(InputData.readline())
                VirusLib = str(InputData.readline())
                #commandline entry
                x = InputData.readline()
                while x:
                        x = x.split('\t', 1)
                        if x[1] not in TempSet:
                                y = str(x[0]) + '\t' + str(x[1])
                                Dict.append(y)
                                TempSet.add(x[1])
                        n += 1
                        x = InputData.readline()
                print "Total of %s reads in original dataset" % n
        with open(FileOut, 'w') as DeDupedData:
                n = 0
                DeDupedData.write(CLE)
                DeDupedData.write(VirusLib)
                for i in Dict:
                        DeDupedData.write(i)
                        n += 1
                print "%s reads remaining after removing potential PCR duplicates" % n

##      ----------------------------------------------------------------------------------------
##      Function BedGraph_Plot() will find regions deleted or duplicated due to recombination and return
##      a string string of frequencies and nucleotide positions. 
##      ----------------------------------------------------------------------------------------

def BEDGraph_Plot():
        DelCover = {}
        InsCover = {}
        with open(cfgvars.Output_Dir + cfgvars.FileTag + "BED_Files/Virus_Recombination_Results.bed","r") as Input_Data:
                TrackName = Input_Data.readline()
                for i in cfgvars.RefsLib1:
                        i = '>' + i
                        if "_RevStrand" not in i:
                                DelCover[i] = [0] * len(cfgvars.Genes[i])
                                InsCover[i] = [0] * len(cfgvars.Genes[i])
                for line in Input_Data:
                        line = line.split()
                        Gene_Name = '>' + line[0]
                        Donorsite = int(line[1])
                        Acceptorsite = int(line[2])
                        Count = int(line[4])
                        Strand = line[5]
                        #DonorSums[Donorsite] += Count
                        #AcceptorSums[Acceptorsite] += Count
                        if Strand == '+':
                                if Donorsite < Acceptorsite:
                                        while Donorsite < Acceptorsite:
                                                DelCover[Gene_Name][Donorsite] += Count
                                                Donorsite +=1
                                elif Acceptorsite < Donorsite:
                                        while Acceptorsite < Donorsite:
                                                InsCover[Gene_Name][Acceptorsite] += Count
                                                Acceptorsite +=1
        OutputFile = open(cfgvars.Output_Dir + cfgvars.FileTag + "BED_Files/Virus_Conservation.bedgraph","w")
        OutputFile.write('track type=bedGraph name="Virus_Conservation" description="Virus_Conservation"\n')
        for i in DelCover:
                n = 0
                for j in DelCover[i]:
                        OutputFile.write('%s\t%s\t%s\t%s\n' % (str(i[1:]), str(n), str(n+1), str(j)))
                        n += 1
        OutputFile.close()
        OutputFile = open(cfgvars.Output_Dir + cfgvars.FileTag + "BED_Files/Virus_Duplications.bedgraph","w")
        OutputFile.write('track type=bedGraph name="Virus_Duplications" description="Virus_Duplications"n"\n')
        for i in InsCover:
                n = 0
                for j in InsCover[i]:
                        OutputFile.write('%s\t%s\t%s\t%s\n' % (str(i[1:]), str(n), str(n+1), '-' + str(j)))
                        n += 1
        OutputFile.close()

##      ----------------------------------------------------------------------------------------
##      Function Rev_Comp() will return the Reverse Complement of a given DNA string
##      ----------------------------------------------------------------------------------------

def Rev_Comp(Seq):
        Seq = Seq.upper()
        basecomplement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'N': 'N'}
        letters = list(Seq)
        letters = [basecomplement[base] for base in letters]
        return ''.join(letters)[::-1]

##      ----------------------------------------------------------------------------------------------------
##      Indices will find the locations of pertinent information in the results file as directed by the Code
##      ----------------------------------------------------------------------------------------------------
    
def Indices(List):
        n = 1
        Ms = []
        Xs = []
        for i in List:
                if i == "M":
                        Ms.append(n)
                        n+=2
                else:
                        Xs.append(n)
                        n+=1
        return [Ms, Xs]

##      -------------------------------------------------------------------------------------------------------
##      ExtractRefData() will find the names of the genes used in the virus or host genome references.
##      Bowtie-inspect must be in $PATH.
##      -------------------------------------------------------------------------------------------------------

def ExtractRefData():
        import ConfigViReMa as cfgvars
        from subprocess import check_output
        cfgvars.RefsLib1 = set()
        cfgvars.RefsLib2 = set()
        print "Extracting Virus Gene Names..."
        z = check_output(['bowtie-inspect', '-a', '1000000', cfgvars.Lib1]).split()
        cfgvars.Genes = {}
        def RefsAppend(Lib, i):
                Name = i.rstrip()
                Lib.add(Name[1:])
                Lib.add(Name[1:] + "_RevStrand")
                return Name
            
        for i in z:
                if i[0] == '>':
                        Name = RefsAppend(cfgvars.RefsLib1, i)
                else:
                        #if cfgvars.Compound_Handling or cfgvars.Defuzz or cfgvars.MicroInDel_Length or cfgvars.BED:
                                Temp = []
                                Temp.append(i.rstrip())
                                Gene = "".join(Temp)
                                cfgvars.Genes[Name] = Gene
        if cfgvars.Lib2:
                        print "Extracting Host Gene Names..."
                        z = check_output(['bowtie-inspect', '-a', '1000000', cfgvars.Lib2]).split()
                        for i in z:
                                if i[0] == '>':
                                        Name = RefsAppend(cfgvars.RefsLib2, i)
                                else:
                                        if cfgvars.Compound_Handling or cfgvars.Defuzz or cfgvars.MicroInDel_Length or cfgvars.BED:
                                                Temp = []
                                                Temp.append(i.rstrip())
                                                Gene = "".join(Temp)
                                                cfgvars.Genes[Name] = Gene
        else:
                        pass
        print "Finished extracting gene data"
        return cfgvars.RefsLib1, cfgvars.RefsLib2, cfgvars.Genes

##      -------------------------------------------------------------------------------------------------------
##      ExtractRefDataBWA() will find the names of the genes used in the virus or host genome references.
##      Input is typical FASTA file, as per the BWA command line.
##      -------------------------------------------------------------------------------------------------------

def ExtractRefDataBWA():
        import ConfigViReMa as cfgvars
        cfgvars.RefsLib1 = []
        cfgvars.RefsLib2 = []
        cfgvars.Genes = {}
        print "Extracting Virus Gene Data..."
        with open(cfgvars.Lib1,'r') as FASTAIN:
                for line in FASTAIN:
                        if line[0] == '>':
                                Name = line.rstrip()
                                cfgvars.RefsLib1.append(Name[1:])
                                cfgvars.RefsLib1.append(Name[1:] + "_RevStrand")
                        else:
                                if cfgvars.Compound_Handling or cfgvars.Defuzz or cfgvars.MicroInDel_Length:
                                        if Name in cfgvars.Genes:
                                                cfgvars.Genes[Name] += line.rstrip()
                                        else:
                                                cfgvars.Genes[Name] = line.rstrip()

        if cfgvars.Lib2:
                print "Extracting Host Gene Data..."
                with open(cfgvars.Lib2,'r') as FASTAIN:
                        for line in FASTAIN:
                                if line[0] == '>':
                                        Name = line.rstrip()
                                        cfgvars.RefsLib2.append(Name[1:])
                                        cfgvars.RefsLib2.append(Name[1:] + "_RevStrand")
                                else:
                                        if cfgvars.Compound_Handling or cfgvars.Defuzz or cfgvars.MicroInDel_Length:
                                                if Name in cfgvars.Genes:
                                                        cfgvars.Genes[Name] += line.rstrip()
                                                else:
                                                        cfgvars.Genes[Name] = line.rstrip()
        print "Finished extracting gene data"
        return cfgvars.RefsLib1, cfgvars.RefsLib2, cfgvars.Genes
    
##      -------------------------------------------------------------------------------------------
##      AddToDict() takes the Donor and Acceptor sites and references for a given recombination event,
##      and collates them into a Dictionary which will later be written to a results file.
##      -------------------------------------------------------------------------------------------

def AddToDict(Donor, Acceptor, DonorSite, AcceptorSite, Dict, ReadName):
        Fuzz = 0
        if cfgvars.Defuzz:
                if "_RevStrand" in Donor:
                        if int(AcceptorSite) != int(DonorSite) - 1:
                                Fuzz = FindFuzz(Donor, DonorSite, Acceptor, AcceptorSite, (cfgvars.MaxFuzz+1))
                                if Fuzz > 0:
                                        if cfgvars.Defuzz == 'Centre':
                                                DonorSite = str(int(DonorSite) + ((Fuzz+1)/2))
                                                AcceptorSite = str(int(AcceptorSite) + ((Fuzz+1)/2))
                                        elif cfgvars.Defuzz == 'Right':
                                                DonorSite = str(int(DonorSite) + Fuzz)
                                                AcceptorSite = str(int(AcceptorSite) + Fuzz)
                                        else:
                                                pass
                        else:
                                pass
                else:
                        if int(AcceptorSite) != int(DonorSite) + 1:
                                Fuzz = FindFuzz(Donor, DonorSite, Acceptor, AcceptorSite, (cfgvars.MaxFuzz+1))
                                if Fuzz > 0:
                                        if cfgvars.Defuzz == 'Centre':
                                                DonorSite = str(int(DonorSite) - (Fuzz/2))
                                                AcceptorSite = str(int(AcceptorSite) - (Fuzz/2))
                                        elif cfgvars.Defuzz == 'Left':
                                                DonorSite = str(int(DonorSite) - Fuzz)
                                                AcceptorSite = str(int(AcceptorSite) - Fuzz)
                                        else:
                                                pass
                        else:
                                pass
        else:
                pass
        if Fuzz <= cfgvars.MaxFuzz:
                if (Donor + "_to_" + Acceptor) not in Dict:
                        Dict[Donor + "_to_" + Acceptor] = {}
                else:
                        pass
                if cfgvars.ReadNamesEntry:
                        if (DonorSite + "_to_" + AcceptorSite) not in Dict[Donor + "_to_" + Acceptor]:
                                Dict[Donor + "_to_" + Acceptor][DonorSite + "_to_" + AcceptorSite] = [1, [ReadName + '_Fuzz=' + str(Fuzz)]]
                        else:
                                Dict[Donor + "_to_" + Acceptor][DonorSite + "_to_" + AcceptorSite][0] += 1
                                Dict[Donor + "_to_" + Acceptor][DonorSite + "_to_" + AcceptorSite][1].append(ReadName + '_Fuzz=' + str(Fuzz))
                else:
                        if (DonorSite + "_to_" + AcceptorSite) not in Dict[Donor + "_to_" + Acceptor]:
                                Dict[Donor + "_to_" + Acceptor][DonorSite + "_to_" + AcceptorSite] = 1
                        else:
                                Dict[Donor + "_to_" + Acceptor][DonorSite + "_to_" + AcceptorSite] += 1
        else:
                pass
        return Donor + "_to_" + Acceptor, DonorSite + "_to_" + AcceptorSite

##      ----------------------------------------------------------------------------------------------------------------
##      FindFuzz() will determine the number of overlapping nucleotides in the donor region and the nucleotides
##      preceeding the acceptor site.
##      -----------------------------------------------------------------------------------------------------------------

def FindFuzz(Donor, DonorSite, Acceptor, AcceptorSite, MaxFuzz):
        F = 0
        if "_RevStrand" in Donor:
                Gene = '>' + Donor[:-10]
                DonorSeq = Rev_Comp(cfgvars.Genes[Gene][int(DonorSite) - 1:int(DonorSite) - 1 + MaxFuzz])
        else:
                Gene = '>' + Donor
                DonorSeq = cfgvars.Genes[Gene][int(DonorSite) - MaxFuzz:int(DonorSite)]
        if "_RevStrand" in Acceptor:
                Gene = '>' + Acceptor[:-10]
                if int(AcceptorSite) + MaxFuzz > len(cfgvars.Genes[Gene]):
                        UpstreamAcceptorSeq = Rev_Comp(cfgvars.Genes[Gene][int(AcceptorSite):])
                else:
                        UpstreamAcceptorSeq = Rev_Comp(cfgvars.Genes[Gene][int(AcceptorSite): int(AcceptorSite) + MaxFuzz])
        else:
                Gene = '>' + Acceptor
                if int(AcceptorSite) - 1 - MaxFuzz < 0:
                        UpstreamAcceptorSeq = cfgvars.Genes[Gene][0: int(AcceptorSite) - 1]
                else:
                        UpstreamAcceptorSeq = cfgvars.Genes[Gene][int(AcceptorSite) - 1 - MaxFuzz: int(AcceptorSite) - 1]
        for i in range(len(UpstreamAcceptorSeq)):
                try:
                    if UpstreamAcceptorSeq[-i-1] == DonorSeq[-i-1]:
                            F += 1
                    else:
                            break
                except:
                        break
        return F

##      -----------------------------------------------------------------------------------------------------------------
##      AddInsToDict() takes the Donor and Acceptor sites, references and trimmed nucleotides for a given Insertion event
##      and collate them into a Dictionary which will later be written to a results file.
##      -----------------------------------------------------------------------------------------------------------------

def AddInsToDict(Donor, DonorSite, AcceptorSite, Insertion, Dict, ReadName):
                if Donor not in Dict:
                        Dict[Donor] = {}
                else:
                        pass
                if cfgvars.ReadNamesEntry:
                        if (str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite)) not in Dict[Donor]:
                                Dict[Donor][str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite)] = [1, [ReadName]]
                        else:
                                Dict[Donor][str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite)][0] += 1
                                Dict[Donor][str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite)][1].append(ReadName)
                else:
                        if (str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite)) not in Dict[Donor]:
                                Dict[Donor][str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite)] = 1
                        else:
                                Dict[Donor][str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite)] += 1

##      -------------------------------------------------------------------------------------------
##      ResultsSort() is the backbone of the results compilation script.  It will take each line from the results
##      output from ViReMa and determine the nature of every discovered event.  This includes recombinations, insertions, subsitutions, etc.
##      The Code appended to the end of each line in the ViReMa output allows ResultsSort() to group particular events.
##      The finer details are then established based upon parameters set in the command-line (e.g. MicroInDel length), and upon the
##      information provided in the ViReMa output.
##      -------------------------------------------------------------------------------------------

def ResultsSort(File1):
        from re import findall
        from math import fabs

        ##      -------------------------------------------------------------------------------------------
        ##      WriteFinalDict() will read all the information collated in each Dictionary and write out the
        ##      results to the results files.
        ##      -------------------------------------------------------------------------------------------

        def ContractX(x):
                while 'Mismatch' in x:
                        y = x.index('Mismatch')
                        newx= x[:y-2]
                        newx[-1] += x[y-1].split("_")[1]
                        newx[-1]+= x[y+3]
                        newx += x[y+4:]
                        x = newx
                while 'Sub' in x:
                        y = x.index('Sub')
                        newx= x[:y-2]
                        newx[-1] += x[y-1].split("_")[1]
                        newx[-1]+= x[y+3]
                        newx += x[y+4:]
                        x = newx
                return x

        def ReverseEvents(line):
                newline = []
                newline.append(line[0])
                x = line[1:]
                for i in range(Entries/3)[::-1]:
                        name = x[i*3]
                        name = ''.join(name.split('_RevStrand'))
                        newline.append(name)
                        y = x[i*3+1]
                        if "_" in y:
                                if '_to_' in y:
                                        y = y.split("_")
                                        y = y[::-1]
                                        y = "_".join(y)
                                else:
                                        y = y.split("_")
                                        y = y[::-1]
                                        y[1] = Rev_Comp(y[1])
                                        y = "_".join(y)
                                newline.append(y)
                                newline.append(x[i*3+2])
                        else:
                                z = x[i*3+2]
                                z = Rev_Comp(z)
                                y = str(int(y) - len(z) + 1)
                                newline.append(y)
                                newline.append(z)
                return newline
        
        def WriteFinalDict(DictName, Mod):
            
                ##      ---------------------------------------------------------------
                ##      WritetoBedFile() will append the entry to the optional BED File
                ##      ---------------------------------------------------------------
            
                def WritetoBEDFile(Genes, Entry, TargetFile):
                        # Genes is in format: 'Donor_to_Acceptor'
                        # Entry is in format: [DonorSite, 'to', AcceptorSite, '#', Count]
                        Genes = Genes.split("_to_")
                        #print Genes, Entry, TargetFile
                        if Genes[0][-10:] == "_RevStrand":
                                            Genes[0] = Genes[0][:-10]
                                            Strandedness = '-'
                        else:
                                            Strandedness = '+'
                        BED_OUTPUT = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (str(Genes[0]), str(Entry[0]), str(Entry[2]), 'NAMES_TBD', str(Entry[4]), Strandedness, str(Entry[0]), str(Entry[2]))
                        if TargetFile == VirusRecs:
                                        if Genes[0] == Genes[1]:
                                                VirusRecs_BED.write(BED_OUTPUT)
                                        else:
                                                pass
                        elif TargetFile == VirusuIns:
                                        VirusuRecs_BED.write(BED_OUTPUT)
                        elif TargetFile == VirusuDels:
                                        VirusuRecs_BED.write(BED_OUTPUT)
                        elif TargetFile == HostRecs:
                                        if Genes[0] == Genes[1]:
                                                HostRecs_BED.write(BED_OUTPUT)
                                        else:
                                                pass
                        elif TargetFile == HostuIns:
                                        HostuRecs_BED.write(BED_OUTPUT)
                        elif TargetFile == HostuDels:
                                        HostuRecs_BED.write(BED_OUTPUT)
                        else:
                                        pass
                ##      ---------------------------------------------------------------

                for k in DictName:
                        Libs = k.split("_to_")
                        n = 0
                        for i in Libs:
                                if i[-10:] == "_RevStrand":
                                        Libs[n] = Libs[n][:-10]
                                n+=1
                        if Mod == 'Recs':
                                if Libs[0] in cfgvars.RefsLib1 and Libs[1] in cfgvars.RefsLib1:
                                        TargetFile = VirusRecs
                                elif Libs[0] in cfgvars.RefsLib2 and Libs[1] in cfgvars.RefsLib2:
                                        TargetFile = HostRecs
                                else:
                                        TargetFile = VirustoHostRecs
                        elif Mod == 'uDel':
                                if Libs[0] in cfgvars.RefsLib1 and Libs[1] in cfgvars.RefsLib1:
                                        TargetFile = VirusuDels
                                elif Libs[0] in cfgvars.RefsLib2 and Libs[1] in cfgvars.RefsLib2:
                                        TargetFile = HostuDels
                                else:
                                        pass                        
                        elif Mod == 'uIns':
                                if Libs[0] in cfgvars.RefsLib1:
                                        TargetFile = VirusuIns
                                else:
                                        TargetFile = HostuIns
                        elif Mod == 'Ins':
                                if Libs[0] in cfgvars.RefsLib1:
                                        TargetFile = VirusInsertions
                                else:
                                        TargetFile = HostInsertions
                        elif Mod == 'Sub':
                                if Libs[0] in cfgvars.RefsLib1:
                                        TargetFile = VirusSubstitutions
                                else:
                                        TargetFile = HostSubstitutions
                        Temp = []
                        if cfgvars.ReadNamesEntry:
                                for i in DictName[k]:
                                        x = [(str(i) + "_#_" + str(DictName[k][i][0])).split("_"), DictName[k][i][1]]
                                        Temp.append(x)
                                Temp.sort(key=lambda a:int(a[0][4]), reverse=True)
                                TargetFile.write("@NewLibrary: " + str(k) + "\n")
                                for i in Temp:
                                        j = '_'.join(i[0])
                                        TargetFile.write(str(j) + "\n")
                                        for Names in i[1]:
                                                TargetFile.write(str(Names) + '\t')
                                        TargetFile.write('\n')
                                TargetFile.write("\n@EndofLibrary\n")
                        else:
                                for i in DictName[k]:
                                        x = (str(i) + "_#_" + str(DictName[k][i])).split("_")
                                        Temp.append(x)
                                Temp.sort(key=lambda a:int(a[4]), reverse=True)
                                TargetFile.write("@NewLibrary: " + str(k) + "\n")
                                for i in Temp:
                                        if cfgvars.BED:
                                                if cfgvars.Lib2:
                                                        if cfgvars.MicroInDel_Length > 0:
                                                                BEDableTargetFiles = [VirusRecs, VirusuDels, HostRecs, HostuDels, VirusuIns, HostuIns]
                                                        else:
                                                                BEDableTargetFiles = [VirusRecs, HostRecs]
                                                else:
                                                        if cfgvars.MicroInDel_Length > 0:
                                                                BEDableTargetFiles = [VirusRecs, VirusuDels, VirusuIns]
                                                        else:
                                                                BEDableTargetFiles = [VirusRecs]
                                                if TargetFile in BEDableTargetFiles:
                                                        WritetoBEDFile(k, i, TargetFile)
                                                        
                                                else:
                                                        pass
                                        else:
                                                pass
                                        j = '_'.join(i)
                                        TargetFile.write(str(j) + "\t")
                                TargetFile.write("\n@EndofLibrary\n")

        def AppendToReadEvents(Donor, DonorSite, Insertion, AcceptorSite, EventType):
                if cfgvars.CoVaMa:
                        cfgvars.ReadEvents.append(Donor)
                        cfgvars.ReadEvents.append(str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite))
                        cfgvars.ReadEvents.append(EventType)
                else:
                        pass
##                ReadEvents.append(Donor)
##                ReadEvents.append(str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite))
##                ReadEvents.append('uIns')
        
        #Dictionaries 
        InsDicts = {}
        SubDicts = {}
        uDelDicts = {}
        uInsDicts = {}
        RecDicts = {}

        #Counts for events used for printed summary
        Padcount = 0
        Totalcount = 0
        uCount = 0
        InsCount = 0
        SubCount = 0
        CompoundCount = 0
        RecombCount = 0
        ErrorCount = 0
        ViralRecombinationCount = 0
        HostRecombinationCount = 0
        ViraltoHostRecombinationCount = 0
        UnknownRecombinationCount = 0
        UnmappedReadsCount = 0
        UnmappedReads = open(cfgvars.Output_Dir + cfgvars.FileTag + "UnMappedReads.txt","w")
        SingleAlignment = open(cfgvars.Output_Dir + cfgvars.FileTag + "Single_Alignments.txt","w")
        UnknownRecombinations = open(cfgvars.Output_Dir + cfgvars.FileTag + "Unknown_Recombinations.txt", "w")

        with open(File1,"r") as InRecombs:
            skip = InRecombs.readline()
            skip = InRecombs.readline()
            #Meat of script, reads each line from ViReMa.py output and stores details into dictionaries
            wholeline = InRecombs.readline()
            while wholeline:
                Totalcount += 1
                line = wholeline.split("\t")[:-1]
                ReadName = line[0]
                Code = ''.join(findall(r"\D", line[-1]))
                Index = Indices(Code)
                MCount = Code.count("M")
                if "M" not in Code:
                                #UnMapped Read
                                UnmappedReads.write(wholeline)
                                UnmappedReadsCount += 1
                elif MCount == 1:
                                #Singly mapped Read
##                                cfgvars.Named_Output.write(ReadName + '\t')
                                PadLongerThanSeed = False
                                for i in Index[1]:
                                        if len(line[i]) >= int(cfgvars.Seed):
                                                PadLongerThanSeed = True
                                        else:
                                                pass
                                if PadLongerThanSeed:
                                        #Mapable region recombined
                                        UnknownRecombinationCount += 1
                                        UnknownRecombinations.write(wholeline)
                                else:
                                        #Single non-padded Alignment
                                        SingleAlignment.write(wholeline)
                                        Padcount += 1
                                if cfgvars.CoVaMa:
                                        cfgvars.Named_Output.write(ReadName + '\t')
                                        MappingRef = line[Index[0][0]]
                                        MappingStartPos = line[Index[0][0]+1].split('_')[0]
                                        MappingFinishPos = line[Index[0][0]+1].split('_')[-1]
                                        if 'RevStrand' in line[Index[0][0]+1]:
                                                MappingStartPos, MappingFinishPos = MappingFinishPos, MappingStartPos
                                        else:
                                                pass
                                        MappedReadData = cfgvars.Genes['>' + str(MappingRef)][int(MappingStartPos)-1:int(MappingFinishPos)]
                                        cfgvars.Named_Output.write(str(MappingRef) + '\t' + str(MappingStartPos) + '\t' + str(MappedReadData) + '\t')
                                        cfgvars.Named_Output.write('\n')
                                else:
                                        pass
                else:
                                #Multiple mappings, means either recombination, insertion, or substitution.
                                if cfgvars.CoVaMa:
                                        cfgvars.ReadEvents = []
                                        cfgvars.ReadEvents.append(ReadName)
                                else:
                                        pass
                                n=0
                                UnRec = ''
                                for i in Index[0][:-1]:
                                        Donor = line[i]
                                        Ref = Donor
                                        if "RevStrand" in line[i+1]:
                                                DonorSite = line[i+1].split("_")[2]
                                                Donor += "_RevStrand"
                                        else:
                                                DonorSite = line[i+1].split("_")[1]
                                        
                                        MappingStartPos = line[i+1].split("_")[0]
##                                        ReadEvents.append(MappingStartPos)
                                        if "RevStrand" in line[i+1]:
                                                MappedReadData = cfgvars.Genes['>' + str(Ref)][int(DonorSite)-1:int(MappingStartPos)]
                                                MappedReadData = Rev_Comp(MappedReadData)
                                        else:
                                                MappedReadData = cfgvars.Genes['>' + str(Ref)][int(MappingStartPos)-1:int(DonorSite)]
                                        if  cfgvars.CoVaMa:
                                                cfgvars.ReadEvents.append(Donor)
                                                cfgvars.ReadEvents.append(MappingStartPos)
                                                cfgvars.ReadEvents.append(MappedReadData)
                                        else:
                                                pass
                                        if Index[0][n+1] == i + 2:
                                                #Recombination Event
                                                Acceptor = line[i+2]
                                                if "RevStrand" in line[i+3]:
                                                        AcceptorSite = line[i+3].split("_")[0]
                                                        Acceptor += "_RevStrand"
                                                else:
                                                        AcceptorSite = line[i+3].split("_")[0]
                                                if Donor == Acceptor and "_RevStrand" in Donor and fabs(int(DonorSite) - int(AcceptorSite) - 1) <= cfgvars.MicroInDel_Length:
                                                                if int(DonorSite) - int(AcceptorSite) - 1 < 0:
                                                                        #MicroInsertion on negative strand
                                                                        uCount += 1
                                                                        DonorA = ">" + Donor[:-10]
                                                                        Insertion = cfgvars.Genes[DonorA][int(DonorSite) - 1:int(AcceptorSite)]
                                                                        Insertion = Rev_Comp(Insertion)
                                                                        NewAcceptorSite = str(int(DonorSite) - 1)
                                                                        AddInsToDict(Donor, DonorSite, NewAcceptorSite, Insertion, uInsDicts, ReadName)
                                                                        AppendToReadEvents(Donor, DonorSite, Insertion, AcceptorSite, 'uIns')
##                                                                        ReadEvents.append(Donor)
##                                                                        ReadEvents.append(str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite))
##                                                                        ReadEvents.append('uIns')
                                                                elif int(DonorSite) - int(AcceptorSite) - 1 > 0:
                                                                        #MicroDeletion on negative strand
                                                                        uCount += 1
                                                                        x = AddToDict(Donor, Acceptor, DonorSite, AcceptorSite, uDelDicts, ReadName)
                                                                        if cfgvars.CoVaMa:
                                                                                cfgvars.ReadEvents.append(x[0])
                                                                                cfgvars.ReadEvents.append(x[1])
                                                                                cfgvars.ReadEvents.append('uDel')
                                                                        else:
                                                                                pass
                                                elif Donor == Acceptor and fabs(int(DonorSite) - int(AcceptorSite) + 1) <= cfgvars.MicroInDel_Length:
                                                                if int(DonorSite) - int(AcceptorSite) + 1 > 0:
                                                                        #MicroInsertion
                                                                        uCount += 1
                                                                        DonorA = ">" + Donor
                                                                        Insertion = cfgvars.Genes[DonorA][int(AcceptorSite) - 1:int(DonorSite)]
                                                                        NewAcceptorSite = str(int(DonorSite) + 1)
                                                                        AddInsToDict(Donor, DonorSite, NewAcceptorSite, Insertion, uInsDicts, ReadName)
                                                                        AppendToReadEvents(Donor, DonorSite, Insertion, AcceptorSite, 'uIns')
##                                                                        ReadEvents.append(Donor)
##                                                                        ReadEvents.append(str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite))
##                                                                        ReadEvents.append('uIns')
                                                                elif int(DonorSite) - int(AcceptorSite) + 1 < 0:
                                                                        #MicroDeletion
                                                                        uCount += 1
                                                                        x = AddToDict(Donor, Acceptor, DonorSite, AcceptorSite, uDelDicts, ReadName)
                                                                        if cfgvars.CoVaMa:
                                                                                cfgvars.ReadEvents.append(x[0])
                                                                                cfgvars.ReadEvents.append(x[1])
                                                                                cfgvars.ReadEvents.append('uDel')
                                                                        else:
                                                                                pass
                                                else:
                                                        #Direct Recombination Event
                                                        RecombCount += 1
                                                        x = AddToDict(Donor, Acceptor, DonorSite, AcceptorSite, RecDicts, ReadName)
                                                        if cfgvars.CoVaMa:
                                                                cfgvars.ReadEvents.append(x[0])
                                                                cfgvars.ReadEvents.append(x[1])
                                                                cfgvars.ReadEvents.append('Rec')
                                                        else:
                                                                pass
                                                        if Donor in cfgvars.RefsLib1 and Acceptor in cfgvars.RefsLib1:
                                                                ViralRecombinationCount +=1
                                                        elif Donor in cfgvars.RefsLib2 and Acceptor in cfgvars.RefsLib2:
                                                                HostRecombinationCount += 1
                                                        else:
                                                                ViraltoHostRecombinationCount += 1
                                        else:
                                                #Insertion between mapped Segments
                                                Acceptor = line[i+3]
                                                Insertion = line[i+2]
                                                if "RevStrand" in line[i+4]:
                                                        AcceptorSite = line[i+4].split("_")[0]
                                                        Acceptor += "_RevStrand"
                                                else:
                                                        AcceptorSite = line[i+4].split("_")[0]
                                                if Acceptor == Donor and "_RevStrand" in Donor and int(DonorSite) == (int(AcceptorSite) + 1):
                                                        #Simple Insertion Event in negative strand
                                                        if len(Insertion) >= cfgvars.MicroInDel_Length:
                                                                InsCount += 1
                                                                AddInsToDict(Donor, DonorSite, AcceptorSite, Insertion, InsDicts, ReadName)
                                                                AppendToReadEvents(Donor, DonorSite, Insertion, AcceptorSite, 'Ins')
##                                                                ReadEvents.append(Donor)
##                                                                ReadEvents.append(str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite))
##                                                                ReadEvents.append('Ins')
                                                        else:
                                                                #MicroInDel on negative strand 
                                                                uCount += 1
                                                                AddInsToDict(Donor, DonorSite, AcceptorSite, Insertion, uInsDicts, ReadName)
                                                                AppendToReadEvents(Donor, DonorSite, Insertion, AcceptorSite, 'uIns')
##                                                                ReadEvents.append(Donor)
##                                                                ReadEvents.append(str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite))
##                                                                ReadEvents.append('uIns')
                                                elif Acceptor == Donor and int(AcceptorSite) == (int(DonorSite) + 1):
                                                        #Simple Insertion Event
                                                        if len(Insertion) >= cfgvars.MicroInDel_Length:
                                                                InsCount += 1
                                                                AddInsToDict(Donor, DonorSite, AcceptorSite, Insertion, InsDicts, ReadName)
                                                                AppendToReadEvents(Donor, DonorSite, Insertion, AcceptorSite, 'Ins')
##                                                                ReadEvents.append(Donor)
##                                                                ReadEvents.append(str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite))
##                                                                ReadEvents.append('Ins')
                                                        else:
                                                                uCount += 1
                                                                AddInsToDict(Donor, DonorSite, AcceptorSite, Insertion, uInsDicts, ReadName)
                                                                AppendToReadEvents(Donor, DonorSite, Insertion, AcceptorSite, 'uIns')
##                                                                ReadEvents.append(Donor)
##                                                                ReadEvents.append(str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite))
##                                                                ReadEvents.append('uIns')
                                                elif int(AcceptorSite) == (int(DonorSite) + len(Insertion) + 1) and Acceptor == Donor:
                                                        #Direct Substitution
                                                        if len(Insertion) <= cfgvars.Mismatches:
                                                                #Mismatch, not Substitution
                                                                MCount -= 1
                                                                if cfgvars.CoVaMa:
                                                                        AppendToReadEvents(Donor, DonorSite, Insertion, AcceptorSite, 'Mismatch')
##                                                                        ReadEvents.append(Donor)
##                                                                        ReadEvents.append(str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite))
##                                                                        ReadEvents.append('Mismatch')
                                                                else:
                                                                        pass
                                                                if MCount == 1:
                                                                        #Singly mapped Read
                                                                        PadLongerThanSeed = ''
                                                                        for i in Index[1]:
                                                                                if len(line[i]) >= int(cfgvars.Seed) or len(line[i]) >= int(cfgvars.Host_Seed):
                                                                                        PadLongerThanSeed += 'X'
                                                                                else:
                                                                                        pass
                                                                        if PadLongerThanSeed:
                                                                                #Mapable region recombined
                                                                                UnknownRecombinationCount += 1
                                                                                UnknownRecombinations.write(wholeline)
                                                                        else:
                                                                                #Single non-padded Alignment
                                                                                SingleAlignment.write(wholeline)
                                                                                Padcount += 1
                                                                else:
                                                                        pass
                                                                    
                                                        else:
                                                                SubCount += 1
                                                                AddInsToDict(Donor, DonorSite, AcceptorSite, Insertion, SubDicts, ReadName)
                                                                if cfgvars.CoVaMa:
                                                                        AppendToReadEvents(Donor, DonorSite, Insertion, AcceptorSite, 'Sub')
##                                                                        ReadEvents.append(Donor)
##                                                                        ReadEvents.append(str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite))
##                                                                        ReadEvents.append('Sub')
                                                                else:
                                                                        pass
                                                elif int(DonorSite) == (int(AcceptorSite) + len(Insertion) + 1) and Acceptor == Donor and "_RevStrand" in Donor:
                                                        #Direct Substitution on negative strand
                                                        if len(Insertion) <= cfgvars.Mismatches:
                                                                #Mismatch, not Substitution
                                                                MCount -= 1
                                                                if cfgvars.CoVaMa:
                                                                        AppendToReadEvents(Donor, DonorSite, Insertion, AcceptorSite, 'Mismatch')
##                                                                        ReadEvents.append(Donor)
##                                                                        ReadEvents.append(str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite))
##                                                                        ReadEvents.append('Mismatch')
                                                                else:
                                                                        pass
                                                                if MCount == 1:
                                                                        #Singly mapped Read
                                                                        PadLongerThanSeed = ''
                                                                        for i in Index[1]:
                                                                                if len(line[i]) >= int(cfgvars.Seed) or len(line[i]) >= int(cfgvars.Host_Seed):
                                                                                        PadLongerThanSeed += 'X'
                                                                                else:
                                                                                        pass
                                                                        if PadLongerThanSeed:
                                                                                #Mapable region recombined
                                                                                UnknownRecombinationCount += 1
                                                                                UnknownRecombinations.write(wholeline)
                                                                        else:
                                                                                #Single non-padded Alignment
                                                                                SingleAlignment.write(wholeline)
                                                                                Padcount += 1
                                                                else:
                                                                        pass
                                                        else:
                                                                SubCount += 1
                                                                AddInsToDict(Donor, AcceptorSite, DonorSite, Insertion, SubDicts, ReadName)
                                                                if cfgvars.CoVaMa:
                                                                        AppendToReadEvents(Donor, DonorSite, Insertion, AcceptorSite, 'Sub')
##                                                                        ReadEvents.append(Donor)
##                                                                        ReadEvents.append(str(DonorSite) + "_" + Insertion + "_" + str(AcceptorSite))
##                                                                        ReadEvents.append('Sub')
                                                                else:
                                                                        pass
                                                else:
                                                        if len(Insertion) >= int(cfgvars.Seed) or len(Insertion) >= int(cfgvars.Host_Seed):
                                                                #Mapable Insertion/Recombination
                                                                UnknownRecombinationCount += 1
                                                                UnRec = 'Y'
                                                        else:
                                                                if cfgvars.Compound_Handling and len(Insertion) > int(cfgvars.Compound_Handling) and Donor == Acceptor and Donor in cfgvars.RefsLib1:
                                                                        #Compound Recombination
                                                                        CompoundCount += 1
                                                                        CompTest = Compound_Handling_Script(Donor, DonorSite, Insertion, AcceptorSite, uDelDicts, RecDicts, ReadName)
                                                                        if CompTest == "HIT":
                                                                                RecombCount += 2
                                                                                ViralRecombinationCount += 2
                                                                                CompoundCount += 1
                                                                        else:
                                                                                #Unknown Compound
                                                                                UnRec = 'Y'
                                                                                UnknownRecombinationCount += 1
                                                                else:
                                                                        #Unknown Insertion.
                                                                        UnknownRecombinationCount += 1
                                                                        UnRec = 'Y'
                                        n+=1 
                                if UnRec:
                                        UnknownRecombinations.write(wholeline)
                                else:
                                        pass
                                if cfgvars.CoVaMa:
                                        i = Index[0][-1]
                                        Donor = line[i]
                                        Ref = Donor
                                        if "RevStrand" in line[i+1]:
                                                DonorSite = line[i+1].split("_")[2]
                                                Donor += "_RevStrand"
                                        else:
                                                DonorSite = line[i+1].split("_")[1]
                                        cfgvars.ReadEvents.append(Donor)
                                        MappingStartPos = line[i+1].split("_")[0]
                                        cfgvars.ReadEvents.append(MappingStartPos)
                                        if "RevStrand" in line[i+1]:
                                                MappedReadData = cfgvars.Genes['>' + str(Ref)][int(DonorSite)-1:int(MappingStartPos)]
                                                MappedReadData = Rev_Comp(MappedReadData)
                                        else:
                                                MappedReadData = cfgvars.Genes['>' + str(Ref)][int(MappingStartPos)-1:int(DonorSite)]
                                        cfgvars.ReadEvents.append(MappedReadData)
                                        cfgvars.ReadEvents = ContractX(cfgvars.ReadEvents)
                                        n = 0
                                        Entries = len(cfgvars.ReadEvents)
                                        for i in cfgvars.ReadEvents:
                                                if 'RevStrand' in i:
                                                        n+=1
                                                else:
                                                        pass
                                        if n!= 0:
                                                if (Entries - 1)/3 == n:
                                                        cfgvars.ReadEvents = ReverseEvents(cfgvars.ReadEvents)
                                                else:
                                                        UnRec = 'Y'
                                        else:
                                                pass
                                        if UnRec:
                                                pass
                                        else:
                                                for i in cfgvars.ReadEvents:
                                                        cfgvars.Named_Output.write(str(i) + '\t')
                                                cfgvars.Named_Output.write('\n')
                                else:
                                        pass
                wholeline = InRecombs.readline()        
        #Output Files for each type of event
        VirusSubstitutions = open(cfgvars.Output_Dir + cfgvars.FileTag + "Virus_Substitutions.txt","w")
        VirusInsertions = open(cfgvars.Output_Dir + cfgvars.FileTag + "Virus_Insertions.txt","w")
        VirusRecs = open(cfgvars.Output_Dir + cfgvars.FileTag + "Virus_Recombination_Results.txt","w")
        if cfgvars.MicroInDel_Length > 0:
                VirusuDels = open(cfgvars.Output_Dir + cfgvars.FileTag + "Virus_MicroDeletions.txt","w")
                VirusuIns = open(cfgvars.Output_Dir + cfgvars.FileTag + "Virus_MicroInsertions.txt","w")
        else:
                pass
        if cfgvars.Lib2:
                HostSubstitutions = open(cfgvars.Output_Dir + cfgvars.FileTag + "Host_Substitutions.txt","w")
                HostInsertions = open(cfgvars.Output_Dir + cfgvars.FileTag + "Host_Insertions.txt","w")
                HostRecs = open(cfgvars.Output_Dir + cfgvars.FileTag + "Host_Recombination_Results.txt","w")
                if cfgvars.MicroInDel_Length > 0:
                        HostuDels = open(cfgvars.Output_Dir + cfgvars.FileTag + "Host_MicroDeletions.txt","w")
                        HostuIns = open(cfgvars.Output_Dir + cfgvars.FileTag + "Host_MicroInsertions.txt","w")
                else:
                        pass
                VirustoHostRecs = open(cfgvars.Output_Dir + cfgvars.FileTag + "Virus-to-Host_Recombination_Results.txt","w")
        else:
                pass

        if cfgvars.BED:
                #Create optional BED files.
                VirusRecs_BED = open(cfgvars.Output_Dir + cfgvars.FileTag + "BED_Files/Virus_Recombination_Results.bed","a")
                VirusRecs_BED.write('track name=Virus_Recombinations description="Virus_Recombinations" graphType=junctions\n')
                if cfgvars.MicroInDel_Length > 0:
                        VirusuRecs_BED = open(cfgvars.Output_Dir + cfgvars.FileTag + "BED_Files/Virus_MicroRecombinations.bed","a")
                        VirusuRecs_BED.write('track name=Virus_MicroInDels description="Virus_MicroInDels" graphType=junctions\n')
                else:
                        pass
                if cfgvars.Lib2:
                        HostRecs_BED = open(cfgvars.Output_Dir + cfgvars.FileTag + "BED_Files/Host_Recombination_Results.bed","a")
                        HostRecs_BED.write('track name=Host_Recombinations description="Host_Recombinations" graphType=junctions\n')
                        if cfgvars.MicroInDel_Length > 0:
                                HostuRecs_BED = open(cfgvars.Output_Dir + cfgvars.FileTag + "BED_Files/Host_MicroRecombinations.bed","a")
                                HostuRecs_BED.write('track name=Host_MicroInDels description="Host_MicroInDels" graphType=junctions\n')
                        else:
                                pass
                else:
                        pass
                    
        ##      Take final Dictionaries of recombination events are write out to files
        print "Writing sorted results to individual output files..."
        WriteFinalDict(RecDicts, 'Recs')
        if cfgvars.MicroInDel_Length > 0:
                WriteFinalDict(uDelDicts, 'uDel')
                WriteFinalDict(uInsDicts, 'uIns')
        else:
                pass
        WriteFinalDict(InsDicts, 'Ins')
        WriteFinalDict(SubDicts, 'Sub')

        ##      Print summary
        print "---------------------------------------------------------------------------------------------------------------------"
        print "Total of %s reads have been analysed:" % Totalcount
        print "%s were single mapping reads with pads." % Padcount
        print "%s Straight-forward Recombination Events detected"% RecombCount
        print "of which %s were Viral Recombinations, %s were Host Recombinations and %s were Virus-to-Host Recombinations" % (ViralRecombinationCount, HostRecombinationCount, ViraltoHostRecombinationCount)
        if cfgvars.MicroInDel_Length > 0:
                print "%s were MicroIndels below a threshold of less than or equal to %s nucleotides." % (uCount, cfgvars.MicroInDel_Length)
        else:
                pass
        print "%s UnIdentified Insertion Events." % InsCount
        print "%s Nucleotide Subsitution events, including mismatches that preserve the gene length." % SubCount
        if cfgvars.Compound_Handling:
                print "%s Compound Recombination Events detected." % CompoundCount
        else:
                pass
        print "%s events were Unknown or Ambiguous Recombination Events." % UnknownRecombinationCount
        print "%s reads were completely unmapped." % UnmappedReadsCount

        #Close all output files and finish
        if cfgvars.CoVaMa:
                cfgvars.Named_Output.close()
        else:
                pass
        UnmappedReads.close()
        InRecombs.close()
        SingleAlignment.close()
        UnknownRecombinations.close()
        VirusRecs.close()
        if cfgvars.MicroInDel_Length > 0:
                VirusuIns.close()
                VirusuDels.close()
        else:
                pass
        VirusSubstitutions.close()
        VirusInsertions.close()
        if cfgvars.Lib2:
                HostRecs.close()
                VirustoHostRecs.close()
                HostInsertions.close()
                if cfgvars.MicroInDel_Length > 0:
                        HostuDels.close()
                        HostuIns.close()
                else:
                        pass
                HostSubstitutions.close()
        else:
                pass
        if cfgvars.BED:
                VirusRecs_BED.close()
                if cfgvars.MicroInDel_Length > 0:
                        VirusuRecs_BED.close()
                else:
                        pass
                if cfgvars.Lib2:
                        HostRecs_BED.close()
                        if cfgvars.MicroInDel_Length > 0:
                                HostuRecs_BED.close()
                        else:
                                pass
                else:
                        pass
                BEDGraph_Plot()
        else:
                pass

##      -------------------------------------------------------------------------------------------
##      This module can be run seperately from the main ViReMa script. This may be useful when tweeking variables such
##      as the MicroInDel length or Compound_Handling, or when combining the results from multiple instances of ViReMa.
##      Consequently, the following code takes arguments from command line, and sends them to the config file for cross-module access.
##      Results Compilation is then initiated as normal.
##      -------------------------------------------------------------------------------------------

if __name__ == '__main__':
        from os.path import exists
        from os import makedirs
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("Input_Data", help= "UnCompiled Results file from ViReMa run")
        parser.add_argument("--Output_Tag", help= "Enter a tag name that will be appended to end of each output file.")
        parser.add_argument("-DeDup", action='store_true', help="Remove potential PCR duplicates. Default is off.")
        parser.add_argument("-ReadNamesEntry", action='store_true', help="Append Read Names contributing to each compiled result. Default is off.")
        parser.add_argument("--Defuzz", help="Choose how to defuzz data:  '5' to report at 5' end of fuzzy region, '3' to report at 3' end, or '0' to report in centre of fuzzy region. Default is no fuzz handling (similar to choosing Right - see Routh et al).")
        parser.add_argument("--MaxFuzz", help="Select maximum allowed length of fuzzy region. Recombination events with longer fuzzy regions will not be reported. Default is Seed Length.")
        parser.add_argument("--MicroInDel_Length", help= "Size of MicroInDels - these are common artifacts of cDNA preparation.  See Routh et al JMB 2012. Default size is 0)")
        parser.add_argument("--Compound_Handling", help= "Select this option for compound recombination event mapping (see manual for details). Enter number of nucleotides to map (must be less than Seed, and greater than number of nts in MicroInDel). Default is off.")
        parser.add_argument("--Output_Dir", help= "Enter a directory name that all compiled output files will be saved in.")
        parser.add_argument("-BED", action='store_true', help= "Output recombination data into BED files.")
        parser.add_argument("-CoVaMa", action='store_true', help= "Make CoVaMa output data.")
        args = parser.parse_args()
        File1 = str(args.Input_Data)
        with open(File1,"r") as InRecombs:
                #Find arguments used in Mapping Phase from ViReMa.py
                cfgvars.Lib1 = InRecombs.readline().rstrip()
                CommandLineEntry = InRecombs.readline()[1:-3].split("', '")
                if "--Host_Index" in CommandLineEntry:
                        cfgvars.Lib2 = CommandLineEntry[CommandLineEntry.index("--Host_Index")+1]
                else:
                        cfgvars.Lib2 = None
                if "--Seed" in CommandLineEntry:
                        cfgvars.Seed = CommandLineEntry[CommandLineEntry.index("--Seed")+1]
                else:
                        cfgvars.Seed = '25'
                if "--Host_Seed" in CommandLineEntry:
                        cfgvars.Host_Seed = CommandLineEntry[CommandLineEntry.index("--Host_Seed")+1]
                else:
                        cfgvars.Host_Seed = cfgvars.Seed
                if "--N" in CommandLineEntry:
                        cfgvars.Mismatches = int(CommandLineEntry[CommandLineEntry.index("--N")+1])
                else:
                        cfgvars.Mismatches = 1
        if args.Output_Tag:
                cfgvars.FileTag = str(args.Output_Tag)
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
        if args.DeDup:
                cfgvars.DeDup = True
        else:
                cfgvars.DeDup = False
        if args.ReadNamesEntry:
                cfgvars.ReadNamesEntry = True
        else:
                cfgvars.ReadNamesEntry = False
        if args.MaxFuzz:
                cfgvars.MaxFuzz = int(args.MaxFuzz)
        else:
                cfgvars.MaxFuzz = int(cfgvars.Seed)
        if args.Compound_Handling:
                cfgvars.Compound_Handling = str(args.Compound_Handling)
        else:
                cfgvars.Compound_Handling = ''
        if args.MicroInDel_Length:
                cfgvars.MicroInDel_Length = int(args.MicroInDel_Length)
        else:
                cfgvars.MicroInDel_Length = 0
        if args.BED:
                cfgvars.BED = True
        else:
                cfgvars.BED = False
        if args.Output_Dir:
                if not exists(str(args.Output_Dir)):
                        cfgvars.Output_Dir = str(args.Output_Dir) + '/'
                        makedirs(cfgvars.Output_Dir)
                else:
                        print "Output Directory already exists!  Appending time to directory name to prevent overwrite."
                        cfgvars.Output_Dir = str(args.Output_Dir) + str(int(time.time())) + '/'
                        makedirs(cfgvars.Output_Dir)
        else:
                passs
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
        print "Finding reference gene data using Bowtie-Inspect"
        cfgvars.RefsLib1, cfgvars.RefsLib2, cfgvars.Genes = ExtractRefData()
        if cfgvars.DeDup:
                UniquifyReport(File1, 'DeDuped_' + File1)
                File1 = 'DeDuped_' + File1
        else:
                pass
        print "Sorting Results and saving into individual outputs"
        ResultsSort(File1)

##      -------------------------------------------------------------------------------------------
##      End
##      -------------------------------------------------------------------------------------------
