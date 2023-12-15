#!/bin/bash

ME=$0
DIR=`dirname $ME`

PTH=$1

#echo $1

for EXPECTED in `find $1 -name '*.py' | grep -E 's[0-9]*.py$'`; do
    FL=`echo $EXPECTED|sed 's/[.]py$//g'`
    OUTPUT=${FL}_$2_pred_$3.py
    INPUT=${FL}_$2_input.py

    FN=`basename $INPUT`
#    echo -n "$FN "
#    echo $INPUT
#    echo $OUTPUT
#    echo $EXPECTED
    bash $DIR/codeDiffs.sh $INPUT $OUTPUT $EXPECTED True
done
