from multiprocessing import Process
from functools import partial

import time, os, sys
import signal

sys.path.append('../lib/')
from common import Timeout

def parallel(func):
    def parallel_func(*args, **kw):
        p = Process(target=func, args=args, kwargs=kw)
	timeout = 2
        p.start()
	counter = 0
	while p.is_alive() == True:
		time.sleep(1)
		counter += 1
		if counter > timeout:
			print 'Son process consumed too much run-time. Going to kill it!'
			os.kill(p.pid, 0)
			break
    return parallel_func

@parallel
def timed_print(x):
    for i in range(x):
	print 'time_print %s' % i
	time.sleep(0.2)

def example1():
    #timed_print(20)
    #time.sleep(0.1)
    for z in range(20):
        print 'z = %s' % z
        time.sleep(0.2)

def example2():
    wait = 0
    sec = 0
    while wait == 0:
	sec += 1
	if sec == 60:
	    print "sec reached 60, exiting loop"
	    wait = 1
            break
	else:
	    print sec
	    time.sleep(1)

def main():
    # Run block of code with timeouts
    try:
        with Timeout(10):
            example2()
#        with Timeout(1):
#            example()
    except Timeout.Timeout:
        print "Timeout"


#main()

#example()
