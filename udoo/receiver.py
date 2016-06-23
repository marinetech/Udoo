#TODO: connect to the node to issue the reception and procees the acquared data files. 
#The ones cointainig signals will be uploaded to the PC104

# IMPORT FOR CONNECTION

import sys
import ud2no_pkg
import os
import time

# IMPORT FOR PROCESS WAV

import scipy as sp
import numpy as np
import themosignal as ts
import wave
import random

# CONNECTION with the node

TCP_IP = "192.168.100.98"
TCP_IP = "127.0.0.1"
TCP_PORT = 44444
BUFFER_SIZE = 64
DATA_BUFFER_SIZE = 64

FILENAMENOISE = "noise.wav"

myPID = os.getpid()
print "HI ", myPID, "!!"
print("Hello")
bridge = ud2no_pkg.Modem(TCP_IP,TCP_PORT,True,BUFFER_SIZE,DATA_BUFFER_SIZE)
print("Connected")
########

bridge.reqRecordData(FILENAMENOISE,1,[1,4],"10",5)
time.sleep(1)
bridge.reqDataFile(FILENAMENOISE)
time.sleep(1)

### Recording part
THRESHOLD = 5 # dB (SNR)
# Create the recording object for noise
rec = ts.Recording([7000, 78000], THRESHOLD)
# Calculate noise power
noise_p = rec.noise_power(FILENAMENOISE)
# Record signal: date format 'dd.mm.YYYY hh:mm:ss'

bridge.reqRTData(1,[1,3], "20",20)

rec.record_stream(time.strftime('%d.%m.%Y %H:%M:%S', time.localtime()), 20, ".")

####### find the power of the signal to plot SNR ####################
sig_samples = rec.getsamples(FILENAMEWAV)
samplesFFT = np.fft.fft(sig_samples)
samplespower = np.linalg.norm(samplesFFT, 2)
#####################################################################

print "SNR: "+ str(10*np.log10(samplespower/noise_p))+" dB"
print "Done! Give me coffee!"
