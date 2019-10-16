# SCENARIO 1: pilot-run-fastp-SE.conf

This configuration file is for a dataset of *single-end* reads. 
fastp is used from trimming because is unknown if the sequencing adaptors have already been removed from raw reads.
The downsampling parameter is specifed because it is also unknown if the samples have contaminants from the host.

# SCENARIO 2: pilot-run-trimmomatic-SE.conf

This configuration file is for a dataset of *single-end* reads. 
Trimmomatic is used from trimming. The Nextera adaptors could be present; the tool will find and remove them.
The downsampling parameter is specifed because it is also unknown if the samples have contaminants from the host.

# SCENARIO 2: pilot-run-trimmomatic-PE.conf

This configuration file is for a dataset of *paired-end* reads. 
Trimmomatic is used from trimming. The TrueSeq adaptors could be present; the tool will find and remove them.
The downsampling parameter is NOT specifed because the samples are virtually free of contaminants and sequencing coverage is 1,000x.
