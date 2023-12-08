#!/bin/bash

for DAT in $1/*/Python; do
    IO=`dirname $DAT`
    IO=`basename $IO`
    for s in `ls $DAT | egrep 's[0-9]*[.]py'`; do
	STEM=`basename $s .py`
	for p in $DAT/$STEM_*_input.py; do
	    PROBLEM=`echo $p | sed 's/.*_\([^_]*\)_input.py/\1/'`
	    for m in $DAT/${STEM}_${PROBLEM}_pred_*.py; do
		MODEL=`echo $m | sed 's/.*_pred_\([^_]*\).py/\1/'`
		ls ${IO}/Python/${STEM}_${PROBLEM}_pred_${MODEL}.py
	    done
	done
    done
done
