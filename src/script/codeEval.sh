#!/bin/bash

ME=$0
DIR=`dirname $ME`

PTH=$1

for INPUT in $PTH/*_input.py; do
    
    OUTPUT=`echo $INPUT | sed s/_input/_output/g`
    EXPECTED=`echo $INPUT | sed s/_input/_expected/g`

    FN=`basename $INPUT`
    echo -n "$FN "
    bash $DIR/codeDiffs.sh $INPUT $OUTPUT $EXPECTED
done
