""" Module for generating signals according to user specifications.

The user inputs some parameters, used for generating a signal
to be used in the experiments she wants to set up.
The waveform is then generated and sent down the cable, through
the modem, to the submerged node.
As parallel, signals coming from the hydrophones are passed through
an FFT to allow discriminate them, prior to proper analysis.

Copyright 2016 Signet Lab, University of Padova
License: GNU GPLv3 http://www.gnu.org/licenses/gpl.html
"""

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import math
from scipy import signal
import wave


class Signal(object):
    """ Class that defines a signal according to specifics.
  
    This class is just a container for parameters of the
    signal. The creation of signal samples is postponed as
    much as possible, and is obtained through a Wave object.
    """
        
    def __init__(self):
        """A Signal object basically store parameters"""


    def make_wave(self, start=0, duration=1, samplerate=96000):
        """Method that creates a Wave object from a Signal object.
    
        start: float seconds
        duration: float seconds
        samplerate: int samples per second

        returns: Wave object
        """
        
        n = round(duration*samplerate)
        times = np.linspace(start, start+duration, n)
        samples = self.evaluate(times)
        return Wave(samples, times, samplerate)


class Wave(object):
    """Represents a discrete-time waveform to be written to a file."""

    def __init__(self, samples, times, samplerate):
        """Creates a Wave object.

        samples: ndarray double
        time_s: ndarray double
        samplerate: double Hertz
        """
        if (samples.size != times.size):
            print "Error: samples not associated with time instants"
            return         
   
        self.samples = samples
        self.time_s = times
        self.samplerate = samplerate
        self.n_samples = samples.size


class Chirp(Signal):
    """Class that defines a Chirp according to specifics.

    This class is just a container for parameters as 
    the writing down is delayed as much as possible.
    The actual waveform samples are obtained by making 
    a Wave object from the Signal object handling it.
    """

    def __init__(self, startf=200, stopf=400, t1=1, method='linear'):
        """Initializes a Chirp signal. 

        startf: float frequency in Hertz (at time 0)
        stopf: float frequency in Hertz (at time t1)
        t1: time instant at which stopf is reached
        method: string indicating the method ['linear','exponential']
        """
        self.startf = startf
        self.stopf = stopf
        self.t1 = t1
        self.method = method

    def evaluate(self, tsamples):
        """Evaluates the signal at the given time instants.

        returns: float ndarray
        """ 
        ts = np.asarray(tsamples)
        return signal.chirp(ts, self.startf, self.t1, self.stopf, self.method)

class Sine(Signal):
    """Class that defines a Sine according to specifics.

    This class is just a container for parameters as 
    the writing down is delayed as much as possible.
    The actual waveform samples are obtained by making 
    a Wave object from the Signal object handling it.
    """
    
    def __init__(self, frequency=440, amplitude=1, offset=0):
        """Initialize a Sin signal.

        frequency: double frequency in Hertz
        amplitude: double amplitude in Volts
        offset: double offset initial phase
        """
        self.freq = frequency
        self.amp = amplitude
        self.offset = offset

    def evaluate(self, tsamples):
        """Evaluates the signal at the given time instants.

        tsamples: ndarray time samples
        
        returns: float ndarray
        """
        ts =  np.asarray(tsamples)
        phases = 2*math.pi * self.freq * ts + self.offset
        return self.amp * np.sin(phases)
            


def writeToWAV(waves, filename, framerate=44100, resolution=2, n_channels=1): 
    """Method that creates a WAV file from the Waves objects it gets as input.

    waves: list with all signals that will go in the WAV file
    filename: string containing the filename
    resolution: integer number of bytes encoding a sample
    n_channels: integer number of channels (1 or 2)
    """

    # find out hw many you need and collect samples
    n_samples = 0    

    for w in waves:
        n_samples = n_samples + w.samples.size
  
    wsamples = np.zeros(n_samples)
  
    t_ind = 0
    for w in waves:
        wsamples[t_ind:t_ind+w.n_samples] = w.samples
        t_ind = w.n_samples

    # open file to write
    wfile = wave.open(filename, 'w')
    
    wfile.setnchannels(n_channels)
    wfile.setframerate(framerate)
    wfile.setsampwidth(resolution)

    # write to file
    wfile.writeframes(wsamples)

    # close the file
    wfile.close()
