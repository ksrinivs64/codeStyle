#!/bin/bash

DIR=`dirname $0`

WS=`mktemp -d`

X=`basename $1`

trap 'rm -rf $WS' EXIT

for DAT in $1/*/Python; do
    IO=`dirname $DAT`
    IO=`basename $IO`
    for s in `ls $DAT | egrep 's[0-9]*[.]py$'`; do
	STEM=`basename $s .py`      
	for p in $DAT/$STEM_*_input.py; do
	    PROBLEM=`echo $p | sed 's/.*_\([^_]*\)_input.py/\1/'`
	    for m in $DAT/${STEM}_${PROBLEM}_pred_*.py; do
		MODEL=`echo $m | sed 's/.*_pred_\([^_]*\).py/\1/'`

		if test -f $2/${IO}/input.txt ; then
		    bash $DIR/ulimitit.sh 60 python $1/${IO}/Python/${STEM}_${PROBLEM}_pred_${MODEL}.py < $2/${IO}/input.txt > ${WS}/out 2>&1
		else
		    bash $DIR/ulimitit.sh 60 python $1/${IO}/Python/${STEM}_${PROBLEM}_pred_${MODEL}.py < /dev/null > ${WS}/out 2>&1
		fi
		echo -n "${IO},${STEM},${PROBLEM},${MODEL},"
		if diff ${WS}/out $2/${IO}/output.txt > /dev/null 2>&1; then
		    echo -n "passed,"
		else
		    echo -n "failed,"
		fi

		model_input=$(realpath $(echo $m | sed 's/\(.*\)_pred_.*.py/\1_input.py/'))
		codenet_py=$(realpath $(echo $m | sed 's/\(.*s[0-9]*\)_[a-z]*_pred_.*.py/\1.py/'))
	    
		bash $DIR/codeCompare.sh $model_input $m $codenet_py $WS

	    done
	done
    done
done
