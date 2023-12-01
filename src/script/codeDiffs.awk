BEGIN {
    delete altered_lines;
}

/^[0-9]*[adc][0-9]*(,[0-9]*)?$/ {
    n = split($0, a, /[adc,]/)
    altered_lines[a[1]] = 1	
}

/^[0-9]*(,[0-9]*)[adc][0-9]*(,[0-9]*)?$/ {
    n = split($0, a, /[adc,]/)
    for(i = a[1]; i <= a[2]; i++) {
	altered_lines[i] = 1
    }
}

END {
    for(i in altered_lines) {
	print i
    }
}
