#!/bin/bash

ME=$0
DIR=`dirname $ME`

INPUT=$1
OUTPUT=$2
EXPECTED=$3
diff -B $INPUT $EXPECTED | gawk -f $DIR/codeDiffs.awk | sort > /tmp/expected_change.txt

diff -B $INPUT $OUTPUT | gawk -f $DIR/codeDiffs.awk  | sort > /tmp/actual_change.txt

missing_changes=`comm -23  /tmp/expected_change.txt  /tmp/actual_change.txt | wc -l`

unexpected_changes=`comm -13  /tmp/expected_change.txt  /tmp/actual_change.txt | wc -l`

expected_changes=`comm -12  /tmp/expected_change.txt  /tmp/actual_change.txt | wc -l`

gold_expected=`cat /tmp/expected_change.txt | wc -l`

echo $expected_changes $missing_changes $unexpected_changes $gold_expected
