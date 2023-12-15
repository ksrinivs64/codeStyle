#!/bin/bash

no_unexpected_removed=0
no_unexpected_added=0
removed_correctly=0
added_correctly=0

ME=$0
DIR=`dirname $ME`

WS=$4
mkdir -p $WS

if [[ $1 =~ \.py$ ]]; then
    python $DIR/../normalize.py $1 > $WS/input 2>/dev/null
    python $DIR/../normalize.py $2 > $WS/output 2>/dev/null
    python $DIR/../normalize.py $3 > $WS/expected 2>/dev/null
else
    cp $1 $WS/input
    cp $2 $WS/output
    cp $3 $WS/expected
fi

if diff $WS/input $WS/expected; then
    echo $1 "nothing to do"
else
    python $DIR/../python/ndiff.py ${WS}/input ${WS}/expected | egrep '^ -' | sort > ${WS}/expected_removals.txt
    
    python $DIR/../python/ndiff.py ${WS}/input ${WS}/output | egrep '^ -' | sort > ${WS}/actual_removals.txt
    
    comm -23 ${WS}/expected_removals.txt ${WS}/actual_removals.txt > ${WS}/removal_diff
    
    if [[ -e ${WS}/removal_diff && ! -s ${WS}/removal_diff ]]; then
    removed_correctly=1
    fi
    
    comm -13 ${WS}/expected_removals.txt ${WS}/actual_removals.txt > ${WS}/removal_diff_2
    
    if [[ -e ${WS}/removal_diff_2 && ! -s ${WS}/removal_diff_2 ]]; then
    no_unexpected_removed=1
    fi
    
    python $DIR/../python/ndiff.py ${WS}/input ${WS}/expected | egrep '^ \+' | sort > ${WS}/expected_additions.txt
    
    python $DIR/../python/ndiff.py ${WS}/input ${WS}/output | egrep '^ \+' | sort > ${WS}/actual_additions.txt
    
    comm -23 ${WS}/expected_additions.txt ${WS}/actual_additions.txt > ${WS}/addition_diff

    if [[ -e ${WS}/addition_diff && ! -s ${WS}/addition_diff ]]; then
	added_correctly=1
    fi
    
    comm -13 ${WS}/expected_additions.txt ${WS}/actual_additions.txt > ${WS}/addition_diff
    
    if [[ -e ${WS}/addition_diff && ! -s ${WS}/addition_diff ]]; then
	no_unexpected_added=1
    fi

    echo $1 $added_correctly $removed_correctly $no_unexpected_removed $no_unexpected_added
fi
