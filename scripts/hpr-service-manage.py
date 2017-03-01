#!/usr/bin/python

import requests, json, time, getopt, sys
import urllib.request, urllib.parse, urllib.error
import subprocess

# Supress InsecureRequestWarning: Unverified HTTPS request is being made in python3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def printHelp():
	print("Usage: ./script.py [-c (create)or -d (destroy)] and [snapshots, local, remote]")
	print("Example: ./script.py -c remote (this will create remote replication service(s))")
	print("Make sure you specified (Must edit) parameters in the begining of this script!")
	sys.exit(1)

def colorPrint(text, color):
	if color == "g": # Green print
		print(("\033[1;32;40m" + text + "\033[0;37;40m"))
	if color == "r": # Red print
		print(("\033[1;31;40m" + text + "\033[0;37;40m"))

def install(package):
	proc = subprocess.Popen("apt-get install -y " + package, shell=True, stdin=None, stderr=None, executable="/bin/bash")
	proc.wait()

def isModuleExist(module, moduleName):
	print("Checking the system for necessary python module(s) that are required to run this script ...")
	try:
		__import__(module)
		print("Module " + module + " is installed")
	except ImportError:
		print("Module " + module + " is not installed")
		result = yesno(name=module)
		if result == 0:
			print("Installing package "  + moduleName + " ...")
			install(package=moduleName)
		elif result == 1:
			print("Not installing package " + moduleName)
			colorPrint(text="Exiting script due to specified module " + module + " is not installed", color="r")
			sys.exit(1)

def yesno(name):
	while True:
		r = input("Would you like to install " + name + "? y/n: ")
		if r == "y":
			return 0
			return False
		elif r == "n":
			return 1
			return False
		else:
			print(('Your choice was "{}". Please use input value "y" or "n" ...'.format(r)))

# Checking if necessary python modules are installed to run this script
isModuleExist(module="requests", moduleName="python-requests")

def main(argv):
#**********************************************************************************
#******************* TODO MUST EDIT THIS TODO *************************************
#**********************************************************************************
	user = "username" # Must edit according to you environment
	password = "userpassword" # Must edit according to you environment
	sourceHost = "10.3.199.193" # Must edit according to you environment
	remoteHost = "10.3.199.194" # Must edit according to you environment
	sourceUrl = "https://" + sourceHost + ":8443"
	remoteUrl = "https://" + remoteHost + ":8443"
	svcType = "scheduled"
	howOften = "*/5 * * * *" # Scheduled to take snapshot every 5 minutes
	keepSS = 5 # How many snapshts are kept on both source and destination sides
	svcName = "test-"
	srcPool = "pool1" # Must edit according to you environment
	destPool = "pool1" # Must edit according to you environment
	srcDataset =  srcPool + "/test-src"
	destDataset = destPool + "/test-dest"
	runTimes = 1 # How many services will be created
	schName = "test-schedule-"
	token = ""
#**********************************************************************************
#******************* TODO MUST EDIT THIS TODO *************************************
#**********************************************************************************
	def checkStatus(response, tk, ip):
		print("Checking response code ...")
		if 200 == response.status_code:
			print("Response code: %s" % response.status_code)
			colorPrint(text="Success", color="g")
		elif 201 == response.status_code:
			print("Response code: %s" % response.status_code)
			colorPrint(text="Success", color="g")
		elif 202 == response.status_code: # 202 is in-progress response code, wait for it and look for response code within
			print("Response code: %s" % response.status_code)
			check = checkJobStatus(response)
			#headers = {"Authorization": "Bearer " + tk}
			#response = requests.get(ip + check, headers=headers, verify=False)
			print("Waiting for response", end=' ')
			while response.status_code == 202:
				headers = {"Authorization": "Bearer " + tk}
				response = requests.get(ip + check, headers=headers, verify=False)
				print(".", end=' ')
			print(" Done")
			if 201 == response.status_code:
				print("Response code: %s" % response.status_code)
				colorPrint(text="Success", color="g")
			elif 200 == response.status_code:
				print("Response code: %s" % response.status_code)
				colorPrint(text="Success", color="g")
			else:
				print("Error - Response code: %s" % response.status_code)
				var = json.loads(response.text)
				print(var["message"])
				colorPrint(text="Failure", color="r")
		elif 400 == response.status_code:
			jsonData = json.loads(response.text)
			print("Error - Response code: %s" % response.status_code)
			print(jsonData["message"])
			colorPrint(text="Failure", color="r")
		elif 401 == response.status_code:
			jsonData = json.loads(response.text)
			print("Error - Response code: %s" % response.status_code)
			print(jsonData["message"])
			colorPrint(text="Failure", color="r")
		elif 404 == response.status_code:
			jsonData = json.loads(response.text)
			print("Error - Response code: %s" % response.status_code)
			print(jsonData["message"])
			colorPrint(text="Failure", color="r")
		elif 500 == response.status_code:
			jsonData = json.loads(response.text)
			print("Error - Response code: %s" % response.status_code)
			print(jsonData["message"])
			colorPrint(text="Failure", color="r")
		else:
			colorPrint(text="ERROR unknown status_code %s" % response.status_code, color="g")

	def checkJobStatus(response):
		jobData = json.loads(response.text)
		jobStatus = jobData["links"][0]["href"] # Make sure that zero is always the right array index
		return jobStatus

	def login(usr, passwd):
		payload = {"password": passwd, "username": usr}
		print("Login to obtain authorization token...")
		response = requests.post(sourceUrl + "/auth/login", data=payload, verify=False)
		jsonData = json.loads(response.text)
		print("Authorization token is: " + jsonData["token"])
		return jsonData["token"]
		checkStatus(response,tk=tks, ip=sourceUrl)

	def createDataset(ds, tk):
		headers = {"content-type": "application/json", "Authorization": "Bearer " + tk}
		payload = {"path": ds}
		response = requests.post(sourceUrl + "/storage/filesystems", data=json.dumps(payload), headers=headers, verify=False)
		checkStatus(response, tk=tk, ip=sourceUrl)

	def destroyDataset(tk, ds, rt, ip):
		dse = urllib.parse.quote_plus(ds)
		headers = {"Authorization": "Bearer " + tk}
		if rt == "local":
			response = requests.delete(ip + "/storage/filesystems/" + dse + "?snapshots=true", headers=headers, verify=False)
		elif rt == "remote":
			response = requests.delete(ip + "/storage/filesystems/" + dse + "?snapshots=true", headers=headers, verify=False)
		elif rt == "snapshots":
			response = requests.delete(ip + "/storage/filesystems/" + dse + "?snapshots=true", headers=headers, verify=False)
		else:
			colorPrint(text="ERROR: Unknown argument: " + rt, color="r")
			printHelp()
		checkStatus(response, tk=tk, ip=ip)

	def createReplicationService(tk, rt, sn, sd, dd, scn):
		headers = {"content-type": "application/json", "Authorization": "Bearer " + tk}
		if rt == "local":
			payload = {"name": sn, "sourceDataset": sd, "type": svcType, "destinationDataset": dd, "schedules": [{"scheduleName": scn, "cron": howOften, "keepSource": keepSS, "keepDestination": keepSS, "disabled": False}]}
		elif rt == "remote":
			payload = {"name": sn, "sourceDataset": sd, "type": svcType, "destinationDataset": dd, "isSource": True, "remoteNode": {"host": remoteHost}, "schedules": [{"scheduleName": scn, "cron": howOften, "keepSource": keepSS, "keepDestination": keepSS, "disabled": False}]}
		elif rt == "snapshots":
			payload = {"name": sn, "sourceDataset": sd, "type": svcType, "schedules": [{"scheduleName": scn, "cron": howOften, "keepSource": keepSS, "disabled": False}]}
		else:
			colorPrint(text="ERROR: Unknown argument: " + rt, color="r")
			printHelp()
		response = requests.post(sourceUrl + "/hpr/services", data=json.dumps(payload), headers=headers, verify=False)
		checkStatus(response, tk=tk, ip=sourceUrl)

	def destroyReplicationService(tk, sn):
		headers = {"Authorization": "Bearer " + tk}
		response = requests.delete(sourceUrl + "/hpr/services/" + sn, headers=headers, verify=False)
		checkStatus(response, tk=tk, ip=sourceUrl)

	def statusService(tk, sn):
		headers = {"Authorization": "Bearer " + tk}
		response = requests.get(sourceUrl + "/hpr/services/" + sn, headers=headers, verify=False)
		checkStatus(response, tk=tk, ip=sourceUrl)
		if response.status_code == 200:
			jsonData = json.loads(response.text)
			state = jsonData["state"]
			if state == "faulted":
				print("Service " + sn + " state is " + state)
				return 1
			else:
				print("Service " + sn + "state is " + state)

	def enableService(tk, sn):
		headers = {"Authorization": "Bearer " + tk}
		response = requests.post(sourceUrl + "/hpr/services/" + sn + "/enable", headers=headers, verify=False)
		checkStatus(response, tk=tk, ip=sourceUrl)

	def disableService(tk, sn):
		headers = {"Authorization": "Bearer " + tk}
		response = requests.post(sourceUrl + "/hpr/services/" + sn + "/disable", headers=headers, verify=False)
		checkStatus(response, tk=tk, ip=sourceUrl)

	def clearService(tk, sn):
		headers = {"Authorization": "Bearer " + tk}
		response = requests.post(sourceUrl + "/hpr/services/" + sn + "/clear", headers=headers, verify=False)
		checkStatus(response, tk=tk, ip=sourceUrl)

	try:
		opts, args = getopt.getopt(argv, "hc:d:", ["create=", "delete="])
	except getopt.GetoptError:
		colorPrint(text="ERROR: Wrong use of command line argument(s), please see usage for more info", color="r")
		printHelp()
	for opt, arg in opts:
		if opt == "-h":
			printHelp()
		elif opt in ("-c", "-create"):
			# Login to obtain token
			token = login(usr = user, passwd = password)
			time.sleep(3)
			repType = arg
			if repType == "snapshots":
				# Creating runTimes number of Scheduled Snapshots services
				for i in range (0, runTimes):
					sn = svcName + repr(i)
					sd = srcDataset + repr(i)
					scn = schName + repr(i)
					dd = destDataset + repr(i) # Not used in this case
					print("Creating source dataset " + sd + " ...")
					createDataset(ds=sd, tk=token)
					print("Creating Scheduled Snapshots service " + scn + " ...")
					createReplicationService(tk=token, rt=repType, sn=sn, sd=sd, dd=dd, scn=scn)
					print("Enabling service Scheduled Snapshots service " + sn + " ...")
					enableService(tk=token, sn=sn)
			elif repType == "local":
				# Creating runTimes number of Local Replication services
				for i in range (0, runTimes):
					sn = svcName + repr(i)
					sd = srcDataset + repr(i)
					dd = destDataset + repr(i)
					scn = schName + repr(i)
					print("Creating source dataset " + sd + " ...")
					createDataset(ds=sd, tk=token)
					print("Creating Local Replication service " + scn + " ...")
					createReplicationService(tk=token, rt=repType, sn=sn, sd=sd, dd=dd, scn=scn)
					print("Enabling service Local Replication service " + sn + " ...")
					enableService(tk=token, sn=sn)
			elif repType == "remote":
				# Creating runTimes number of Remote Replication services
				for i in range (0, runTimes):
					sn = svcName + repr(i)
					sd = srcDataset + repr(i)
					dd = destDataset + repr(i)
					scn = schName + repr(i)
					print("Creating source dataset " + sd + " ...")
					createDataset(ds=sd, tk=token)
					print("Creating Remote Replication service " + sn + " ...")
					createReplicationService(tk=token, rt=repType, sn=sn, sd=sd, dd=dd, scn=scn)
					print("Enabling service Local Replication service " + sn + " ...")
					enableService(tk=token, sn=sn)
			else:
				colorPrint(text="ERROR: Unknown argument: " + repType, color="r")
				printHelp()
		elif opt in ("-d", "-destroy"):
			# Login to obtain token
			token = login(usr = user, passwd = password)
			time.sleep(3)
			repType = arg
			if repType == "snapshots":
				# Destroying runTimes number of Scheduled Snapshots services
				for i in range (0, runTimes):
					sn = svcName + repr(i)
					sd = srcDataset + repr(i)
					dd = destDataset + repr(i) # Not used in this case
					print("Checking Scheduled Snapshots service " + sn + " status ...")
					if statusService(tk=token, sn=sn) == 1:
						print("Clearing faulted service " + sn + " ...")
						clearService(tk=token, sn=sn)
					else:
						print("Disabling Scheduled Snapshots service " + sn + " ...")
						disableService(tk=token, sn=sn)
					print("Destroying Scheduled Snashots service " + sn + " ...")
					destroyReplicationService(tk=token, sn=sn)
					print("Destroying source dataset " + sd + " ...")
					destroyDataset(tk=token, ds=sd, rt=repType, ip=sourceUrl)
			elif repType == "local":
				# Destroying runTimes number of Local Replication services
				for i in range (0, runTimes):
					sn = svcName + repr(i)
					sd = srcDataset + repr(i)
					dd = destDataset + repr(i)
					print("Checking Local Replication service " + sn + " status ...")
					if statusService(tk=token, sn=sn) == 1:
						print("Clearing faulted service " + sn + " ...")
						clearService(tk=token, sn=sn)
					else:
						print("Disabling Local Replication service " + sn + " ...")
						disableService(tk=token, sn=sn)
					print("Destroying Local Replication service " + sn + " ...")
					destroyReplicationService(tk=token, sn=sn)
					print("Destroying destination dataset " + dd + " ...")
					destroyDataset(tk=token, ds=dd, rt=repType, ip=sourceUrl)
					print("Destroying source dataset " + sd + " ...")
					destroyDataset(tk=token, ds=sd, rt=repType, ip=sourceUrl)
			elif repType == "remote":
				# Destroying runTimes number of Remote Replication services
				for i in range (0, runTimes):
					sn = svcName + repr(i)
					sd = srcDataset + repr(i)
					dd = destDataset + repr(i)
					print("Checking Remote Replication service " + sn + " status ...")
					if statusService(tk=token, sn=sn) == 1:
						print("Clearing faulted service " + sn + " ...")
						clearService(tk=token, sn=sn)
					else:
						print("Disabling Remote Replication service " + sn + " ...")
						disableService(tk=token, sn=sn)
					print("Destroying Remote Replication Service " + sn + " ...")
					destroyReplicationService(tk=token, sn=sn)
					print("Destroy destination dataset" + dd + " ...")
					destroyDataset(tk=token, ds=dd, rt=repType, ip=remoteUrl)
					print("Destroying source dataset " + sd + " ...")
					destroyDataset(tk=token, ds=sd, rt=repType, ip=sourceUrl)
			else:
				colorPrint(text="ERROR: Unknown argument: " + repType, color="r")
				printHelp()
if __name__ == "__main__":
	if len(sys.argv) < 2: # If no command line arguments are giveni, print help
		colorPrint(text="No command line arguments, please see usage for more info", color="r")
		printHelp()
	main(sys.argv[1:])
