#!/usr/bin/python

# Created by Nikolay Popov
# on 7/26/2016
# This is a library of functions to update test case results using testrail REST API

# This is example of how to use update_testrail function to update test case
#msg="automation test"
#update_testrail(run_id="01", cid="001", result=1, msg=msg)

import sys, json

sys.path.append('/koka/libs')
from testrail import *

def get_testrail_client():
	# Tertrail URL, user and password
	testrail_url = "https://testrail.company.com/testrail/"
	client = APIClient(testrail_url)
	client.user = "user.name@email.com"
	client.password = "LOLPASSWORD" # I made this password up on purpuse so nobody will steal my real password
	return client

def update_case(client, case_id, run_id, status_id, msg=""):
	#Parameters for update_case is the combination of run id and case id and msg.
	#status_id is 1 for Passed, 2 For Blocked, 4 for Retest and 5 for Failed

	if run_id is not None:
		try:
			result = client.send_post("add_result_for_case/%s/%s" % (run_id,case_id),{"status_id": status_id, "comment": msg })
		except Exception, error:
			print "Exception in update_testrail() updating TestRail."
			print "ERROR: %s" % error
			return(1)
		else:
			print "Updated test result for case: %s in test run: %s" % (case_id,run_id)
			return(0)

def update_testrail(run_id, cid, result, msg):
	print "Authenticating with testrail server ..."
	client = get_testrail_client()
	print client

	print "Updating Test Case ..."
	status = update_case(case_id=cid, run_id=run_id, status_id=result, msg=msg, client=client)
