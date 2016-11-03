#import thread
import threading

#import socket
from socket import *

# import winsound
import winsound

# import random
import random

# import egi

# import egi.simple as egi
import egi.threaded as egi
## # make the script reenterable )
## # -- for ipython "%edit ... " tests
## reload(egi)

import sys # sys.argv[]
import time # time.sleep()

#
# probably 'ms_localtime()' stuff should be hidden under the hood as well,
# but at the moment we'll need to explicitly use this function when we send markers,
# as this is what we use internally in sync()
#


## ms_localtime = egi.egi_internal.ms_localtime
ms_localtime = egi.ms_localtime

isTestStart = False
isTestStop = False

class recvThread(threading.Thread):
	def __init__(self, threadID, name):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
	def run(self):
		wait_command('10.10.10.60', 55514, 1024)

def wait_command(host, port, bufsize):
	global isTestStart
	global isTestStop
	ADDR = (host, port)

	udpSerSock = socket(AF_INET, SOCK_DGRAM)
	udpSerSock.bind(ADDR)

	data, addr = udpSerSock.recvfrom(bufsize)
	if (data[0:4] == 'STRT'):
		data_snd = 'ACK'
		udpSerSock.sendto(data_snd, addr)
		isTestStart = True
	elif (data[0:4] == 'CRUS'):
		ns.send_event('CRUS')
	elif(data[0:4] == 'LAND'):
		ns.send_event('LAND')
	elif(data[0:4] == 'STOP'):
		data_snd = 'ACK'
		udpSerSock.sendto(data_snd, addr)
		isTestStop = True

	udpSerSock.close()

trails = 100000 #need to be big
randomdata = range(1,trails+1)
traillist = random.sample(randomdata, trails)

#
# Panels / Multi-Port ECI --> log
# or just Panels --> Log (I assume you have selected 'Long Form')
#

ns = egi.Netstation()

# sample address and port -- change according to your network settings
## ns.connect('11.0.0.42', 55513)

print "Oddball:Connecting..."
ns.initialize('10.10.10.42', 55513)
# Multi-Port ECI Window: "Connected to PC"

print "Oddball:Begin Session..."
ns.BeginSession()
# log: 'NTEL' \n

print "Oddball:Synching..."
ns.sync()
# log window: the timestamp ( the one provided by ms_localtime() )
## ns.send_event('evt2', label="event2")

print "Oddball:MARK 'INIT'..."
ns.send_event('INIT')

startThread = recvThread(1, "start_thread")
startThread.start()

print "MainConsole:WAIT..."
while(isTestStart == False):
	time.sleep(0.1)
print "MainConsole:START..."

stopThread = recvThread(1, "stop_thread")
stopThread.start()

ns.StartRecording()
ns.send_event('STRT')
# I do not recommend to use this feature, as my experience is that Netstation
# [ the version _we_ use, may be not the latest one ] may sometimes crash
# on this command ; so I'd rather click the 'record' and 'stop' buttons manually.

#Stimulation counter
stim_stn=0
stim_odd=0

# Present the stimulation
print "Oddball:MARK 'BGIN'..."
ns.send_event('BGIN', timestamp=egi.ms_localtime())
for i in range(1, trails+1):
	if (isTestStop == True):
		print "MainConsole:STOP..."
		break
	i = i - 1
	if(traillist[i] <= trails*0.8):
		winsound.Beep(1000,50)
		ns.send_event('STM+', timestamp=egi.ms_localtime())
		stim_stn = stim_stn + 1
	else:
		winsound.Beep(1100,50)
		ns.send_event('STM-', timestamp=egi.ms_localtime())
		stim_odd = stim_odd + 1

	ns.send_event('BLNK', timestamp=egi.ms_localtime())
	time.sleep(0.5)

print "Oddball:MARK 'TEND'..."
ns.send_event('TEND', timestamp=egi.ms_localtime())

print "Oddball:MARK 'STOP'..."
ns.send_event('STOP') # just to have some "end of session" marker in the log

print "Oddball:Stop Recording..."
ns.StopRecording()

## ns.EndSession()
## ns.disconnect()
print "Oddball:MARK 'UNIT'..."
ns.send_event('UNIT')

print "Oddball:End Session..."
ns.EndSession()

print "Oddball:Disconnecting..."
ns.finalize()

print "Standard stimulation:%d"%stim_stn
print "Oddball stimulation:%d"%stim_odd
# Final notes:

# 0. To view / export the event markers:
#    open session file -->
#    --> Events --> Event List -->
#    --> opt-click to "unwrap" all the field entries
#    --> File --> Save Events

# 1. Starting / stopping the recording automatically is not recommended ;

# 2. Maximum amount of entries in the table is 256 ;
#    the length (in bytes) of every value in the table should not exceed 65536 .


# 3. In our example events 5,6 would appear in the log window in the order of appearance,
#    but in the corrected order for the event list ;
#    actually, for the event list *all* the events are sorted according to their timestamps,
#    so if some events arrive at the same millisecond, they may appear in the "wrong" order in the list .

