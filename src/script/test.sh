#!/bin/bash

DIR=`dirname $0`

CODENET_INPUT=$1
TEST_COL=$2
OUT_DIR=$3

gawk -v RS='"' 'NR % 2 == 0 { gsub(/\n/, "\\n") } { printf("%s%s", $0, RT) }' | gawk 'BEGIN { FS = "\",\"|\",|,\"|\<,\>" } { print $0 }' | gawk -v InputDir=$CODENET_INPUT -v TestCol=$TEST_COL -v OutDir=$OUT_DIR -f $DIR/test.awk

