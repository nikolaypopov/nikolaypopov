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
cluster_name = cfg['server']['cluster']
tenant_name = cfg['server']['tenant']
bucket_name = cfg['server']['bucket']
lun_name = cfg['server']['lun_name']
lun_size = cfg['server']['lun_size']
log_file = cfg['server']['log']

max_run times = cfg['client']['runtimes']
max_fail_times = cfg['client']['failtimes']

out = Output()

def create_delete_lun_overnight():
	client = SSHClient(neadm_host, neadm_username, neadm_password)

	fail = 0
	times = 0

	print 'Executing this test %s times' % max_run_times
	while (times < max_run_times) & (fail < max_fail_times):
		my_time = time.strftime("%Y-%m-%d %H:%M:%S")
		times += 1
		print 'Running time: %s' % times
		rc, cout = client.run('/neadm/neadm iscsi create {} {}/{}/{}/{}{} {}{}'.format(service_name, cluster_name, tenant_name, bucket_name, lun_name, times, lun_size[0], lun_size[1]))
		if rc != 0:
			print cout
			out.colorPrint('Error: Failed to create LUN {}/{}/{}/{}{} with the size {}{}'.format(cluster_name, tenant_name, bucket_name, lun_name, times, lun_size[0], lun_size[1]), 'r')
			error = '{} CE-{}: {}'.format(my_time, times, cout)
			with open(log_file, 'a') as text_file: # Write errors into log file
				text_file.write('{}'.format(error))
		print cout

		rc, cout = client.run('/neadm/neadm iscsi delete {} {}/{}/{}/{}{}'.format(service_name, cluster_name, tenant_name, bucket_name, lun_name, times))
		if rc != 0:
			print cout
			out.colorPrint('Error: Failed to delete LUN {}/{}/{}/{}{}'.format(cluster_name, tenant_name, bucket_name, lun_name, times), 'r')
                        error = '{} DE-{}: {}'.format(my_time, times, cout)
                        with open(log_file, 'a') as text_file: # Write errors into log file
                                text_file.write('{}'.format(error))
			fail += 1
			print 'Failed to delete {}/{} times'.format(fail, max_fail_times)
		print cout

create_delete_lun_overnight()
