
#! /bin/bash
# For this script it's advisable to use a shell, such as Bash,
# that supports a TAR_FD value greater than 9.

echo "$TAR_VOLUME of $TAR_ARCHIVE:" 

name=`expr $TAR_ARCHIVE : '\(.*\)-[0-9]*$'`

case $TAR_SUBCOMMAND in
-c)       ;;
-d|-x|-t) test -r ${name:-$TAR_ARCHIVE}-$TAR_VOLUME || exit 1
          ;;
*)        exit 1
esac

echo ${name:-$TAR_ARCHIVE}-$TAR_VOLUME >&$TAR_FD
