#!/usr/bin/python

import requests, json, sys, time, datetime, re
#import paramiko

sys.path.append('/koka/config')
from config import *

def checkResponseStatus(response):
	if 200 == response.status_code:
		return 200
	else:
		return "Error: Unknown error"

def resultPrint(status):
	if 1 == status:
		print "*******************************************"
		print "FAILED"
		print "*******************************************"
	if 0 == status:
		print "*******************************************"
		print "SUCCESS"
		print "*******************************************"

def jenkinsLastBuildNumber(tn, jj, sn): # Takes test name, jenkins job name, suite name
	response = requests.get("http://10.3.199.15:8080/view/NSVP-QA/job/" + jj + "/lastBuild/buildNumber")
	print response

	jobData	= response.json()
	buildNumber = "{}".format(jobData)
	return "See results for the test here: http://10.3.199.15:8080/view/NSVP-QA/job/" + jj + "/" + buildNumber + "/testReport/" + sn + "/MyClass/" + tn

def findLine(tl, suite):
	with open(suite, "r") as f:
		searchlines = f.readlines()
	for i, line in enumerate(searchlines):
		if tl in line:
			myLine = searchlines[i-1] # Find line before testLine
			return myLine

def testName(tsn):
	myString = "{}".format(tsn)
	match = re.search('\w+\s(\w+).', myString)
	if match:
		return match.group(1)
	else:
		return "No Match"

def checkTask(vcip, tid):
	headers = {'content-type': 'application/json'}
	response = requests.get("https://" + vcip + "/vsphere-client/nsvp_client/rest/system/events", headers=headers, verify=False)
	if checkResponseStatus(response) == 200:
		jsonData = json.loads(response.text)
		i = 0
		while jsonData["result"][i]["eid"] != tid:
			i = i+1
		print "Waiting for task to finish",
		while jsonData["result"][i]["status"] == 2:
			headers = {'content-type': 'application/json'}
			response = requests.get("https://" + vcip + "/vsphere-client/nsvp_client/rest/system/events", headers=headers, verify=False)
			jsonData = json.loads(response.text)
			print ".",
		print " Done"
		if jsonData["result"][i]["status"] == 1:
			print "Task %s with eid %s has successfully finished" %(jsonData["result"][i]["name"],jsonData["result"][i]["eid"])
			return(0)
		elif jsonData["result"][i]["status"] == 10:
			print "Result: %s task with eid %s has failed" %(jsonData["result"][i]["name"],jsonData["result"][i]["eid"])
			if jsonData["result"][i]["errorMessage"]:
				print "Error: %s" % jsonData["result"][i]["errorMessage"]
			else:
				print "Explanation: No explanation came from NEF"
			return(1)
		else:
			print "???NEED TO DBG???"
			return(1)

def createFS(vcip, nsid, pool, fs, body):
	headers = {'content-type': 'application/json'}
	response = requests.post("https://" + vcip + "/vsphere-client/nsvp_client/rest/nstor/filesystem?hostId=" + nsid + "&pool=" + pool + "&filesystem=" + fs, headers=headers, data=json.dumps(body), verify=False)
	if checkResponseStatus(response) == 200:
		jsonData = json.loads(response.text)
		if jsonData["status"] == 1:
			if jsonData["error"]: # If error IS NOT null
				print "Test result: " + jsonData["error"]["message"]
				if jsonData["error"]["explanation"]: # If explanation IS NOT null
					print "Explanation: " + jsonData["error"]["explanation"]
				else:
					print "Explanation: No explanation came from NEF"
				return(1)
			else:
				print "Filesystem " + fs + " was successfully created"
				return(0)
		else:
			print "Test result: " + jsonData["error"]["message"]
			if jsonData["error"]["explanation"]: # If explanation IS NOT null
				print "Explanation: " + jsonData["error"]["explanation"]
			return(1)
	else:
		print response
		return(1)

def editFS(vcip, nsid, pool, fs, body):
	headers = {'content-type': 'application/json'}
	response = requests.put("https://" + vcip + "/vsphere-client/nsvp_client/rest/nstor/filesystem?hostId=" + nsid + "&pool=" + pool + "&filesystem=" + fs, headers=headers, data=json.dumps(body), verify=False)
	if checkResponseStatus(response) == 200:
		jsonData = json.loads(response.text)
		if jsonData["status"] == 1:
			if jsonData["error"]: # If error IS NOT null
				print "Test result: " + jsonData["error"]["message"]
				if jsonData["error"]["explanation"]: # If explanation IS NOT null
					print "Explanation: " + jsonData["error"]["explanation"]
				else:
					print "Explanation: No explanation came from NEF"
				return(1)
			else:
				print "Filesystem " + fs + " was successfully edited"
				return(0)
		else:
			print "Test result: " + jsonData["error"]["message"]
			if jsonData["error"]["explanation"]: # If explanation IS NOT null
				print "Explanation: " + jsonData["error"]["explanation"]
			return(1)
	else:
		print response
		return(1)

def destroyFS(vcip, nsid, pool, fs):
	headers = {'content-type': 'application/json'}
	response = requests.delete("https://" + vcip + "/vsphere-client/nsvp_client/rest/nstor/filesystem?hostId=" + nsid + "&pool=" + pool + "&filesystem=" + fs, headers=headers, verify=False)
	if checkResponseStatus(response) == 200:
		jsonData = json.loads(response.text)
		if jsonData["status"] == 1:
			if jsonData["error"]: # If error IS NOT null
				print "Test result: " + jsonData["error"]["message"]
				if jsonData["error"]["explanation"]: # If explanation IS NOT null
					print "Explanation: " + jsonData["error"]["explanation"]
				else:
					print "Explanation: No explanation came from NEF"
				return(1)
			else:
				print "Filesystem " + fs + " was successfully deleted"
				return(0)
			if jsonData["error"]:
				print "Test result: " + jsonData["error"]["message"]
				if jsonData["error"]["explanation"]: # If explanation IS NOT null
					print "Explanation: " + jsonData["error"]["explanation"]
					return(1)
			else:
				print "Filesystem " + fs + " was successfully deleted or doesn't exist"
				return(0)
	else:
		print response
		return(1)

def createVolume(vcip, nsid, pool, vol, body):
	headers = {'content-type': 'application/json'}
	response = requests.post("https://" + vcip + "/vsphere-client/nsvp_client/rest/nstor/volume?hostId=" + nsid + "&pool=" + pool + "&volume=" + vol, headers=headers, data=json.dumps(body), verify=False)
	if checkResponseStatus(response) == 200:
		jsonData = json.loads(response.text)
		if jsonData["status"] == 1:
			if jsonData["error"]: # If error IS NOT null
				print "Test result: " + jsonData["error"]["message"]
				if jsonData["error"]["explanation"]: # If explanation IS NOT null
					print "Explanation: " + jsonData["error"]["explanation"]
				else:
					print "Explanation: No explanation came from NEF"
				return(1)
			else:
				print "Test result: " + "Volume " + vol + " was successfully created and shared over iSCSI"
				return(0)
		else:
			print response
			print "Test result: " + jsonData["error"]["message"]
			if jsonData["error"]["explanation"]: # If explanation IS NOT null
				print "Explanation: " + jsonData["error"]["explanation"]
			return(1)
	else:
		print response
		return(1)

def editVolume(vcip, nsid, pool, vol, body):
	headers = {'content-type': 'application/json'}
	response = requests.put("https://" + vcip + "/vsphere-client/nsvp_client/rest/nstor/volume?hostId=" + nsid + "&pool=" + pool + "&volume=" + vol, headers=headers, data=json.dumps(body), verify=False)	
	if checkResponseStatus(response) == 200:
		jsonData = json.loads(response.text)
		return(jsonData["tid"])
	else:
		print response
		return(1)

def destroyVolume(vcip, nsid, pool, vol):
	headers = {'content-type': 'application/json'}
	response = requests.delete("https://" + vcip + "/vsphere-client/nsvp_client/rest/nstor/volume?hostId=" + nsid + "&pool=" + pool + "&volume=" + vol, headers=headers, verify=False)
	if checkResponseStatus(response) == 200:
		jsonData = json.loads(response.text)
		if jsonData["status"] == 1:
			if jsonData["error"]: # If error IS NOT null
				print "Test result: " + jsonData["error"]["message"]
				if jsonData["error"]["explanation"]: # If explanation IS NOT null
					print "Explanation: " + jsonData["error"]["explanation"]
				else:
					print "Explanation: No explanation came from NEF"
				return(1)
			else:
				print "Test result: " + "Volume " + vol + " was successfully deleted"
				return(0)
		else:
			if jsonData["error"]:
				print "Test result: " + jsonData["error"]["message"]
				if jsonData["error"]["explanation"]: # If explanation IS NOT null
					print "Explanation: " + jsonData["error"]["explanation"]
					return(1)
			else:
				print "Test result: Volume " + vol + " was successfully deleted or doesn't exist"
				return(0)
	else:
		print response
		return(1)

def createSnapshot(vcip, nsid, pool, fs, ds, sn):
	headers = {'content-type': 'application/json'}
	response = requests.post("https://" + vcip +"/vsphere-client/nsvp_client/rest/nstor/snapshot?hostId=" + nsid + "&pool=" + pool + "&dataset=" + ds + "&filesystem=" + fs + "&&snapshot=" + sn, headers=headers, verify=False)
	print response
	if checkResponseStatus(response) == 200:
		jsonData = json.loads(response.text)
		print jsonData
		if jsonData["status"] == 1:
			if jsonData["error"]: # If error IS NOT null
				print "Test result: " + jsonData["error"]["message"]
				if jsonData["error"]["explanation"]: # If explanation IS NOT null
					print "Explanation: " + jsonData["error"]["explanation"]
				else:
					print "Explanation: No explanation came from NEF"
				return(1)
			else:
				print "Test result: Snapshot " + snapshot + " was successfully created"
				return(0)
		else:
			print "Test result: " + jsonData["error"]["message"]
			if jsonData["error"]["explanation"]: # If explanation IS NOT null
				print "Explanation: " + jsonData["error"]["explanation"]
			return(1)
	else:
		print response
		return(1)

def deleteSnapshot(vcip, nsid, pool, fs, ds, sn):
	headers = {'content-type': 'application/json'}
	response = requests.delete("https://" + vcip +"/vsphere-client/nsvp_client/rest/nstor/snapshot?hostId=" + nsid + "&pool=" + pool + "&dataset=" + ds + "&filesystem=" + fs + "&&snapshot=" + sn, headers=headers, verify=False)
	print response
	if checkResponseStatus(response) == 200:
		jsonData = json.loads(response.text)
		print jsonData
		if jsonData["status"] == 1:
			if jsonData["error"]: # If error IS NOT null
				print "Test result: " + jsonData["error"]["message"]
				if jsonData["error"]["explanation"]: # If explanation IS NOT null
					print "Explanation: " + jsonData["error"]["explanation"]
				else:
					print "Explanation: No explanation came from NEF"
				return(1)
			else:
				print "Test result: Snapshot " + snapshot + " was successfully deleted"
				return(0)
		else:
			if jsonData["error"]:
				print "Test result: " + jsonData["error"]["message"]
				if jsonData["error"]["explanation"]: # If explanation IS NOT null
					print "Explanation: " + jsonData["error"]["explanation"]
					return(1)
			else: # Successfull deletion or existing or non existing fs always returns "status": 0 so it will always fall into this else
				print "Test result: Snapshot " + snapshot + " was successfully deleted or doesn't exist"
				return(0)
	else:
		print response
		return(1)

def createService(vcip, nsid, sn, body):
	headers = {'content-type': 'application/json'}
	response = requests.post("https://" + vcip + "/vsphere-client/nsvp_client/rest/nstor/hpr?hostId=" + nsid, data=json.dumps(body), headers=headers, verify=False)
	if checkResponseStatus(response) == 200:
		jsonData = json.loads(response.text)
		return(jsonData["tid"])
	else:
		print response
		return(1)

def listService(vcip, nsid, sn):
	response = requests.get("https://" + vcip + "/vsphere-client/nsvp_client/rest/nstor/hpr?hostId=" + nsid + "&service=" + sn, verify=False)
	if checkResponseStatus(response) == 200:
		jsonData = json.loads(response.text)
		if jsonData["status"] ==0:
			print "Error: " + jsonData["error"]["message"]
			print "Explanation: " + jsonData["error"]["explanation"]
			return(1)
		else:
			print "Service " + svcName + " is " + jsonData["result"]["state"]
			return(0)
	else:
		print response
		return(1)

def deleteService(vcip, nsid, sn, body):
	headers = {'content-type': 'application/json'}
	response = requests.delete("https://" + vcip + "/vsphere-client/nsvp_client/rest/nstor/hpr?hostId=" + nsid + "&service=" + sn, data=json.dumps(body), headers=headers, verify=False)
	if checkResponseStatus(response) == 200:
		jsonData = json.loads(response.text)
		print "Service " + svcName + " was successfully deleted"
		return(0)
	else:
		print response
		return(1)
