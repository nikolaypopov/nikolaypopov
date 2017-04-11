#!/usr/bin/python

#from subprocess import *
from subprocess import Popen, PIPE, STDOUT

filename = "somefile.txt"
pathfrom = "/root/"
pathto   = "/root/test/"
runtimes = 5

# Function to execute commands
def run(cmd):
	p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
	#output = p.communicate()
	return p.communicate(), p.returncode

# Function to print success = green, fail = red
def colorPrint(text, color):
	if color == "g": # Green print
		print(("\033[1;32;40m{}\033[0;37;40m").format(text))
	if color == "r": # Red print
		print(("\033[1;31;40m{}\033[0;37;40m").format(text))

def execute():
	# Copy file to directory
	#print "Copying ", filename, " to " + pathto + " ..."
	print "Copying {} to {} ...".format(filename, pathto)
	copyfile,_ = run("cp {}{} {}.".format(pathfrom, filename, pathto))

	# Check if the file is in the directory
	ls,_ = run("ls -1 {}".format(pathto))

	copyls = []
	for line in ls:
		if line is not None:
			copyls += line.split("\n")
			break

	# Printing content of ls -l without printing last element
	print "Content {}".format(copyls[:-1])

	if filename in copyls:
		colorPrint("File was copyed successfully", "g")
	else:
		colorPrint("File was not copyed", "r")
		exit(1)

	# Checking diff
	checkdiff,returncode = run("diff {}{} {}{}".format(pathfrom, filename, pathto, filename))
	if returncode == 0:
		colorPrint("Diff success", "g")
	else:	
		colorPrint("Diff fail", "r")
	
	# Delete file from directory
	print "Deleting {} from {} ...".format(filename, pathto)
	deletefile,_ = run("rm {}{}".format(pathto, filename))

	# Check if the file was removed from the directory
	ls,_ = run("ls -1 {}".format(pathto))

	deletels = []
	for line in ls:
		if line is not None:
			deletels += line.split("\n")
			break

	# Printing content of ls -l without printing last element
	print "Content {}".format(deletels[:-1])

	if filename in deletels:
		colorPrint("File was not deleted", "r")
	else:
		colorPrint("File was deleted successfully", "g")

print ("Executing copy/delete {} times".format(runtimes))
times = 0
while times < runtimes:
	execute()
	times += 1
