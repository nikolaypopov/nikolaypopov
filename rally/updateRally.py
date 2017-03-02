#!/usr/bin/python

import json, time, datetime, re
from pyral import Rally, rallyWorkset

# Created by Nikolay Popov 
# on 5/25/2016
# This is example of how to update Rally testcases using Rally REST API
#
# This is the example of how to use this function with my jencins build number function or with just plain notes
# createRallyTestCaseResult(tcid = "TC01", tcr = "Fail", note = jenkinsLastBuildNumber(tn = testCaseName))
# createRallyTestCaseResult(tcid = "TC01", tcr = "Fail", note = "some notes")

def createRallyTestCaseResult(tcid, tcr, note):
	my_server = "rally1.rallydev.com"
	my_apikey = "_LOLAPIKEYVERYLONGLOOKINGONE" # This used to login instead of my username and password, i made it up
	my_workspace = "WORKSPACENAME"
	my_project = "PROJECTNAME"

	def timeStamp():
		return datetime.datetime.now().isoformat()

	# Passed parameters from test case (Test Case ID Number and Test Case Result)
	my_tc = tcid
	my_result = tcr
	print "Test Case: " + my_tc + ", Result: " + my_result
	target_test_case_id = 'FormattedID = "{}"'.format(my_tc)

	my_date = timeStamp() # Date now
	print "Date: " + my_date

	rally = Rally(my_server, apikey=my_apikey, workspace=my_workspace, project=my_project) # Authorization using ApiKey
	#rally.enableLogging("createtestcaseresult.log")

	print "Getting Project details ... "
	time.sleep(3)
	target_project = rally.getProject() # Getting Project details
	tp = target_project

	#print "***************************************************************"
	#print tp.details() # Printing Project details
	#print "***************************************************************"

	print "Getting Test Case details ... "
	time.sleep(3)
	target_test_case = rally.get('TestCase', fetch=True, query=target_test_case_id, project=tp.Name) # Getting TestCase details

	tc = target_test_case.next()
	#print "***************************************************************"
	#print tc.details() # Printing TestCase details
	#print "***************************************************************"

	test_case_result_fields = { # Body for TestCaseResults
		'TestCase': tc.ref,
		'Build': 'Automation Build Name', # You could also pass this parameter but I didn't need to at the time
		'Verdict': my_result,
		'Notes': note, # Print URL that points to Jenkins test case output
		'Date': my_date
	}

	print "Adding Test Case Result ... "
	test_case_result = rally.create('TestCaseResult', test_case_result_fields) # Creating TestCaseResult
	print "Done!"
