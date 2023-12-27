#!/bin/bash

DIR=`dirname $0`

WS=`mktemp -d`

X=`basename $1`

trap 'rm -rf $WS' EXIT

for DAT in $1/*; do
    IO=`basename $DAT`
    for s in `ls $DAT`; do

	for m in $DAT/$s/*_pred_*.java; do

	    model=$(echo $m | sed 's/.*_pred_\(.*\).java/\1/')
	    bench=$(echo $m | sed 's/.*_\(.*\)_pred.*.java/\1/')

	    cp $m $WS/Main.java

	    sol=`dirname $m`
	    sol=`basename $sol`
		
	    echo -n $IO,$sol,$model,$bench,
	    
	    if javac -d $WS $WS/Main.java 2>$WS/${model}_${bench}.err; then

		if test -f $2/${IO}/input.txt ; then
                    bash $DIR/ulimitit.sh 60 java -cp $WS $IO.$sol.Main < $2/${IO}/input.txt > ${WS}/out 2>&1
                else
                    bash $DIR/ulimitit.sh 60 java -cp $WS $IO.$sol.Main < /dev/null > ${WS}/out 2>&1
                fi

		if diff $2/${IO}/output.txt ${WS}/out > ${WS}/diff.out; then
		    echo -n "passed,"
		else
		    echo -n "failed,"
		fi

	    else
		echo -n "noncompile,"
	    fi

	    model_input=$(realpath $(echo $m | sed 's/\(.*\)_pred_.*.java/\1_input.java/'))
	    codenet_java=$(realpath $(echo $m | sed 's/\(.*s[0-9]*\)_[a-z]*_pred_.*.java/\1.java/'))
	    
	    bash $DIR/codeCompare.sh $model_input $m $codenet_java $WS
	    
	done
    done
done
