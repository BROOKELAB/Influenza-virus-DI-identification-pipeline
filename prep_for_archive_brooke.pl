#!/usr/bin/env perl
use 5.016;
use strict;
use warnings;

# TODO: replace with File::Find?  This is sooo much cleaner...
use File::Find::Rule;
use File::Spec;
use Getopt::Long;
use Carp;
use File::Temp;
use Text::Wrap;
use FindBin;

$Text::Wrap::columns = 70;

my $from;

# TODO: allow variable 'tape' archive size?
my $TAR_SIZE = 2_000_000 * 1024;  # 2TB

# EXE
my $MD5SUM = '/usr/bin/md5sum';
my $TAR = '/bin/tar';
my $GZ = 'pigz';

# TODO: allow alternative scripts?
my $TAR_SCRIPT = "/home/groups/hpcbio_shared/cbrooke_lab/DARPA-project/src/Brooke-DARPA/split-tar.sh";

# ownership and perms

# TODO: will need to be modified to allow other group IDs; if so will need
# sanity check. Also, this only uses the current user ID (which perl requires,
# though we could simply fallback to system

my $GRP = 'hpcbio_cbrooke';
my $GID = getgrnam('hpcbio_cbrooke');
my $USER = $ENV{LOGNAME} || $ENV{USER} || getpwuid($<);
my $UID = getpwnam($USER);

# this is really meant to be called as a cluster job
my $procs = $ENV{SLURM_CPUS_PER_TASK} || 1;

my $USAGE = <<USAGE;

    perl $0 -d <DIR>

    This script is used simply to prep and archive a data directory:

    This takes an input directory, and

      1l) changes group ownership,
      2) sets file permissions to 0660 and dir permissions to 2770
      3) tar's up the directory, splitting into 2TB chunks (saving a file list in the process)
      4) runs pigz on the individual .tar files
      5) runs md5sum on all the *.tar.gz

    A fairly useless and overly verbose log file is also generated to keep tabs
    on the entire process.  It's there for your amusement.  Fun!

USAGE

GetOptions(
    'dir:s'    => \$from
);

die $USAGE unless (
    ($from      && -e $from     && -d $from)
);

# sanity check
for my $exe ( $TAR, $TAR_SCRIPT, $GZ, $MD5SUM ) {
    die "Problem: Either can't find executable $exe" unless -e $exe;
    die "Problem: $exe isn't executable" unless -x $exe;
}

$from =~ s/[\\\/]$//;
my $abspath = File::Spec->rel2abs($from);

my @warnings;

if (-e "$from.log.txt") {
    unlink "$from.log.txt";
}

open(my $logfh, '>', "$from.log.txt") or die $!;

print_log($logfh, "1. Changing group permissions");

for my $path (File::Find::Rule->in($from)) {
    if (-l $path ) {
        print_log_step($logfh, "Ignoring symlink $path");
        next;
    }

    # check if it's necessary to change group permissions
    if (-o $path) {
        my $status = chown $UID, $GID, $path;
        if ($status == 0) {
            print_log_step($logfh, "WARNING: Can't modify group with $path: $!", $status);
            die "Can't modify group for file $path: $!";
        }
        if (-d $path) {
            mod_perms('2770', $path, $logfh);
        } else {
            mod_perms('0660', $path, $logfh);
        }
    } else {
        # it has to be at least read/write by effective UID/GID
        if (! -w $path && ! -r $path) {
            print_log_step($logfh, "WARNING: Can't modify user/group on $path: Incorrect permissions", 1);
        }
    }
}

print_log($logfh, "1. Finished changing permissions");

print_log($logfh, "2. Compressing directory");

my $call;

if (-e "$from.file-list.txt") {
    unlink "$from.file-list.txt";
}

my $cmd;

eval {
    $cmd = <<COMPRESS;
$TAR -c -v -M --tape-length=$TAR_SIZE \\
    --file $from.tar \\
    --format=posix \\
    --new-volume-script=$TAR_SCRIPT \\
    --exclude-from=$FindBin::RealBin/excludes.txt \\
    --exclude-vcs \\
    --exclude-backups \\
    $from >> $from.file-list.txt
COMPRESS
    $call = system($cmd);
};

if ($call != 0) {
    print_log_step($logfh, "Problem tarring directory $from: $!", $call, "\nCMD: $cmd");
}

print_log($logfh, "2. Finished tarring directory");

for my $file (File::Find::Rule->file->name(qr/^$from.*?tar(-[\d]+)?$/)->in(File::Basename::dirname($from))) {
    $call = 0;
    my $cmd ="$GZ -9 -f $file";
    eval {
        $call = system( $cmd );
    };

    if ($call != 0) {
        print_log_step($logfh, "Problem compressing $file: $!", $call, "\nCMD: $cmd");
    } else {
        print_log_step($logfh, "$GZ run on $from");
    }
}

print_log($logfh, "2. Finished compressing directory");

### tar-gzip the folder in question up, getting a list of files.

print_log($logfh, "3. Generating MD5 on archive");

if (-e "$from.md5") {
    unlink "$from.md5";
}

for my $file (File::Find::Rule->file->name(qr/^$from.*?tar(-[\d]+)?\.gz$/)->maxdepth(1)->in('.')) {
    my $cmd = "$MD5SUM $file >> $from.md5";
    eval {
        $call = system( $cmd );
    };

    if ($call != 0) {
        print_log_step($logfh, "Problem running md5sum $from: $!", $call, "\nCMD: $cmd");
    } else {
        print_log_step($logfh, "$MD5SUM run on $from");
    }
}
print_log($logfh, "3. Finished MD5 on archive");

print_log($logfh, "4. Changing ownership/permissions on archive and logs");

for my $file ( glob("$from.*") ) {
    mod_perms('0660', $file, $logfh);
}

print_log($logfh, "4. Finished ownership/permissions changes on archive and logs");

#print_log($logfh, "5. Gzipping up logs and file lists");
#
#for my $file ( ("$from.file-list.txt") ) {
#    eval {
#        $call = system("$GZ -9 -f -p $ENV{SLURM_CPUS_PER_TASK} $file");
#    };
#    if ($call != 0) {
#        print_log_step($logfh, "Problem compressing $file: $!", $call);
#    } else {
#        print_log_step($logfh, "$GZ run on $from");
#    }
#
#}
#
#print_log($logfh, "5. Finished gzipping up logs and file lists");

exit;

####### tail the file list to make sure the archiving worked
### md5sum the tar.gz
### rsync the data, md5sum, and the file list to the archive

###### # Keep log of the transfer
###### #my $rsync_cmd = qx<rsync -a -v --stats "$backupfrom" "$backupto">;

### md5sum the archive copy (?) or copy the archive back and verify the transfer worked
### remove original tar.gz
### (remove the original data) # only after we have vetted this process

sub check_exe {
    my $exe = shift;
    return (-e $exe && -x $exe);
}

sub run_cmd {
    my $cmd = shift;
    return unless $cmd;
    my $status = system($cmd);
    if ($? == -1) {
        print "failed to execute: $!\n";
    }
    elsif ($? & 127) {
        printf "child died with signal %d, %s coredump\n",
            ($? & 127),  ($? & 128) ? 'with' : 'without';
    }
    else {
        printf "child exited with value %d\n", $? >> 8;
    }
}

sub mod_perms {
    my ($perms, $path, $logfh) = @_;

    my $cnt = chmod oct($perms), $path;
    if ($cnt == 0) {
        print_log_step($logfh, "WARNING: Permissions error with $path: $!", 1);
    } else {
        #print_log_step($logfh, "$path changed to $perms");
    }
    1;
}

sub print_log {
    my ($fh, $msg, $wrap) = @_;

    Carp::croak('Bad filehandle') unless defined $fh;

    say $fh "#####################################################################\n";
    say $fh $wrap ? wrap('','', "$msg\n") : "$msg\n";
    say $fh "#####################################################################\n";
}

sub print_log_step {
    my ($fh, $msg, $call) = @_;
    $call //= 0;
    Carp::croak('Bad filehandle') unless defined $fh;

    my $code = $call >> 8;

    if ( $call ) {
        say $fh "Exit code $code: $msg";
        Carp::croak("Exit code $code: $msg") if $call;
    } else {
        say $fh $msg;
    }
}
