#!/usr/bin/python

import unittest, pytest, os, time

class MyClass(unittest.TestCase):

#*********************************************************
# NSVP HPR related test cases
#*********************************************************

	def test_001_scheduled_snapshots(self):
		rc = os.system("/koka/tests/hpr-snapshots.py")		
		self.assertEqual(rc, 0)
	
	time.sleep(5)

	def test_002_local_replication(self):
		rc = os.system("/koka/tests/hpr-local.py")
		self.assertEquals(rc, 0)

	time.sleep(5)

	def test_003_remote_replication(self):
		rc = os.system("/koka/tests/hpr-remote.py")		
		self.assertEqual(rc, 0)

	time.sleep(5)

	def test_004_snapshot_create_delete(self):
		rc = os.system("/koka/tests/snapshot-create-delete.py")
		self.assertEqual(rc, 0)

	def test_004_scheduled_snapshots_volume(self):
		rc = os.system("/koka/tests/hpr-snapshots-volume.py")
		self.assertEqual(rc, 0)

	time.sleep(5)

	def test_005_local_replication_volume(self):
		rc = os.system("/koka/tests/hpr-local-volume.py")
		self.assertEqual(rc, 0)

	time.sleep(5)

	def test_006_remote_replication_volume(self):
		rc = os.system("/koka/tests/hpr-remote-volume.py")
		self.assertEqual(rc, 0)

	time.sleep(5)

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(MyClass)
	unittest.TextTestRunner(verbosity=2).run(suite)
