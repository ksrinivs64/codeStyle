#!/bin/bash

ME=$0
DIR=`dirname $ME`

PTH=$1

for INPUT in $PTH/*_inputs.py; do
    
    OUTPUT=`echo $INPUT | gsed s/_inputs/_transform/`
    EXPECTED=`echo $INPUT | gsed s/_inputs/_orig/`

    FN=`basename $INPUT`
    echo -n "$FN "
    bash $DIR/codeDiffs.sh $INPUT $OUTPUT $EXPECTED
done
