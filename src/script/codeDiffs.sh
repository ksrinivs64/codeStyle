#!/bin/bash

ME=$0
DIR=`dirname $ME`

INPUT=$1
OUTPUT=$2
EXPECTED=$3

diff $INPUT $EXPECTED | gawk -f $DIR/codeDiffs.awk > /tmp/expected_change.txt

diff $INPUT $OUTPUT | gawk -f $DIR/codeDiffs.awk  > /tmp/actual_change.txt

missing_changes=`comm -13  /tmp/expected_change.txt  /tmp/actual_change.txt | wc -l`

unexpected_changes=`comm -23  /tmp/expected_change.txt  /tmp/actual_change.txt | wc -l`

expected_changes=`comm -12  /tmp/expected_change.txt  /tmp/actual_change.txt | wc -l`

echo $expected_changes $missing_changes $unexpected_changes
