@load "filefuncs"

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
	    c = gensub(/^"?([^"]*)"?$/, "\\1", "", contents[j])
            columnNames[c] = j
	}

    } else {
        name = gensub(/.*\/([^/]*)[.][a-z]*"?$/, "\\1", "g", contents[columnNames["orig"]])

        dir = gensub(/^.*\/(p[0-9]*)\/.*$/, "\\1", "g", contents[columnNames["orig"]])
	inpt = InputDir "/" dir "/input.txt"

	transformed_prog = contents[columnNames[TestCol]]
	if (stat(transformed_prog, garbage) != 0) {
	    next
	}
	transformed_status = system("bash ulimitit.sh 10 " RunIt " " transformed_prog " < " inpt " > " OutDir "/transformed_" dir "_" name " 2> " OutDir "/transformed_" dir "_" name ".err")

	original_prog = contents[columnNames["orig"]]
	original_status = system("bash ulimitit.sh 10 " RunIt " " original_prog " < " inpt " > " OutDir "/original_" dir "_" name " 2> " OutDir "/original_" dir "_" name ".err")

	if (transformed_status == 0 && original_status == 0) {
	    purported_output = InputDir "/" dir "/output.txt"

	    transform_check = system("diff --ignore-space-change " OutDir "/transformed_" dir "_" name " " OutDir "/original_" dir "_" name)
	    if (transform_check == 0) {
		print dir "_" name " has identical output"
	    } else {
		print dir "_" name " has different output"
	    }

	    purported_check = system("diff --ignore-space-change " OutDir "/transformed_" dir "_" name " " purported_output)
	    if (purported_check != 0) {
		print dir "_" name " has different purported output"
	    }

	    if (transform_check == 0) {
		system("rm " OutDir "/original_" dir "_" name)
		system("rm " OutDir "/original_" dir "_" name ".err")
		system("rm " OutDir "/transformed_" dir "_" name)
		system("rm " OutDir "/transformed_" dir "_" name ".err")
	    }
	    
	} else {
	    if (original_status != 0) {
		print "original " dir "_" name " failed to run"
	    }
	    if (transformed_status != 0) {
		print "transformed " dir "_" name " failed to run"
	    }
	}
    }
}
