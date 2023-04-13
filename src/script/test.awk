BEGIN {
    delete columnNames
}

function nextWord(str, start) {
    s = substr(str, start)
    if ("\"" == substr(s, 1, 1)) {
	n = match(s, /"\s*$|",/)
	return substr(s, 1, n) 
    } else {
	n = match(s, /\s*$|,/)
	return substr(s, 1, n-RLENGTH)
    }
}

{
    delete contents
    
    i=1
    elt = 1
    while (i < length($0)-1) {
	s = nextWord($0, i)
	contents[elt++] = s
	i += length(s) + 1
    }

    if (FNR == 1) {
	for(j = 1; j < elt; j++) {
	    columnNames[contents[j]] = j
	}

    } else {
	name = gensub(/.*\/(.*)[.]py/, "\\1", "g", contents[columnNames["Filename"]])

	dir = gensub(/\/.*[.]py/, "", "g", contents[columnNames["Filename"]])
	inpt = InputDir "/" dir "/input.txt"

	prog = contents[columnNames[TestCol]]
	prog = gensub(/'/, "\"", "g", gensub(/^"/, "", "g", gensub(/"$/, "", "g", prog)))
	
	status = system("bash ulimitit.sh 10 python -c $'" prog "' < " inpt " > " OutDir "/" name " 2> " OutDir "/" name ".err")

	if (status == 0) {
	    outpt = InputDir "/" dir "/output.txt"

	    check = system("diff " OutDir "/" name " " outpt)

	    if (check == 0) {
		print name " has identical output"
	    } else {
		print name " has different output"
	    }
	} else {
	    print name " failed to run"
	}
    }
}
