#!/usr/bin/perl -w

#use warnings;

open (INFILE, "$ARGV[0]") or die "Could not open file $ARGV[0]!\n";
open (OUTFILE, ">$ARGV[1]") or die "Could not open output file $ARGV[1]!\n";
open (UNKNOWN, ">$ARGV[1].unknown") or die "Could not open output file $ARGV[1]!\n";


my $i=0; #Keeps track of whether in the midst of a valid segment
my %forhash = (); #Saves forward DI's above 50 support
my %revhash = (); # Saves reverse DI's above 50 support
my $revbool = 0; #Keeps track of whether segment is reverse
my $seg = ""; # Saves current segment

while(<INFILE>){
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
			$revhash{$key} = $val;
#			if($2 > $1){print "Insertion(Rev): $key $val\n";} #Rough way to report Insertions
		}
		else{
			$key = "$seg" . "_" . $1 . "_" . $2;
                        $val = $3;
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
print OUTFILE "Segment\tStart\tStop\tForward_support\tReverse_support\tTotal_support\n";
print UNKNOWN "Segment\tStart\tStop\tForward_support\tReverse_support\tTotal_support\n";

#Print table
for $k (sort keys %mergehash){
	@arr = split(/_/, $k);
	$indel = "D";
	if($arr[1] > $arr[2]){$indel = "I";}

	if(exists $revhash{$k} && exists $forhash{$k}){
		$total = $revhash{$k} + $forhash{$k};
		if($total > 49){
			if($indel eq "D"){
			print OUTFILE "$arr[0]\t$arr[1]\t$arr[2]\t$forhash{$k}\t$revhash{$k}\t$total\n";
			}
			else{
			print UNKNOWN "$arr[0]\t$arr[1]\t$arr[2]\t$forhash{$k}\t$revhash{$k}\t$total\n";
			}
		}
	}
	elsif(exists $forhash{$k}){
		if($forhash{$k} > 49){
			if($indel eq "D"){
			print OUTFILE "$arr[0]\t$arr[1]\t$arr[2]\t$forhash{$k}\t0\t$forhash{$k}\n";
			}
			else{
			print UNKNOWN "$arr[0]\t$arr[1]\t$arr[2]\t$forhash{$k}\t0\t$forhash{$k}\n";
			}
		}
	}
	else{
		if($revhash{$k} > 49){
			if($indel eq "D"){
			print OUTFILE "$arr[0]\t$arr[1]\t$arr[2]\t0\t$revhash{$k}\t$revhash{$k}\n";
			}
			else{
			print UNKNOWN "$arr[0]\t$arr[1]\t$arr[2]\t0\t$revhash{$k}\t$revhash{$k}\n";
			}
		}
	}
}


