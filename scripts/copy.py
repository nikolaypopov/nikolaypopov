#!/usr/bin/python

#from subprocess import *
from subprocess import Popen, PIPE, STDOUT

filename = "somefile"
pathfrom = "/path/from/"
pathto   = "/path/to/"
runtimes = 10

# Function to execute commands
def run(cmd):
	p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
	return p.communicate(), p.returncode

# Function to print success = green, fail = red
def colorPrint(text, color):
	if color == "g": # Green print
		print(("\033[1;32;40m{}\033[0;37;40m").format(text))
	if color == "r": # Red print
		print(("\033[1;31;40m{}\033[0;37;40m").format(text))

def cleanup():
	# Checking content of the destination folder
	print "Checking if cleanup is needed ..."
	ls,_ = run("ls -1 {}".format(pathto))

	deletels = []
	for line in ls:
		if line is not None:
			deletels += line.split("\n")
			break

	# If file exists we try to delete it
	if filename in deletels:
		colorPrint("Found file you trying to copy, initiating cleanup ...", "r")
		deletefile,returncode = run("rm {}{}".format(pathto, filename))
		if returncode == 0:
			colorPrint("Cleanup has finished successfully", "g")
		else:
			colorPrint("Cleanup has failed", "r")
			exit(1)
	else:
		colorPrint("Cleanup is not needed", "g")

def execute():
	# Copy file to directory
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
		colorPrint("ERR: File was not copyed", "r")
		exit(1)

	# Checking diff
	checkdiff,returncode = run("diff {}{} {}{}".format(pathfrom, filename, pathto, filename))
	if returncode == 0:
		colorPrint("Diff success", "g")
	else:	
		colorPrint("ERR: Diff fail", "r")
		exit(1)
	
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

	if filename not in deletels:
		colorPrint("File was deleted successfully", "g")
	else:
		colorPrint("ERR: File was not deleted", "r")
		exit(1)

cleanup()
print ("Executing copy/delete {} times".format(runtimes))
times = 0
while times < runtimes:
	execute()
	times += 1
