#!/bin/bash

PROG=$1

S=`echo $PROG | sed 's#.*/\(s[0-9]*\)/.*#\1#'`
P=`echo $PROG | sed 's#.*/\(p[0-9]*\)/.*#\1#'`

javac -d /tmp $PROG

java -cp /tmp ${P}.${S}.Main
