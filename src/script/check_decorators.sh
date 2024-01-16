for f in $(cat $1); do
    p=$(dirname $(dirname $f))
    s=$(basename $f)

    input=$2/${p}/input.txt

    original=$3/${p}/Python/${s}.py

    removed=$4/${p}/Python/${s}_decorator_input.py

    echo $f $removed $input
done
