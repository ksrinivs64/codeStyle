#!/bin/bash

DIR=`dirname $0`

WS=`mktemp -d`

trap 'rm -rf $WS' EXIT

for gen in $1/*_output.py; do
    cp $gen $WS/Main.java
    javac -d $WS $WS/Main.java

    PROB=$(awk '/^package p/ { print gensub(/package (p[0-9]*)[.].*$/, "\\1", "g", $0); }' $gen)

    PKG=$(awk '/^package p/ { print gensub(/package (p[0-9]*[.].*);$/, "\\1", "g", $0); }' $gen)

    echo xxx $PROB $PKG
    
    java -cp $WS ${PKG}.Main < $2/${PROB}/input.txt

done
