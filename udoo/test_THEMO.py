# Script that generates two waveforms, a chirp and a sine, and writes
# them, one after tho other, to a single WAV file

import scipy as sp
import numpy as np
import THEMOSignal as TS



### Generation part

# define parameters
SAMP_FREQ = 96000 # Hz
FILENAME = "sound.wav"

# Generate a chirp signal passing from 200 to 400 Hz in 5 seconds
sig1 = TS.Chirp(200, 400, 5)
# Generate a sine tone at 260 Hz frequency
sig2 = TS.Sine(260)

# Generate the waves of 1 second length
wave1 = sig1.make_wave(0, 1)
wave2 = sig2.make_wave(0, 1)

# collect the waves into a list
wavelist = [wave1, wave2]

# write a WAV file at sampling frequency 96 kHz
TS.writeToWAV(wavelist, FILENAME, SAMP_FREQ)




### Recording part

rec1 = TS.Recording(18000, 34000, 1)

state = rec1.analyze("sound.wav")
