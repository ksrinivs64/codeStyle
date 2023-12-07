#!/bin/bash

ME=$0
DIR=`dirname $ME`

WS=`mktemp -d`

trap 'rm -rf $WS' EXIT

mkdir -p $WS

python $DIR/../normalize.py $1 >$WS/input.py
python $DIR/../normalize.py $3 > $WS/expected.py

diff -B $WS/input.py $WS/expected.py | gawk -f $DIR/codeDiffs.awk | sort > $WS/expected_change.txt

diff -B $WS/input.py $2 | gawk -f $DIR/codeDiffs.awk  | sort > $WS/actual_change.txt

missing_changes=`comm -23  $WS/expected_change.txt  $WS/actual_change.txt | wc -l`

unexpected_changes=`comm -13  $WS/expected_change.txt  $WS/actual_change.txt | wc -l`

expected_changes=`comm -12  $WS/expected_change.txt  $WS/actual_change.txt | wc -l`

gold_expected=`cat $WS/expected_change.txt | wc -l`

echo $expected_changes $missing_changes $unexpected_changes $gold_expected
