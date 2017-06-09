"""

This script will perform the following:

1) Cleanup already existing test environment
2) Create nedge iSCSI HA service on nedge server
3) Discover and mount iSCSI LUN on ubuntu client

Written by Nikolay Popov

"""

import os, re, time, sys, json
from multiprocessing import Process
from functools import partial

pathtofile = os.path.dirname(__file__) # Absolute path to where my script is

sys.path.append(os.path.join(pathtofile, '../lib/'))
from ssh_client import SSHClient
from common import Output
from common import Timeout

# Getting config
json_data_file = open(os.path.join(pathtofile, '../config/config.json'), 'r')
cfg = json.load(json_data_file)

neadm_host = cfg['server']['host']
neadm_username = cfg['server']['username']
neadm_password = cfg['server']['password']
service_name = cfg['server']['service_name']
nedge_quorum = cfg['server']['quorumnode']
nedge_node1 = cfg['server']['node1']
nedge_node2 = cfg['server']['node2']
nedge_vip = cfg['server']['vip']
client_net_name = cfg['server']['client_net']
client_net_ip1 = cfg['server']['client_net_ip1']
client_net_ip2 = cfg['server']['client_net_ip2']

cluster_name = cfg['server']['cluster']
tenant_name = cfg['server']['tenant']
bucket_name = cfg['server']['bucket']
lun_name = cfg['server']['lun_name']
lun_size = cfg['server']['lun_size']

client_host = cfg['client']['host']
client_username = cfg['client']['username']
client_password = cfg['client']['password']
filename = cfg['client']['filename']
pathfrom = cfg['client']['pathfrom']
pathto = cfg['client']['pathto']
runtimes = cfg['client']['runtimes']

out = Output()

def cleanup_ctb():
	client = SSHClient(neadm_host, neadm_username, neadm_password)

	print 'Checking if cleanup cluster is needed ...'

	rc, cout = client.run('/neadm/neadm cluster list')
	if cluster_name in cout:
		out.colorPrint('Found cluster, preparing to cleanup', 'r')

		rc, cout = client.run('/neadm/neadm bucket delete {}/{}/{}'.format(cluster_name, tenant_name, bucket_name))
		print cout

		rc, cout = client.run('/neadm/neadm tenant delete {}/{}'.format(cluster_name, tenant_name))
		print cout

		rc, cout = client.run('/neadm/neadm cluster delete {}'.format(cluster_name))
		print cout
	else:
		out.colorPrint('Cleanup cluster is not needed\n', 'g')

def cleanup_service():
	client = SSHClient(neadm_host, neadm_username, neadm_password)

	print 'Checking if cleanup service is needed ...'

	rc, cout = client.run('/neadm/neadm service show %s' % service_name)
	if rc == 0:
		out.colorPrint('Found service, preparing to cleanup ...\n', 'r')

		rc, cout = client.run('/neadm/neadm iscsi delete {} {}/{}/{}/{}'.format(service_name, cluster_name, tenant_name, bucket_name, lun_name))
		print cout

		rc, cout = client.run('/neadm/neadm service disable %s' % service_name)
		print cout

		rc, cout = client.run('/neadm/neadm service vip delete {} {}/24'.format(service_name, nedge_vip))
		print cout

		rc, cout = client.run('/neadm/neadm service delete %s' % service_name)
		print cout

		out.colorPrint('Cleanup has finished successfully\n', 'g')
	else:
		out.colorPrint('Cleanup service is not needed\n', 'g')

def cleanup_client():
	client = SSHClient(client_host, client_username, client_password)
	cl = 'yes'

	print 'Checking if cleanup client is needed ...'

	rc, cout = client.run('mount')
	text = re.split('\n', cout)
	for line in text:
		if pathto in line:
			print line
			match = re.search('(\S+)\s+on\s+({})\s+\w+\s+\w+\s+\S+'.format(pathto), line)
			if match:
				out.colorPrint('Found LUN \"{}\" mounted onto test filesystem \"{}\", cleanup is needed'.format(match.group(1), match.group(2)), 'r')
				rc, cout = client.run('umount %s' % pathto)
				print cout

				rc, cout = client.run('rm -r %s' % pathto)
				print cout

			        rc, cout = client.run('iscsiadm -m node')
			        print cout
			        text = re.split('\n', cout)
				portal = ''
				targetname = ''
			        for line in text:
					if nedge_vip in line:
						match = re.search('({}:\d+),\S+\s+(\S+)'.format(nedge_vip), line)
			                        if match:
							portal = match.group(1)
							targetname = match.group(2)
						else:
							print 'Couldn\'t match'
							exit(1)

				print 'Portal: %s' % portal
				print 'IQN: %s' % targetname

				rc, cout = client.run('iscsiadm -m node --targetname {} --portal {} --logout'.format(targetname, portal))
				print cout

				rc, cout = client.run('iscsiadm -m node -o delete --targetname {} --portal {}'.format(targetname, portal))
				print cout

				cl = 'no'
			else:
				out.colorPrint('Couldn\'t match mounted filesystem name', 'r')
				exit(1)
	if cl == 'yes':
		out.colorPrint('Cleanup client is not needed\n', 'g')


def create_ctb():
	# Connecting to MUT
	client = SSHClient(neadm_host, neadm_username, neadm_password)

	# Show service to get information about preferred node and list of nodes that are in the service
	rc, cout = client.run('/neadm/neadm cluster create {}'.format(cluster_name))
        if rc != 0:
                print cout
                out.colorPrint('Failed to create cluster {}'.format(cluster_name), 'r')
                exit(1)
        print cout

	time.sleep(2)

	rc, cout = client.run('/neadm/neadm tenant create {}/{}'.format(cluster_name, tenant_name))
        if rc != 0:
                print cout
                out.colorPrint('Failed to create tenant {}/{}'.format(cluster_name, tenant_name), 'r')
                exit(1)
        print cout

	time.sleep(2)

	rc, cout = client.run('/neadm/neadm bucket create {}/{}/{}'.format(cluster_name, tenant_name, bucket_name))
        if rc != 0:
                print cout
                out.colorPrint('Failed to create bucket {}/{}/{}'.format(cluster_name, tenant_name, bucket_name), 'r')
                exit(1)
        print cout

def create_service():
	client = SSHClient(neadm_host, neadm_username, neadm_password)

	rc, cout = client.run('/neadm/neadm service create iscsi %s' % service_name)
	print cout

	rc, cout = client.run('/neadm/neadm service add {} {}'.format(service_name, nedge_node1))
	print cout

	rc, cout = client.run('/neadm/neadm service add {} {}'.format(service_name, nedge_node2))
	print cout

	rc, cout = client.run('/neadm/neadm service vip add {} {} {}/24 -p {}'.format(service_name, nedge_quorum, nedge_vip, nedge_node1))
	print cout

	rc, cout = client.run('/neadm/neadm service show %s' % service_name)
	print cout
	text = re.split('\n', cout)
	nodeid = []
	for line in text:
		if 'X-Servers' in line:
			match = re.search('X-Servers\s+(\w+)\D(\w+)', line)
			if match:
				nodeid = [match.group(1), match.group(2)]
			else:
				out.colorPrint('Couldn\'t match service nodes IDs', 'r')
				exit(1)

	if len(nodeid) != 2:
		out.colorPrint('Not enough nodes in the service, should be 2', 'r')
		exit(1)

	print 'Node IDs: {}, {}'.format(nodeid[0], nodeid[1])

	rc, cout = client.run('/neadm/neadm service configure {} X-Container-Network-{} \"{} --ip {}\"'.format(service_name, nodeid[0], client_net_name, client_net_ip1))
	print cout

	rc, cout = client.run('/neadm/neadm service configure {} X-Container-Network-{} \"{} --ip {}\"'.format(service_name, nodeid[1], client_net_name, client_net_ip2))
	print cout

	rc, cout = client.run('/neadm/neadm service enable %s' % service_name)
	if rc != 0:
		print cout
		out.colorPrint('Error: unable to enable service: %s' % service_name, 'r')
		exit(1)
	print cout

	rc, cout = client.run('/neadm/neadm iscsi create {} {}/{}/{}/{} {}{}'.format(service_name, cluster_name, tenant_name, bucket_name, lun_name, lun_size[0], lun_size[1]))
	if rc != 0:
		print cout
		out.colorPrint('Error: unable to create LUN {}/{}/{}/{} with the size {}{}'.format(cluster_name, tenant_name, bucket_name, lun_name, lun_size[0], lun_size[1]), 'r')
		exit(1)
	print cout

def mount_iscsi_lun():
	client = SSHClient(client_host, client_username, client_password)

	rc, cout = client.run('iscsiadm -m discovery -t sendtargets -p %s' % nedge_vip)
	if rc != 0:
		print cout
		out.colorPrint('Error: unable to find iSCSI target via IP: %s' % nedge_vip, 'r')
		exit(1)
	out.colorPrint('Successfully discovered target via %s\n' % nedge_vip, 'g')

	text = re.split('\n', cout)
	portal = ''
	targetname = ''
	for line in text:
		if nedge_vip in line:
			match = re.search('({}:\d+),\S+\s+(\S+)'.format(nedge_vip), line)
			if match:
				portal = match.group(1)
				targetname = match.group(2)
			else:
				print 'Couldn\'t match'
				exit(1)

	print 'Portal: %s' % portal
	print 'IQN: %s' % targetname

	rc, cout = client.run('iscsiadm -m node --targetname {} --portal {} --login'.format(targetname, portal))
	if rc != 0:
		out.colorPrint(cout, 'r')
		out.colorPrint('Error: Couldnot login to iSCSI target', 'r')
		exit(1)
	out.colorPrint(cout, 'g')

	rc, cout = client.run('fdisk -l | grep sd')
	print cout
	text = re.split('\n', cout)
	diskname = ''
	for line in text:
		if lun_size[0] in line:
			print line
			match = re.search('Disk\s(\W\w+\W\w+):\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+', line)
			if match:
				diskname = match.group(1)
			else:
				print 'Couldn\'t match'
				exit(1)

	out.colorPrint('Found iSCSI LUN, disk name is %s\n' % diskname, 'g')

	rc, cout = client.run('mkfs.ext4 %s' % diskname)
	if rc != 0:
		print cout
		out.colorPrint('Couldn\'t create filesystem on iSCSI LUN %s' % diskname, 'r')
		exit(1)
	print cout
	out.colorPrint('Filesystem was successfully create on top of %s' % diskname,'g')

	rc, cout = client.run('mkdir %s' % pathto)
	if rc != 0:
		out.colorPrint('Error: %s' % cout, 'r')
		out.colorPrint('Couldn\'t create directory %s' % pathto, 'r')
		exit(1)
	print cout
	out.colorPrint('{} was successfully created\n'.format(pathto), 'g')

	rc, cout = client.run('mount {} {}'.format(diskname, pathto))
	print cout
	if rc != 0:
		out.colorPrint('Error: %s' % cout,'r')
		out.colorPrint('Error: Unable to mount {} to {}'.format(diskname, pathto),'r')
		exit(1)
	print cout
	out.colorPrint('{} was successfully mounted to {}'.format(diskname, pathto),'g')

cleanup_client()
cleanup_service()
cleanup_ctb()

create_ctb()
create_service()
mount_iscsi_lun()
