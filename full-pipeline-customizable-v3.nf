#!/usr/bin/env nextflow

// version
params.version  = 3.0

def helpMessage() {
    log.info"""
    ===================================
     DIP-pipeline  ~  version ${params.version}
    ===================================
    Usage:

    This pipeline can be run specifying parameters in a config file or with command line flags.   

    To override existing values from the command line, please type these parameters:

	Mandatory arguments:
	--genomeFasta           Path to reference genome to be used for analysis (must be surrounded by quotes)                          
	--outputDir             Path to output directory where the results will be saved. (must be surrounded by quotes)
	--reads                 Path to input data (must be surrounded by quotes)

	Read preparation options:
	--singleEnd             options: true|false. true for single reads; false for paired reads. Default: true.
	--readPrepTool          Options: fastp|trimmomatic. Tool to be used for read preparation. Default: fastp

	trimmomatic-specific options:
	--trimOptions           Trimmomatic commands in a single line. (Must be surrounded by quotes)

	fastp-specific options:
	--guess_adapter         options: true|false. auto-detect adapter from input file. Only available with fastp
	--forward_adaptor       adapter sequence to be clipped off (forward) (must be surrounded by quotes). cannot be combined with guess_adapter
	--reverse_adaptor       adapter sequence to be clipped off (reverse) (must be surrounded by quotes). cannot be combined with guess_adapter
	--min_read_length       minimum length of read to be kept after trimming for downstream analysis. Default: 70
	--min_base_quality      minimum base quality. Default: 20
	--trimN                 options: true|false. Trim Ns on both ends of read. Default: true

	virema-specific options:
	--viremaApp             Path to virema application (must be surrounded by quotes)
	--micro                 The minimum length of microindels
	--defuzz                If a start position is fuzzy, then its reported it at the 3' end (3), 5' end (5), or the center of fuzzy region (0)
	--mismatch              This is the value of --N option in ViRema
	--X                     This is the value of --X in ViRema for setting number of nucleotides not allowed to mismatch on either end of read
	--downsample            total unaligned reads to downsample to and use for ViRema
	
	Biocluster-specific options:
	--executor              System-specific variable. See online documentation for more info. Default: slurm. 
	--myQueue               System-specific variable. See online documentation for more info. Default: normal 
	--trimMemory            Memory in GB for trimming step. Default: 15
	--trimCPU               CPUs for trimming step. Default: 6
	--bowtie2Mem            Memory in GB for alignemnt step. Default: 15
	--bowtie2CPU            CPUs for alignment step. Default: 6
	--viremaMem             Memory in GB for ViRema step. Default: 60
	--viremaCPU             CPUs for ViRema step. Default: 6

	Module versions:
	--fastpMod              name of fastp module
	--trimMod               name of Trimmomatic module
	--trimVersion           version number of Trimmomatic tool
	--fastqcMod             name of FastQC module
	--multiQCMod            name of MultiQC module
	--bowtie2Mod            name of Bowtie2 module
	--bowtie1Mod            name of Bowtie module
	--pythonMod             name of Python module
	--perlMod               name of Perl module
	--samtoolsMod           name of SamTools module

	Other arguments:
	--email                 Set this parameter to your e-mail address to get a summary e-mail with details of the run sent to you when the workflow exits
	--scriptdir             Path to folder with perl scripts (must be surrounded by quotes)
    """.stripIndent()
}

// Show help message
params.help = false
if (params.help){
    helpMessage()
    exit 0
}

// Path to folder with perl scripts
params.scriptdir = "/home/groups/hpcbio_shared/cbrooke_lab/DARPA-project/src/Brooke-DARPA/"

// Output path
params.outputDir = false

// Path to raw reads folder
params.reads = false

// Paths to reference genome 
params.genomeFasta  = false
params.genomesDir   = "/igbgroup/groups/hpcbio_shared/cbrooke_lab/DIPanalysis-Zhe-2019-10/data/genome/nf-produced"

// Read preparation options
params.singleEnd = true        
params.readPrepTool = 'fastp'   

// fastp-specific options
params.guess_adapter = true  
params.forward_adaptor = false  
params.reverse_adaptor = false  
params.min_read_length = '75' 
params.min_base_quality = '20'  
params.trimN = true

// trimmomatic-specific options
//params.trimOptions = 'ILLUMINACLIP:$EBROOTTRIMMOMATIC/adapters/TruSeq3-PE-2.fa:2:15:10 SLIDINGWINDOW:3:20 LEADING:28 TRAILING:28 MINLEN:75'
params.trimOptions = false

// bowtie2-specific options
params.scoreMin = 'L,0,-0.3'

// ViRema-specific options
params.viremaApp = "/home/groups/hpcbio_shared/cbrooke_lab/DARPA-project/apps/ViReMa_with_Fuzz"
params.micro = '20' 
params.defuzz = '3' 
params.mismatch = '1'
params.X = '8'
params.downsample = false

// Biocluster-specific options. List memory in gigabytes.
params.executor = 'slurm'
params.myQueue = 'normal'
params.trimMemory = '15'
params.trimCPU = '6'
params.bowtie2Mem = '15'
params.bowtie2CPU = '6'
params.viremaMem = '60'
params.viremaCPU = '6'
params.defaultMem = '10'
params.defaultCPU = '2'

// Module versions
params.trimMod = 'Trimmomatic/0.38-Java-1.8.0_152'
params.trimVersion = '0.38' /*Put the version here only*/
params.fastpMod = 'fastp/0.20.0-IGB-gcc-4.9.4 '
params.fastqcMod = 'FastQC/0.11.8-IGB-gcc-4.9.4-Java-1.8.0_152'
params.bowtie2Mod = 'Bowtie2/2.3.2-IGB-gcc-4.9.4'
params.bowtie1Mod = 'Bowtie/1.2.0-IGB-gcc-4.9.4'
params.pythonMod = 'Python/2.7.13-IGB-gcc-4.9.4'
params.perlMod = 'Perl/5.24.1-IGB-gcc-4.9.4'
params.multiQCMod = 'MultiQC/1.7-IGB-gcc-4.9.4-Python-3.6.1'
params.samtoolsMod = 'SAMtools/1.9-IGB-gcc-4.9.4'
params.seqtkMod = 'seqtk/1.2-IGB-gcc-4.9.4'

// Other arguments:
params.email = false

// output subfolder - DO NOT EDIT
params.trimPath = "${params.outputDir}/read-preparation"
params.FQrawPath = "${params.outputDir}/fastqc/raw"
params.FQtrimPath = "${params.outputDir}/fastqc/trim"
params.multiQCPath = "${params.outputDir}/fastqc"
params.alignPath = "${params.outputDir}/align"
params.viremaPath = "${params.outputDir}/virema"

/*
* Step 1. Sanity checks
*/

if (params.readPrepTool != 'fastp' && params.readPrepTool != 'trimmomatic'){
    exit 1, "Must set read Preparation Tool using --readPrepTool possible values: fastp|trimmomatic"
}
if (params.readPrepTool != 'fastp' && params.guess_adapter){
    exit 1, "Must set read Preparation Tool to fastp using --readPrepTool to be able to auto-detect adapters with --guess_adapter"
}
if (params.readPrepTool == 'trimmomatic' && !params.trimOptions){
    exit 1, "Must specify trimming options with --trimOptions when --readPrepTool is set to trimmomatic"
}

// the input channel

Channel
    .fromFilePairs( params.reads, size: params.singleEnd ? 1 : 2)
    .ifEmpty { error "Cannot find any reads matching: ${params.reads}" }
    .into { reads2Qual; reads2Trim1; reads2Trim2; reads2Trim3; reads2Trim4 }

// the log file at the beginning of the run

log.info "==================================="
log.info " DIP-pipeline  ~  version ${params.version}"
log.info "==================================="
def summary = [:]
summary['Reference']    = params.genomeFasta
summary['Reads']        = params.reads
summary['Data Type'] = params.singleEnd ? 'Single-End' : 'Paired-End'
summary['Read prep tool']  = params.readPrepTool
if(params.readPrepTool == 'fastp') {
	summary['fastp version']   = params.fastpMod
	summary['autodetect adapter']   = params.guess_adapter
	summary['Forward adapter seq'] = params.forward_adaptor
	summary['Reverse adapter seq'] = params.reverse_adaptor
	summary['trim Ns']     = params.trimN
}
if(params.readPrepTool == 'trimmomatic') {
	summary['Trimmomatic version']   = params.trimMod
	summary['trimming options']   = params.trimOptions
}
summary['bowtie2 version'] = params.bowtie2Mod
summary['bowtie2 aln options'] = params.scoreMin
summary['bowtie1 version'] = params.bowtie1Mod
summary['ViRema path'] = params.viremaApp
summary['ViRema micro'] = params.micro 
summary['ViRema defuzz'] = params.defuzz 
summary['ViRema mismatch'] = params.mismatch
summary['ViRema --X option'] = params.X 
summary['scripts dir']     = params.scriptdir
summary['Output dir']     = params.outputDir
summary['Working dir']    = workflow.workDir
summary['Current home']   = "$HOME"
summary['Current user']   = "$USER"
summary['Current path']   = "$PWD"
if(params.email) { summary['E-mail Address'] = params.email }

log.info summary.collect { k,v -> "${k.padRight(15)}: $v" }.join("\n")
log.info "========================================="


/*
* Step 2. Preprocessing Genome
*/
   
genomeFile                  = file(params.genomeFasta)
genomePrefix                = genomeFile.getBaseName()
genomeStoreBowtie1          = "${params.genomesDir}/${genomePrefix}"
genomeStoreBowtie2          = "${params.genomesDir}/${genomePrefix}"

if( !genomeFile.exists() ) {
   exit 1, "Missing reference genome file: ${genomeFile}"
}

process bowtie2Index_genome{
    tag                    { gf }
    executor               params.executor
    cpus                   params.bowtie2CPU
    queue                  params.myQueue
    memory                 "$params.bowtie2Mem GB"
    module                 params.bowtie2Mod
    storeDir               genomeStoreBowtie2
    validExitStatus        0

    input:
    file gf from genomeFile

    output:
    file "*.bt2" into bowtie2IndexRef

    script:
    """
    bowtie2-build --threads ${task.cpus} ${gf} ${genomePrefix}
    """
}

process bowtie1Index_genome{
    tag                    { gf }
    executor               params.executor
    cpus                   params.bowtie2CPU
    queue                  params.myQueue
    memory                 "$params.bowtie2Mem GB"
    module                 params.bowtie1Mod
    storeDir               genomeStoreBowtie1
    validExitStatus        0

    input:
    file gf from genomeFile

    output:
    file "*.ebwt" into bowtie1IndexRef

    script:
    """
    bowtie-build ${gf} ${genomePrefix}
    """
}


/*
* Step 3. Read preparation
*/

if(params.readPrepTool == 'fastp') {

	process readPrep_fastp {
	    tag              "reads: $name"
	    executor         params.executor
	    cpus             params.trimCPU
	    queue            params.myQueue
	    memory           "$params.trimMemory GB"
	    module           params.fastpMod
	    publishDir       params.trimPath, mode: 'copy'
	    validExitStatus  0,1
	    errorStrategy   'finish'
	    
    	    input:
	    set name, file(reads) from reads2Trim2

	    output:
	    set val(name), file('*.trimmed.fq') optional true into  alnChannel
	    set val(name), file('*.json') optional true into  multiqc3    
	    file '*'

	    script: 
	    trimOptions      = params.trimN ? ' --cut_front  --cut_tail ' : ' ' 
	    adapterOptionsSE = params.guess_adapter ? ' ' : ' --adapter_sequence="${params.forward_adaptor}" '
	    adapterOptionsPE = params.guess_adapter ? ' --detect_adapter_for_pe ' : ' --detect_adapter_for_pe --adapter_sequence="${params.forward_adaptor}"  --adapter_sequence_r2="${params.reverse_adaptor}"  '
	    
	    if(params.singleEnd) {
		"""
		fastp --in1 ${reads[0]} --out1 ${name}.R1.trimmed.fq ${adapterOptionsSE} ${trimOptions} -l ${params.min_read_length}  --thread ${task.cpus} -w ${task.cpus} --html ${name}_fastp.html --json ${name}_fastp.json
		"""
	    } else {
		"""
		fastp --in1 ${reads[0]} --in2 ${reads[1]} --out1 ${name}.R1.paired.fq --out2 ${name}.R2.paired.fq  ${adapterOptionsPE}  ${trimOptions} -l ${params.min_read_length} --thread ${task.cpus} --html ${name}_fastp.html --json ${name}_fastp.json

	        cat ${name}.R1.paired.fq ${name}.R2.paired.fq > ${name}.both.trimmed.fq	
	        """
	    }	    

	}  /* end process */ 
		
	process readPrep_MultiQC_fastp {
	    executor         params.executor
	    cpus             params.defaultCPU
	    queue            params.myQueue
	    memory           "$params.defaultMem GB"
	    module           params.multiQCMod
	    publishDir       params.multiQCPath, mode: 'copy', overwrite: true
	    validExitStatus  0,1
	    errorStrategy   'finish'
	    
	    input:
	    file('*')  from multiqc3.collect()


	    output:
	    file "*_report.html" into multiqc_report_post
	    file "*"

	    script: 
	    """
	    multiqc .
	    """
	} /* end process */	

} /* end read prep with fastp */

if(params.readPrepTool == 'trimmomatic') {

	process readPrep_FASTQC_raw {
	    tag              "reads: $name"
	    executor         params.executor
	    cpus             params.defaultCPU
	    queue            params.myQueue
	    memory           "$params.trimMemory GB"
	    module           params.fastqcMod
	    publishDir       params.FQrawPath, mode: 'copy', overwrite: true
	    validExitStatus  0,1
	    errorStrategy   'finish'
	    
	    input:
	    set val(name), file(reads) from reads2Qual

	    output:
	    file('*.zip') optional true into  multiqc1 	    
	    file '*_fastqc.{zip,html}'

            script:
	    """
	    fastqc -t ${params.trimCPU} --noextract ${reads}
	    """
	} /* end process */

	process readPrep_trimmomatic {
	    tag              "reads: $name"
	    executor         params.executor
	    cpus             params.defaultCPU
	    queue            params.myQueue
	    memory           "$params.trimMemory GB"
	    module           params.trimMod
	    publishDir       params.trimPath, mode: 'copy'
	    validExitStatus  0,1
	    errorStrategy   'finish'
	    
    	    input:
	    set name, file(reads) from reads2Trim1

	    output:
	    set val(name), file('*.trimmed.fq') optional true into fastqcChannel
	    set val(name), file('*.trimmed.fq') optional true into alnChannel
	    file '*'

            script:
	    if(params.singleEnd) {
	       """
	       java -Xmx4g -XX:ParallelGCThreads=2 -jar \$EBROOTTRIMMOMATIC/trimmomatic-${params.trimVersion}.jar SE \
	       -threads $params.trimCPU -phred33 ${reads[0]} \
	       ${name}.R1.trimmed.fq \
	       $params.trimOptions
	       """
	    } else {
	       """
	       java -Xmx4g -XX:ParallelGCThreads=2 -jar \$EBROOTTRIMMOMATIC/trimmomatic-${params.trimVersion}.jar PE \
	       -threads $params.trimCPU -phred33 ${reads[0]} \
	       ${name}.R1.paired.fq ${name}.R1.unpaired.fq \
	       ${name}.R2.paired.fq ${name}.R2.unpaired.fq \
	       $params.trimOptions
	              
	       cat ${name}.R1.paired.fq ${name}.R2.paired.fq > ${name}.both.trimmed.fq
	       """
            }
 	}  /* end process */
 	
	process readPrep_FASTQC_trim {
	    tag              "reads: $name"
	    executor         params.executor
	    cpus             params.defaultCPU
	    queue            params.myQueue
	    memory           "$params.trimMemory GB"
	    module           params.fastqcMod
	    publishDir       params.FQtrimPath, mode: 'copy', overwrite: true
	    validExitStatus  0,1
	    errorStrategy   'finish'
	    
	    input:
	    set val(name), file(reads) from fastqcChannel

	    output:
	    file('*.zip') optional true into  multiqc2 	    
	    file '*_fastqc.{zip,html}'

            script:
	    """
	    fastqc -t ${params.trimCPU} --noextract ${reads}
	    """
	}  /* end process */ 
 	
	process readPrep_MultiQC_trimmomatic {
	    executor         params.executor
	    cpus             params.defaultCPU
	    queue            params.myQueue
	    memory           "$params.defaultMem GB"
	    module           params.multiQCMod
	    publishDir       params.multiQCPath, mode: 'copy', overwrite: true
	    validExitStatus  0,1
	    errorStrategy   'finish'
	    
	    input:
	    file('/raw/*') from multiqc1.collect()
	    file('/trim/*') from multiqc2.collect()

	    output:
	    file "*_report.html" into multiqc_report_post
	    file "*_data"

            script:
	    """
	    multiqc .
	    """
	}  /* end process */ 	
} /* end read prep with trimmomatic */

/*
* Step 4. Bowtie2 alignment
*/
process runbowtie2 {
    tag              "$name"
    executor         params.executor
    cpus             params.bowtie2CPU
    queue            params.myQueue
    memory           "$params.bowtie2Mem GB"
    module           params.bowtie2Mod,params.samtoolsMod
    publishDir       params.alignPath, mode: 'copy'
    validExitStatus  0,1
    errorStrategy   'finish'
    
    input:
    set name, file(trimRead) from alnChannel
    file bowtie2Index from bowtie2IndexRef

    output:
    set val(name), file('*_unaligned.fq') into viremaChannel
    file "*"

    script: 
    """
    bowtie2 -p $params.bowtie2CPU -x $genomePrefix -U $trimRead --score-min $params.scoreMin --al ${name}_aligned.fq --un ${name}_unaligned.fq | samtools view -bSh  - > ${name}.bam
    """
}

/*
* Step 5. ViReMa
*/
process runVirema {
    tag              "$name"
    executor         params.executor
    cpus             params.viremaCPU
    queue            params.myQueue
    memory           "$params.viremaMem GB"
    module           params.bowtie1Mod,params.pythonMod,params.seqtkMod
    publishDir       params.viremaPath, mode: 'copy'
    validExitStatus  0,1
    errorStrategy   'finish'
    
    input:
    set name, file(unalign) from viremaChannel
    file bowtie1Index from bowtie1IndexRef
    
    output:
    set val(name), file('*Virus_Recombination_Results.txt') into virema_sum
    file "*"

    script: 
    if(params.downsample){
	    """
      numlines="\$(wc -l $unalign | cut -d ' ' -f1)"
      echo "numlines before downsampling \${numlines}"
      seqtk sample -s10017 $unalign $params.downsample > ${name}_downsample.fq
      numlines="\$(wc -l ${name}_downsample.fq | cut -d ' ' -f1)"
      echo "numlines after downsampling \${numlines}" 
	    awk '{print (NR%4 == 1) ? "@1_" ++i : \$0}' ${name}_downsample.fq >  ${name}_rename.fq    
	    python ${params.viremaApp}/ViReMa.py --MicroInDel_Length $params.micro -DeDup --Defuzz 3 \
	    --N ${params.mismatch} --X ${params.X} --Output_Tag ${name} -ReadNamesEntry --p $params.viremaCPU \
	    $genomePrefix ${name}_rename.fq ${name}.results
	    """
    } else {
	    """   
	    awk '{print (NR%4 == 1) ? "@1_" ++i : \$0}' $unalign >  ${name}_rename.fq    
	    python ${params.viremaApp}/ViReMa.py --MicroInDel_Length $params.micro -DeDup --Defuzz 3 \
	    --N ${params.mismatch} --X ${params.X} --Output_Tag ${name} -ReadNamesEntry --p $params.viremaCPU \
	    $genomePrefix ${name}_rename.fq ${name}.results
	    """
    } /* end if */
}

/*
* Step 6. ViReMa Summary of results (w/ perl scripts)
*/
process calcSummary {
    tag              "$name"
    executor         params.executor
    cpus             params.defaultCPU
    queue            params.myQueue
    memory           "$params.defaultMem GB"
    module           params.perlMod
    publishDir       params.viremaPath, mode: 'copy'
    errorStrategy   'finish'
    
    input:
    set name, file('in_file') from virema_sum

    output:
    set val(name), file('*.par*')

    script: 
    """
    perl ${params.scriptdir}/parse-recomb-results-Fuzz.pl -i $in_file -o ${name}.par -d 1
    perl ${params.scriptdir}/parse-recomb-results-Fuzz.pl -i $in_file -o ${name}.par5 -d 5
    """
}


/*
 * Completion e-mail notification
 */

workflow.onComplete {

    if (params.email) {
      def subject = "[DIP-pipeline] Successful: $workflow.runName"
      if(!workflow.success){
         subject = "[DIP-pipeline] FAILED: $workflow.runName"
      }
      
      def BODY = """

===============================================================================
[DIP-pipeline] execution summary
===============================================================================
Completed at : ${workflow.complete}
Duration     : ${workflow.duration}
Success      : ${workflow.success}
workDir      : ${workflow.workDir}
exit status  : ${workflow.exitStatus}
Error report : ${workflow.errorReport ?: '-'}
Error message: ${workflow.errorMessage ?: '-'}
===============================================================================

    """
    
      try {
        // Try to send HTML e-mail using sendmail
        def html_email = "To: $params.email\nSubject: $subject\nMime-Version: 1.0\nContent-Type: text/html\n\n${BODY}";
        def smproc = [ 'sendmail', '-t' ].execute() << html_email
        log.debug "[DIP-pipeline] Sent summary e-mail using sendmail"
      } catch (all) {
        // Catch failures and try with plaintext
        [ 'mail', '-s', subject, params.email ].execute() << BODY
      }
      log.info "[DIP-pipeline] COMPLETED. Sent summary e-mail to $params.email"
   }  
}


workflow.onError {
    if (params.email) {
      def subject = "[DIP-pipeline] Successful: $workflow.runName"
      if(!workflow.success){
         subject = "[DIP-pipeline] FAILED: $workflow.runName"
      }
      
      def BODY = """

===============================================================================
[DIP-pipeline] execution summary
===============================================================================
Completed at : ${workflow.complete}
Duration     : ${workflow.duration}
Success      : ${workflow.success}
workDir      : ${workflow.workDir}
exit status  : ${workflow.exitStatus}
Error report : ${workflow.errorReport ?: '-'}
Error message: ${workflow.errorMessage ?: '-'}
===============================================================================

    """
    
      try {
        // Try to send HTML e-mail using sendmail
        def html_email = "To: $params.email\nSubject: $subject\nMime-Version: 1.0\nContent-Type: text/html\n\n${BODY}";
        def smproc = [ 'sendmail', '-t' ].execute() << html_email
        log.debug "[DIP-pipeline] Sent summary e-mail using sendmail"
      } catch (all) {
        // Catch failures and try with plaintext
        [ 'mail', '-s', subject, params.email ].execute() << BODY
      }
      log.info "[DIP-pipeline] FAILED. Sent summary e-mail to $params.email"
   }  
}