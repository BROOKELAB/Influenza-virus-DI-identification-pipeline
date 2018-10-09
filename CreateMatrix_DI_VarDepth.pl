#!/usr/bin/perl

#use strict;
use Cwd;
use File::Spec; 

# defaults, initializations, and constants
my $help = "\nCreateMatrix_DIpar5\nCreates a matrix of counts from DI pipeline result files.\n".
          "\nOptions-Switches:\n".
          "\t-d  Option: specify directory with par5 result files. Required.\n".
          "\t-o  Option: specify output file name. Default=STDOUT.\n".
          "\t-m  Option: specify minimum read support.\n\t\t    Default=0 (no filter unless option -v is set).\n".
          "\t-v  Option: specify variable minimum read support file. Optional.\n".
          "\t-f  Option: specify read support filter type. Optional, default=1.\n".
          "\t\t1: single column minimum\n".
          "\t\t2: additive column minimum\n".
          "\n************\nAuthor: J. Cristobal Vera, email: jcvera\@illinois.edu\n";
my $usage = "\nUsage:\nCreateMatrix_DIpar5.pl -d [Input Directory] -o [Output File] -f [Filter Type] -m [Min Read Coverage] -v [Variable Min Read Coverage File]\n";
my $n = 0;
my ($indir,$title);
my $outfh = 'OUT';
my $na = 'NA';  #missing value symbol; use NA for R and '' for excel or JMP
my $minreads_default = 0; ##minimum required read support. zero = no filter unless option -v is set
my $filter = 1;   ##filter type
my $varfile;  #file with variable min read support values. if a segment value is missing, $minreads value is used
my %minreads;
my %rows;

#process command line custom script tags
my %cmds = ReturnCmds(@ARGV);
die "\n$help\n$usage\n" if ($cmds{'h'});
$indir = $cmds{'d'} if ($cmds{'d'});
if ($cmds{'o'}) {
  $outfh = 'OUT';
  open ($outfh, ">$cmds{'o'}") or die "Cannot create $cmds{'o'}: $!\n";
}
if ($cmds{'v'}) {
  $varfile = $cmds{'v'};
  open (VAR, "<$varfile") or die "Cannot open $varfile: $!\n";
  my $x = 0;
  while (my $line = <VAR>){
    $x++;
    chomp $line;
    my @line = split /\t/,$line;
    $minreads{$line[0]} = $line[1];
  }
  print STDERR "\nMinimum read support values found: $x\n\n";
}
$filter = $cmds{'f'} if ($cmds{'f'});
$minreads_default = $cmds{'m'} if ($cmds{'m'});

#make absolute paths
$indir = File::Spec->rel2abs($indir);

#get all file names
opendir(INDIR,$indir) or die "Can't open directory: $indir: $!\n";
my @files = grep {m/.+\.par5$/ && -f "$indir/$_"} readdir(INDIR);
close(INDIR);
@files = sort @files;
my @samples;

foreach my $file (@files){
  my $filedir = "$indir/$file";
  my $sample = $file;
  $sample =~ s/_L00[0-9].+\.par5$//;
  $sample =~ s/\.par5$//;
  push @samples,$sample;
  $n += 1;
  $title = "DIs\t$sample\_$n" if ($n == 1);
  $title .= "\t$sample\_$n" if ($n > 1);
  open (IN, "<$filedir") or die "Cannot open $filedir: $!\n";
  while (my $line = <IN>){
    chomp $line;
    my $minreads = 0;
    my @line = split /\t/,$line;
    next if ($line[0] eq 'Segment');
    my ($seg,$start,$stop,$reads,$type) = ($line[0],$line[1],$line[2],$line[5],$line[6]);
    
    ##add variable min read support value##
    if ($varfile and exists $minreads{$seg}){
      $minreads = $minreads{$seg};
    }
    else{
      $minreads = $minreads_default;
    }
    
    my $id = "$seg\_$start\_$stop";
    $rows{$id}{$sample} = $reads;
    if ($filter == 1){
      ##Jessica changed script here...
      unless ($reads and $reads >= $minreads){
	$rows{$id}{$sample} = "NA";
      }
    }
    elsif ($filter == 2){
      $rows{$id}{'filter'} += $reads if ($reads and $rows{$id}{'filter'} ne 'pass');
      $rows{$id}{'filter'} = 'pass' if ($rows{$id}{'filter'} >= $minreads);
    }
  }
  close(IN);
}
print STDERR "\nSample files parsed: $n\n\n";
@samples = sort @samples;

#print out
print $outfh "$title\n";
foreach my $id (sort keys %rows){
  ##Jessica changed script here... 
  if($filter == 2){
  if ($rows{$id}{'filter'} eq 'pass'){
    print $outfh "$id";
    foreach my $sample (@samples){
      print $outfh "\t$rows{$id}{$sample}" if (exists $rows{$id}{$sample});
      print $outfh "\t$na" if (!exists $rows{$id}{$sample});
    }
    print $outfh "\n";
  }
  }
  elsif($filter == 1){
    print $outfh "$id";
    foreach my $sample (@samples){
      print $outfh "\t$rows{$id}{$sample}" if (exists $rows{$id}{$sample});
      print $outfh "\t$na" if (!exists $rows{$id}{$sample});
    }
    print $outfh "\n";
  }
}

sub ReturnCmds{
  my (@cmds) = @_;
  my ($opt);
  my %cmds;
  foreach my $cmd (@cmds){
    if (!$opt and $cmd =~ m/^-([a-zA-Z])/) {
      $opt = $1;
    }
    elsif ($opt and $cmd =~ m/^-([a-zA-Z])/){
      $cmds{$opt} = 1;
      $opt = $1;
    }
    elsif ($opt){
      $cmds{$opt} = $cmd;
      $opt = '';
    }
  }
  $cmds{$opt} = 1 if ($opt);
  return %cmds;
}

sub CheckJobs{
    my (@jobinfo) = @_;
    foreach my $job (@jobinfo){
        if ($job =~ m/\/(NGS[0-9]+)\.job/) {
            my $id = $1;
            return 0 if (!-e "$id.b.err");
        }
        else{
            die "\nError: job ID not found.\n";
        }
    }
    return 1;
}
