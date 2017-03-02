#!/usr/bin/python

import sys, requests, json, os, time

sys.path.append('/koka/libs')
from lib import *

sys.path.append('/koka/libs')
from updatetestrail import *

sys.path.append('/koka/config')
from config import *

myFileName = os.path.realpath(__file__) # Get this filename and path

findTestCase = findLine(tl = "{}".format(myFileName), suite = "/koka/suites/suite-hpr.py") # Find test case related to this file name and path
testCaseName = testName(tsn = "{}".format(findTestCase)) # Get test case name in suite
print "Test case name in suite: " + testCaseName

jenkinsJob = "TEST-HPR"
suiteName = "suite-hpr"

try:
	# Creating filesystem on a source host
	print "Create fs ..."
	payload = {"shareSmb":False,"shareNfs":False,"recordSize":131072,"compressionMode":"on","reservationSize":0,"quotaSize":0,"readWriteList":"*"}
	if createFS(vcip=vcIP, nsid=srcHostID, pool=srcPool, fs=srcFs, body=payload) == 1:
		exit(1)

	# Creating local replication service on source host
	print "Create Service ..."
	payload = {"name": svcName, "sourceDataset": srcDataset, "destinationDataset": destDataset, "type": "scheduled", "recursive": False, "schedules": [{"keepDestination": keepSS, "keepSource": keepSS, "cron": cron, "replicationDisabled": False, "scheduleName": schName, "disabled": False, "force": False}], "force": False, "scheduleName": svcName, "takeoverOrphanedSnapshots": False}
	taskID = createService(vcip=vcIP, nsid=srcHostID, sn=svcName, body=payload)
	print "Creation task ID: " + taskID

	# Checking creation task status
	if checkTask(vcip=vcIP, tid=taskID) == 1:
		update_testrail(run_id=TRrun_id, cid="312573", result=5, msg=jenkinsLastBuildNumber(tn = testCaseName, jj = jenkinsJob, sn = suiteName))
	update_testrail(run_id=TRrun_id, cid="312573", result=1, msg=jenkinsLastBuildNumber(tn = testCaseName, jj = jenkinsJob, sn = suiteName))

	# Wait 10 sec
	print "Sleeping for 5 seconds ..."
	time.sleep(5)

	# Checking if service is enabled on source host
	print "Check service status ..."
	listService(vcip=vcIP, nsid=srcHostID, sn=svcName)
	time.sleep(5)

	# Destroying service on source host
	print "Destroy service ..."
	if deleteService(vcip=vcIP, nsid=srcHostID, sn=svcName, body=payload) == 1:
		update_testrail(run_id=TRrun_id, cid="312570", result=5, msg=jenkinsLastBuildNumber(tn = testCaseName, jj = jenkinsJob, sn = suiteName))
	update_testrail(run_id=TRrun_id, cid="312570", result=1, msg=jenkinsLastBuildNumber(tn = testCaseName, jj = jenkinsJob, sn = suiteName))
	time.sleep(5)

	# Destroying filesystem on a destination host
	print "Destroy destination fs ..."
	destroyFS(vcip=vcIP, nsid=srcHostID, pool=srcPool, fs=destFs)
	time.sleep(5)

	# Destroying filesystem on a source host
	print "Destroy source fs ..."
	destroyFS(vcip=vcIP, nsid=srcHostID, pool=srcPool, fs=srcFs)
	time.sleep(5)
except requests.ConnectionError:
	print "Error: Failed execute API"
	exit(1)
