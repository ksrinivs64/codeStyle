#!/bin/bash

DIR=`dirname $0`

RESULT_CSV=$1
CODENET_INPUT=$2
TEST_COL=$3
OUT_DIR=$4

gawk -v RS='"' 'NR % 2 == 0 { gsub(/\n/, "\\n") } { printf("%s%s", $0, RT) }' $RESULT_CSV | awk 'BEGIN { FS = "\",\"|\",|,\"|\<,\>" } { print $0 }' | gawk -v InputDir=$CODENET_INPUT -v TestCol=$TEST_COL -v OutDir=$OUT_DIR -f $DIR/test.awk

