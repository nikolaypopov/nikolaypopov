#!/usr/bin/python

import sys, requests, json, os

sys.path.append('/koka/libs')
from lib import *

sys.path.append('/koka/libs')
from updatetestrail import *

sys.path.append('/koka/config')
from config import *

print "*******************************************"
print "Test description: Create and delete Local Replication Service on top of iSCSI volume"
print "Sending API request to VC " + vcIP
print "*******************************************"

myFileName = os.path.realpath(__file__) # Get this filename and path

findTestCase = findLine(tl = "{}".format(myFileName), suite = "/koka/suites/suite-hpr.py") # Find test case related to this file name and path
testCaseName = testName(tsn = "{}".format(findTestCase)) # Get test case name in suite
print "Test case name in suite: " + testCaseName

jenkinsJob = "TEST-HPR"
suiteName = "suite-hpr"

try:
	# Create volume
	print "Create iSCSI volume ..."
	payload = {"compressionMode":"on","recordSize":131072,"reservationSize":0,"volumeSize":2147483648,"targetGroup":"","share":True}
	if createVolume(vcip=vcIP, nsid=srcHostID, pool=srcPool, vol=srcVolName, body=payload) == 1:
		exit(1)

	# Creating service
	print "Create Service ..."
	payload = {"name": svcName, "sourceDataset": srcVolume, "destinationDataset": destVolume, "type": "scheduled", "recursive": False, "schedules": [{"keepDestination": keepSS, "keepSource": keepSS, "cron": cron, "replicationDisabled": False, "scheduleName": schName, "disabled": False, "force": False}], "force": False, "scheduleName": svcName, "takeoverOrphanedSnapshots": False}
	taskID = createService(vcip=vcIP, nsid=srcHostID, sn=svcName, body=payload)
	print "Task ID is " + taskID

	# Checking creation task status
	if checkTask(vcip=vcIP, tid=taskID) == 1:
		update_testrail(run_id=TRrun_id, cid="312575", result=5, msg=jenkinsLastBuildNumber(tn = testCaseName, jj = jenkinsJob, sn = suiteName))
		resultPrint(1)
		exit(1)
	update_testrail(run_id=TRrun_id, cid="312575", result=1, msg=jenkinsLastBuildNumber(tn = testCaseName, jj = jenkinsJob, sn = suiteName))
	resultPrint(0)

	# Wait 5 sec
	print "Sleeping for 5 seconds ..."
	time.sleep(5)

	# Checking if service is enabled
	print "Check service status ..."
	listService(vcip=vcIP, nsid=srcHostID, sn=svcName)

	# Destroying service
	print "Destroy service ..."
	if deleteService(vcip=vcIP, nsid=srcHostID, sn=svcName, body=payload) == 1:
		update_testrail(run_id=TRrun_id, cid="312575", result=5, msg=jenkinsLastBuildNumber(tn = testCaseName, jj = jenkinsJob, sn = suiteName))
		resultPrint(1)
		exit(1)
	update_testrail(run_id=TRrun_id, cid="312575", result=1, msg=jenkinsLastBuildNumber(tn = testCaseName, jj = jenkinsJob, sn = suiteName))
	resultPrint(0)

	# Destroying volume
	print "Destroy destination volume ..."
	destroyVolume(vcip=vcIP, nsid=srcHostID, pool=srcPool, vol=destVolName) == 1

	# Destroy volume
	print "Destroy source volume"
	destroyVolume(vcip=vcIP, nsid=srcHostID, pool=srcPool, vol=srcVolName) == 1
except requests.ConnectionError:
	print "Error: Failed execute API"
	exit(1)
