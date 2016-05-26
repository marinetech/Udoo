# Script that generates two waveforms, a chirp and a sine, and writes
# them, one after tho other, to a single WAV file

import scipy as sp
import numpy as np
import THEMOSignal as TS
import wave
import random


### Generation part

# define parameters
SAMP_FREQ = 96000 # Hz
FILENAMEWAV = "sound.wav"
FILENAMENOISE = "noise.wav"
FILENAMECSV = "sound.csv"
VOL = 60 # volume 60%


# generate some noise for the purpose of simulation
noise_dur = 1.
mean = 0
std = 1 
num_samples = int(SAMP_FREQ/noise_dur)
# noise_f = np.random.normal(mean, std, size=num_samples)*32767*0.4
noise = np.zeros(num_samples, dtype='int16')

for n in range(num_samples):
    noise[n] = (random.random()*2-1)*32767*0.4

wfile = wave.open(FILENAMENOISE, 'w')

wfile.setnchannels(1)
wfile.setframerate(SAMP_FREQ)
wfile.setsampwidth(2)
wfile.setnframes(noise.size)

# transform to binary
wnoise = ''
for i in range(len(noise)):
    wnoise += wave.struct.pack('h', noise[i])

# write to file
wfile.writeframes(wnoise)

# close the file
wfile.close()



## Generate a chirp signal passing from 50 to 100 Hz in 1 second
sig1 = TS.Chirp(50, 100, 1)
# Generate a sine tone at 100 Hz frequency
sig2 = TS.Sine(100)

# Generate the waves of 1 second length
wave1 = sig1.make_wave(0, 1)
wave2 = sig2.make_wave(0, 1)

# Collect the waves into a list
wavelist = [wave1, wave2]

# write a WAV file at sampling frequency 96 kHz
TS.writeToWAV(wavelist, FILENAMEWAV, SAMP_FREQ, VOL, 2)

# write a CSV file 
TS.writeToCSV(wavelist, FILENAMECSV)


### Recording part
THRESHOLD=10 # dB (SNR)
# Create the recording object for noise
rec = TS.Recording([18000, 34000], THRESHOLD)
# Analyze noise
noise_p = rec.analyzenoise(FILENAMENOISE)
# Analyze signal
state = rec.analyze(FILENAMEWAV)

# find the power of the signal
sig_samples = rec.getsamples(FILENAMEWAV)
samplesFFT = np.fft.fft(sig_samples)
samplespower = np.linalg.norm(samplesFFT, 2)


print "State: " + str(state)
print "SNR: "+ str(10*np.log10(samplespower/noise_p))+" dB"
