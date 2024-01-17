for f in $(cat $1); do
    p=$(basename $(dirname $(dirname $(dirname $f))))
    s=$(basename $f | sed 's/_[a-z]*_input//')

    python $f < $2/${p}/input.txt > /tmp/tempout1
    python $3/${p}/Python/${s}.py < $2/${p}/input.txt > /tmp/tempout2

    if diff /tmp/tmpout1 /tmp/tempout2; then
	echo $f works
    else
	echo $f differs
    fi
done
