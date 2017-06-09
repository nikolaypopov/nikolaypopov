"""

This test will execute 2 different runs in loop for as times as set by user in config

1) First run will execute copy of selected file from one directory to a new directory and will perform failover on selected nedge service
2) Second run will execute copy of selected file while performing failover on selected nedge service in the middle of copying process

NOTE: During both runs, files will be compare after copy and failover, using diff to ensure there was no data loss or corruption

Written by Nikolay Popov

"""

import re, time, sys, json

from multiprocessing import Process
from functools import partial

sys.path.append('/root/nedge/lib/')
from ssh_client import SSHClient
from common import Output
from common import Timeout

# Getting config
json_data_file = open('../config/config.json', 'r')
cfg = json.load(json_data_file)

neadm_host = cfg['server']['host']
neadm_username = cfg['server']['username']
neadm_password = cfg['server']['password']
service_name = cfg['server']['service_name']

client_host = cfg['client']['host']
client_username = cfg['client']['username']
client_password = cfg['client']['password']
filename = cfg['client']['filename']
pathfrom = cfg['client']['pathfrom']
pathto = cfg['client']['pathto']
runtimes = cfg['client']['runtimes']

out = Output()

globalTimeOut = 600 # 10 minute global timeout for this whole script

def cleanup():
	# Connecting to MUT
	client = SSHClient(client_host, client_username, client_password)

        # Checking content of the destination folder
        print "Checking if cleanup is needed ..."
        rc, cout = client.run("ls -1 {}".format(pathto))

	if rc == None:
		out.colorPrint('ERROR: Unknown Error', 'r')
		exit(1)
	elif rc == 0:
		print 'Console output:\n%s' % cout
	else:
		out.colorPrint('ReturnCode: %s' % rc, 'r')
		out.colorPrint('Error: %s' % cout, 'r')
		exit(1)

        # If file exists we try to delete it
        if filename in cout:
                out.colorPrint('Found file you trying to copy, initiating cleanup ...', 'r')
                rc, cout = client.run('rm {}/{}'.format(pathto, filename))
                if rc != 0:
                        out.colorPrint('Cleanup has failed', 'r')
			out.colorPrint('ReturnCode: %s' % rc, 'r')
			out.colorPrint('Error: %s' % cout, 'r')
                        exit(1)
                out.colorPrint('Cleanup has finished successfully\n', 'g')
        else:
                out.colorPrint('Cleanup is not needed\n', 'g')

def parallel(func):
	def parallel_func(*args, **kw):
		p = Process(target=func, args=args, kwargs=kw)
		p.start()
	return parallel_func

def getSize(path):
	# Connecting to MUT
	client = SSHClient(client_host, client_username, client_password)

	rc, cout = client.run('ls -la {}/{}'.format(path, filename))
	text = re.split('\n', cout)

	if rc != 0:
		out.colorPrint('Failed to execute \"ls -la {}/{}\" command'.format(path, filename), 'r')
		out.colorPrint('ReturnCode: %s' % rc, 'r')
		out.colorPrint('Error: %s' % cout, 'r')
		exit(1)

	# Searching for size of file
	for line in text:
		match = re.search('\S+\s+1\s+\S+\s\S+\s(\d+)\s+\S+\s+\S+\s+\S+\s+{}/{}'.format(path, filename), line)
		if match:
			return match.group(1)
		else:
			print out.colorPrint('Couldn\'t match regex to find size of {}/{}'.format(path, filename), 'r')
			exit(1)

def failover():
	# Connecting to MUT
	client = SSHClient(neadm_host, neadm_username, neadm_password)

	# Show service to get information about preferred node and list of nodes that are in the service
	rc, cout = client.run('/neadm/neadm service show %s' % service_name)
	text = re.split('\n', cout)
	pref_node = ''
	nodes = []
	for line in text:
		print line
		if 'X-VIPS' in line: # Getting preferred node
			match = re.search('X-VIPS\s+\[\[\"(\S+)\"\W\{\S+', line)
			if match:
				pref_node = match.group(1)
			else:
				out.colorPrint('Couldn\'t match preferred node', 'r')
				exit(1)
		elif 'X-VIP-Nodes' in line: # Getting list of nodes
			match = re.search('X-VIP-Nodes\s+\[\"(\S+)\".\"(\S+)\"\]', line)
			if match:
				nodes = [match.group(1), match.group(2)]
			else:
				out.colorPrint('Couldn\'t match service nodes', 'r')
				exit(1)

	# If any of there are still 0 something is wrong
	if len(pref_node) == 0 or len(nodes) == 0:
		out.colorPrint('Couldn\'t get necessary information from service show', 'r')
		exit(1)

	#print len(pref_node), len(nodes)
	print 'Nodes in service: \"{}\", \"{}\"'.format(nodes[0], nodes[1])
	print 'Current preferred node is \"%s\"\n' % pref_node

	# Check if service has less then 2 nodes then do not perform failover
	if len(nodes) < 2:
		out.colorPrint('Unable to perform failover, because service has less then 2 nodes', 'r')	
		exit(1)

	# Figuring out which node to perform failover to
	failover_node = ''
	for node in nodes:
		if node != pref_node:
			failover_node = node

	copyFrom = getSize(pathfrom)
	r = 0
	print 'WAITING FOR FAILOVER: Comparing sizes of {}/{} and {}/{}'.format(pathfrom, filename, pathto, filename)
	while r == 0:
		time.sleep(3)
		copyTo = getSize(pathto)
		if int(copyTo) > int(copyFrom) / 2:
			out.colorPrint('WAITING FOR FAILOVER: At least half the file was copyed successfully, %s/%s\n' % (copyTo, copyFrom), 'g')
			r = 1
		else:
			print 'WAITING FOR FAILOVER: File is still copying ... %s/%s' % (copyTo, copyFrom)
			r = 0

	print 'Performing failover from \"{}\" to \"{}\"'.format(pref_node, failover_node)
	rc, cout = client.run('/neadm/neadm service vip config {} preferred {}'.format(service_name, failover_node))
	
	if rc == None:
		out.colorPrint('ERROR: Unknown Error', 'r')
		exit(1)
	elif rc == 0:
		print 'Console output:\n%s' % cout
	else:
		out.colorPrint('ReturnCode: %s' % rc, 'r')
		out.colorPrint('Error: %s' % cout, 'r')
		exit(1)

@parallel
def copy_file():
	# Connection to MUT
	client = SSHClient(client_host, client_username, client_password)

        # Copy file to directory
        print 'Copying {} to {} ...'.format(filename, pathto)
        rc, cout = client.run('cp {}/{} {}/.'.format(pathfrom, filename, pathto))

        # Check if the file is in the directory
        rc, cout = client.run('ls -lah {}'.format(pathto))

	if rc == None:
		out.colorPrint('ERROR: Unknown Error', 'r')
		exit(1)
	elif rc == 0:
		print 'Console output:\n%s' % cout
        else:
                out.colorPrint('ReturnCode: %s' % rc, 'r')
                out.colorPrint('Error: %s' % cout, 'r')
                exit(1)

def check_diff():
	# Connection to MUT
	client = SSHClient(client_host, client_username, client_password)

        # Checking diff
	print 'Checking diff between files {}/{} and {}/{}'.format(pathfrom, filename, pathto, filename)
        rc, cout = client.run('diff {}/{} {}/{}'.format(pathfrom, filename, pathto, filename))

	if rc == None:
		out.colorPrint('ERROR: Unknown Error', 'r')
		exit(1)
	elif rc == 0:
        	out.colorPrint('Diff success\n', 'g')
	else:
                out.colorPrint('Failed to match diffs', 'r')
		out.colorPrint('ReturnCode: %s' % rc, 'r')
		out.colorPrint('Error: %s' % cout, 'r')
                exit(1)

def delete_file():
	# Connection to MUT
	client = SSHClient(client_host, client_username, client_password)

        # Delete file from directory
        print 'Deleting {} from {} ...'.format(filename, pathto)
        rc, cout = client.run('rm {}/{}'.format(pathto, filename))

        # Check if the file was actually removed from the directory
        rc, cout = client.run('ls -1 {}'.format(pathto))

	if rc == None:
		exit(1)
	elif rc != 0:
                out.colorPrint('ReturnCode: %s' % rc, 'r')
                out.colorPrint('Error: %s' % cout, 'r')
                exit(1)
        print 'Console output:\n%s' % cout

        if filename not in cout:
                out.colorPrint('File was deleted successfully\n', 'g')
        else:
                out.colorPrint('Error: File was not deleted\n', 'r')
                exit(1)

def run1():
	timeout = 300 # 5 minute timeout for copy
	print ("Executing failover after copying file onto mounted iSCSI share and checking diff: %s times" % runtimes)
	copyFrom = getSize(pathfrom)
	copy_file()
	r = 2
	print 'WAITING TO FINISH COPY: Checking if file was fully copyed from %s to %s' % (pathfrom, pathto)
	try:
		with Timeout(timeout):
			while r == 2:
				time.sleep(3)
				copyTo = getSize(pathto)
				if copyTo == copyFrom:
					out.colorPrint('WAITING TO FINISH COPY: File is fully copyed, %s/%s\n' % (copyTo, copyFrom), 'g')
					r = 0
				else:
					print 'WAITING TO FINISH COPY: File is still copying ... %s/%s' % (copyTo, copyFrom)
					r = 2
	except Timeout.Timeout:
		out.colorPrint('ERROR: Timeout exeeded %s seconds' % timeout, 'r')
		# Connection to MUT
		client = SSHClient(client_host, client_username, client_password)

		# Search for cp process
		rc, cout = client.run('ps -ef | grep cp {}/{}'.format(pathto, filename))
		text = re.split('\n', cout)

		for line in text:
			print line
			if filename in line:
				out.colorPrint('ERROR: Copying file is taking too long', 'r')
				print line
				print 'Killing cp process ...'
				rc, cout = client.run('pkill cp')
				cleanup()
				exit(1)
			if filename not in line:
				out.colorPrint('ERROR: When timeout exeeded its limit, copy process was not found, it must have been interrupted for some reason', 'r')
				cleanup()
				exit(1)
			else:
				out.colorPrint('ERROR: Unknown Error', 'r')
				cleanup()
				exit(1)
	time.sleep(3)
	check_diff()
	failover()
	time.sleep(3)
	check_diff()
	delete_file()

def run2():
	timeout = 300 # 5 minute timeout for copy
	copyFrom = getSize(pathfrom)
	copy_file()
	failover()
	time.sleep(3)
	r = 2
	print 'WAITING TO FINISH COPY: Checking if file was fully copyed from %s to %s' % (pathfrom, pathto)
	try:
		with Timeout(timeout):
			while r == 2:
				time.sleep(3)
				copyTo = getSize(pathto)
				if copyTo == copyFrom:
					out.colorPrint('WAITING TO FINISH COPY: File is fully copyed, %s/%s\n' % (copyTo, copyFrom), 'g')
					r = 0
				else:
					print 'WAITING TO FINISH COPY: File is still copying ... %s/%s' % (copyTo, copyFrom)
					r = 2
	except Timeout.Timeout:
		out.colorPrint('ERROR: Timeout exeeded %s seconds' % timeout, 'r')
		# Connection to MUT
		client = SSHClient(client_host, client_username, client_password)

		# Delete file from directory
		rc, cout = client.run('ps -ef | grep cp {}/{}'.format(pathto, filename))
		text = re.split('\n', cout)

		for line in text:
			print line
			if filename in line:
				out.colorPrint('ERROR: Copying file is taking too long', 'r')
				print line
				print 'Killing cp process ...'
				rc, cout = client.run('pkill cp')
				cleanup()
				exit(1)
			if filename not in line:
				out.colorPrint('ERROR: When timeout exeeded its limit, copy process was not found, it must have been interrupted for some reason', 'r')
				cleanup()
				exit(1)
			else:
				out.colorPrint('ERROR: Unknown Error', 'r')
				cleanup()
				exit(1)
	time.sleep(3)
	check_diff()
	delete_file()

times = 0
print 'Executing this test %s times' % runtimes
while times < runtimes:
	try:
		with Timeout(globalTimeOut):
			cleanup()
			run1()
			print "Wait 5 seconds before continuing with second part of the test ...\n"
			time.sleep(5)
			cleanup()
			run2()
	except Timeout.Timeout:
		out.colorPrint('ERROR: Timeout exeeded %s seconds' % globalTimeOut, 'r')
	times += 1
