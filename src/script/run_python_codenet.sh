#!/bin/bash

WS=`mktemp -d`

trap 'rm -rf $WS' EXIT

for DAT in $1/*/Python; do
    IO=`dirname $DAT`
    IO=`basename $IO`
    for s in `ls $DAT | egrep 's[0-9]*[.]py'`; do
	STEM=`basename $s .py`
	for p in $DAT/$STEM_*_input.py; do
	    PROBLEM=`echo $p | sed 's/.*_\([^_]*\)_input.py/\1/'`
	    for m in $DAT/${STEM}_${PROBLEM}_pred_*.py; do
		MODEL=`echo $m | sed 's/.*_pred_\([^_]*\).py/\1/'`
		echo python $1/${IO}/Python/${STEM}_${PROBLEM}_pred_${MODEL}.py < $2/${IO}/input.txt 
		python $1/${IO}/Python/${STEM}_${PROBLEM}_pred_${MODEL}.py < $2/${IO}/input.txt > ${WS}/out 2>&1
		if diff ${WS}/out $2/${IO}/output.txt; then
		    echo "yes"
		else
		    echo "no"
		fi
		
	    done
	done
    done
done
