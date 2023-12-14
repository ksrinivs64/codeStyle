#!/bin/bash

ME=$0
DIR=`dirname $ME`

WS=`mktemp -d`

trap 'rm -rf $WS' EXIT

mkdir -p $WS

if test $4="True"; then
    python $DIR/../normalize.py $1 > $WS/input.py
    python $DIR/../normalize.py $3 > $WS/expected.py
    python $DIR/../normalize.py $2 > $WS/output.py
else
    cp $1 $WS/input.py
    cp $3 $WS/expected.py
fi

diff -B $WS/input.py $WS/expected.py | gawk -f $DIR/codeDiffs.awk | sort > $WS/expected_change.txt

diff -B $WS/input.py $WS/output.py | gawk -f $DIR/codeDiffs.awk  | sort > $WS/actual_change.txt

missing_changes=`comm -23  $WS/expected_change.txt  $WS/actual_change.txt | wc -l`

unexpected_changes=`comm -13  $WS/expected_change.txt  $WS/actual_change.txt | wc -l`

expected_changes=`comm -12  $WS/expected_change.txt  $WS/actual_change.txt | wc -l`

gold_expected=`cat $WS/expected_change.txt | wc -l`

actual_change=`cat $WS/actual_change.txt | wc -l`

echo $1 $expected_changes $missing_changes $unexpected_changes $gold_expected $actual_change
