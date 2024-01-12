#!/bin/bash

WS=`mktemp -d`
mkdir $WS
trap 'rm -rf $WS' EXIT

first=1
while IFS= read -r line
do
    words=$(echo $line | tr "," "\n")
    if test $first == 1; then
	i=1
	first=0
	for key in $words; do
	    if test $key == "orig"; then
		ORIG=$i
	    elif test $key == "transform"; then
		XFM=$i
	    fi
	    i=`expr $i + 1`
	done
    else
	expected=$(echo $line | cut -d "," -f $ORIG)
	xfm=$(echo $line | cut -d "," -f $XFM)

	s=`dirname $expected`
	p=`dirname $s`
	s=`basename $s`
	p=`basename $p`
	input="$2/$p/$s/Main.java"

	cp $xfm ${WS}/Main.java
	if javac -d $WS $WS/Main.java 2>$WS/${s}.err; then
	    echo $s passed
	else
	    echo $s failed
	fi
    fi	
done < $1
