import re, signal

class Timeout():
	"""Timeout class using ALARM signal."""
	class Timeout(Exception):
		pass

	def __init__(self, sec):
		self.sec = sec
 
	def __enter__(self):
		signal.signal(signal.SIGALRM, self.raise_timeout)
		signal.alarm(self.sec)
 
	def __exit__(self, *args):
		signal.alarm(0)    # disable alarm
 
	def raise_timeout(self, *args):
		raise Timeout.Timeout()

class Output():

	def __init__(self):
		pass

	# Function to print 'g' = green, 'r' = red
	def colorPrint(self, text, color):
		if color == "g": # Green print
			print(("\033[1;32;40m{}\033[0;37;40m").format(text))
		if color == "r": # Red print
			print(("\033[1;31;40m{}\033[0;37;40m").format(text))

	def match_line(self, text):
		my_line = "{}".format(text)
		match = re.search('\w+\s(\w+).', my_line)
		if match:
			return match.group(1)
		else:
			return "No Match"

