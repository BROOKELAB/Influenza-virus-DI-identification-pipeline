#!/usr/bin/perl

use Cwd;
use File::Spec;

#open (INFILE, "$ARGV[0]") or die "Could not open file $ARGV[0]!\n";
#open (OUTFILE, ">$ARGV[1]") or die "Could not open output file $ARGV[1]!\n";
#open (UNKNOWN, ">$ARGV[1].unknown") or die "Could not open output file $ARGV[1]!\n";

#Parameters & help info
my $help = "\nparse-recomb-results-Fuzz.pl\nSummarizes the results given in the Virus_Recombination_Results.txt file produced by ViReMa. This takes Fuzz factor values into account as well.\n".
          "\nOptions-Parameters:\n".
          "\t-d  Option: specify the minimum depth needed to retain a DI.\n".
	  "\t-o  Option: specify output file name.\n".
	  "\t-i  Option: specify input file name.\n".
          "\n************\nAuthor: Jessica R. Holmes, email: jholmes5\@illinois.edu\n";
my $usage = "\nUsage:\nparse-recomb-results-Fuzz.pl -d [Depth] -o [Output File] -i [Input File]\n";
my $outfh = 'OUT';
my $infh = 'IN';
my $outUK = 'UK';
my %cmds = ReturnCmds(@ARGV);
die "\n$help\n$usage\n" if ($cmds{'h'});
my $depth = $cmds{'d'} if ($cmds{'d'});
if ($cmds{'o'}) {
  $outfh = 'OUT';
  open ($outfh, ">$cmds{'o'}") or die "Cannot create $cmds{'o'}: $!\n";
  open ($outUK, ">$cmds{'o'}.unknown") or die "Cannot create $cmds{'o'}: $!\n";
}
if ($cmds{'i'}) {
  $infh = 'IN';
  open ($infh, "<$cmds{'i'}") or die "Cannot create $cmds{'i'}: $!\n";
}

#Other Program variables
my $i=0; #Keeps track of whether in the midst of a valid segment
my %forhash = (); #Saves forward DI's above 50 support
my %revhash = (); # Saves reverse DI's above 50 support
my $revbool = 0; #Keeps track of whether segment is reverse
my $seg = ""; # Saves current segment

while(<$infh>){
	my $line = $_;
        chomp $line;
	if($line =~ /^\@NewLibrary/ && $i==0){
		$line =~ /^\@NewLibrary\:\s(.+)_to_(.+)/;
 		if($1 eq $2){
			$seg = $1;
			if ($seg =~ /.+_RevStrand/){
				$seg =~ /(.+)_RevStrand/;
				$revbool = 1;
				$seg = $1;
			}
			$i=1;
		}
		else{ next;}
	}
	elsif($line =~ /\d+_to_\d+_#_\d+/ && $i==1){
		$line =~ /(\d+)_to_(\d+)_#_(\d+)/;
		if($revbool){
			$key = "$seg" . "_" . $2 . "_" . $1;
			$val = $3;
		
			$fuzzline = <$infh>;
			chomp $fuzzline;
			$fuzzline =~ /^\d+_\d+_Fuzz=(\d+)\t*.*$/;
			$fuzz = $1;
#			print "fuzzline = $fuzzline; fuzz = $fuzz\n";
			$val = $val . "_" . $1;
		
			$revhash{$key} = $val;
		}
		else{
			$key = "$seg" . "_" . $1 . "_" . $2;
                        $val = $3;
			
			$fuzzline = <$infh>;
                        chomp $fuzzline;
                        $fuzzline =~ /^\d+_\d+_Fuzz=(\d+)\t*.*$/;
                        $fuzz = $1;
                        $val = $val . "_" . $1;			

			$forhash{$key} = $val;
#			if($1 > $2){print "Insertion: $key $val\n";}
		}
	}
        elsif($line =~ /^\@EndofLibrary/ && $i==1){
		$i=0;
		$revbool = 0;
	}
}

%mergehash = (%revhash, %forhash);
print $outfh "Segment\tStart\tStop\tForward_support\tReverse_support\tTotal_support\tFuzz_factor\n";
print $outUK "Segment\tStart\tStop\tForward_support\tReverse_support\tTotal_support\tFuzz_factor\n";

#Print table
for $k (sort keys %mergehash){
	@arr = split(/_/, $k);
	$indel = "D";
	if($arr[1] > $arr[2]){$indel = "I";}

	if(exists $revhash{$k} && exists $forhash{$k}){
		@revarr = split(/_/,$revhash{$k});
		@forarr = split(/_/,$forhash{$k});
		$total = $revarr[0] + $forarr[0];
		$fuzz = $forarr[1];
		if($total >= $depth){
			if($indel eq "D"){
			print $outfh "$arr[0]\t$arr[1]\t$arr[2]\t$forarr[0]\t$revarr[0]\t$total\t$fuzz\n";
			}
			else{
			print $outUK "$arr[0]\t$arr[1]\t$arr[2]\t$forarr[0]\t$revarr[0]\t$total\t$fuzz\n";
			}
		}
	}
	elsif(exists $forhash{$k}){
		if($forhash{$k} >= $depth){
			@forarr = split(/_/,$forhash{$k});
                        $total = $forarr[0];
                        $fuzz = $forarr[1];
			if($indel eq "D"){
			 print $outfh "$arr[0]\t$arr[1]\t$arr[2]\t$forarr[0]\t0\t$total\t$fuzz\n";
			}
			else{
			 print $outUK "$arr[0]\t$arr[1]\t$arr[2]\t$forarr[0]\t0\t$total\t$fuzz\n";
			}
		}
	}
	else{
		if($revhash{$k} >= $depth){
			@revarr = split(/_/,$revhash{$k});
                        $total = $revarr[0];
                        $fuzz = $revarr[1];
			if($indel eq "D"){
			print $outfh "$arr[0]\t$arr[1]\t$arr[2]\t0\t$revarr[0]\t$total\t$fuzz\n";
			}
			else{
			print $outUK "$arr[0]\t$arr[1]\t$arr[2]\t0\t$revarr[0]\t$total\t$fuzz\n";
			}
		}
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
