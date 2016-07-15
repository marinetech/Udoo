# Generate and transmit a wav file to the node and issue to play it

# IMPORT FOR CONNECTION

import sys
import ud2no_pkg
import os
import time

# IMPORT FOR GENERATE WAV

import scipy as sp
import numpy as np
import themosignal as ts
import wave
import random

# CONNECTION with the node

TCP_IP = "165.91.230.227"
#TCP_IP = "127.0.0.1"
TCP_PORT = 44444
BUFFER_SIZE = 64
DATA_BUFFER_SIZE = 64

myPID = os.getpid()
print "HI ", myPID, "!!"
print("Hello")
bridge = ud2no_pkg.Modem(TCP_IP,TCP_PORT,True,BUFFER_SIZE,DATA_BUFFER_SIZE)
print("Connected")
########

# GENERATE SIGNAL 
### Generation part

# define parameters
SAMP_FREQ = 96000 # Hz
FILENAMEWAV = "sound.wav"
FILENAMENOISE = "noise.wav"
FILENAMECSV = "sound.csv"
VOL = 60 # volume 60%

## Generate a chirp signal passing from 50 to 100 Hz in 1 second
sig1 = ts.Chirp(50, 100, 1)
# Generate a sine tone at 100 Hz frequency
sig2 = ts.Sine(100)

# Generate the waves of 1 second length, starting from 0
wave1 = sig1.make_wave(0, 1)
wave2 = sig2.make_wave(0, 1)

# Collect the waves into a list
wavelist = [wave1, wave2]

# write a WAV file at sampling frequency 96 kHz
ts.writeToWAV(wavelist, FILENAMEWAV, SAMP_FREQ, VOL, 2)

time.sleep(1)

projector_list = [2,3]

print "File Generater: ", FILENAMEWAV

try:
	bridge.sendDataFile(FILENAMEWAV)
	time.sleep(0.1)
	print "File Sent: ", FILENAMEWAV
	bridge.reqSetPower(projector_list,5)
	time.sleep(0.1)
	bridge.reqPlayProj(FILENAMEWAV,[1,4],round(time.time() + 2))
	print "File Played 10 times: ", FILENAMEWAV
	bridge.reqResetSensors(1,[1,4])
	time.sleep(0.1)
	bridge.reqDeleteAllSent()
	time.sleep(0.1)
	bridge.reqResetProj(projector_list)

finally:
	print >>sys.stderr, 'closing socket'
	bridge.close()
