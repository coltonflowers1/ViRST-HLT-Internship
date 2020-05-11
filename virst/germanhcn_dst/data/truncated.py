import sys
import re

trunc = []
err = re.compile(r"[01]+S")

with open(sys.argv[1], "r") as infile:
	lines = infile.readlines()
	i = 0
	count = 0
	while i < len(lines):
		if lines[i] == "\n":
			i+=1
		elif re.search(err, lines[i]):
			while i < len(lines) and lines[i] != "\n" :
				i+=1
		else:
			count +=1
			i+=1
	txtLines = [line for line in lines if line != "\n"]
	
	print(count, len(txtLines), count/len(txtLines))

