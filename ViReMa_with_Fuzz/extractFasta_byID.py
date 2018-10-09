#!/usr/bin/python

### extracts sequences from a fasta file (arg 1)
### whose id is in the IDs file (arg 2)

import string
import sys
ListOfIds = sys.argv[1]
fastafile = sys.argv[2]

try:
    ids=open(ListOfIds, 'r')
except IOError, e:
    print "File error: ",ListOfIds
    pass


lignes = ids.readlines()
req=[]
for ligne in lignes:
    req.append(ligne.strip())


#### reading the fasta file to cut
handle = open(fastafile)

bank={}
seqIDmap={}
seq_id = handle.next()
while (seq_id[0]!=">"):
    seq_id = handle.next()
while True:
    try:
        seq = handle.next()
        line = handle.next()
        while (line[0]!=">"):
            seq = seq+line
            line = handle.next()
        bank[seq_id]=seq
        IDclean=string.split(seq_id, " ")[0][1:].strip()
        seqIDmap[IDclean]=seq_id
        seq_id = line # for the next
    except StopIteration:
        break
# last line
bank[seq_id]=seq
seqIDmap[string.split(seq_id, " ")[0][1:].strip()]=seq_id

handle.close()

######## end reading the potentially big fasta file

faName=fastafile.split("/")[-1]
listName=ListOfIds.split("/")[-1]
subsetName=listName+"-"+faName
subset = open(subsetName,"w")
nbNF=0
for i in req:
    try:
        subset.write(seqIDmap[i].strip()+"\n")
        subset.write(bank[seqIDmap[i]].strip()+"\n")
    except KeyError:
        print i, "not found in fasta"
        nbNF+=1

subset.close()

print
print nbNF, "IDs (listed above) from",listName, "have not been found in", faName
print
print "the Subset fasta file", subsetName, "is now created"
