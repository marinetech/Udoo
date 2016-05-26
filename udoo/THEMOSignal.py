""" Module for generating signals according to user specifications.

The user inputs some parameters, used for generating a signal
to be used in the experiments she wants to set up.
The waveform is then generated and sent down the cable, through
the modem, to the submerged node.
As parallel, signals coming from the hydrophones are passed through
an FFT to allow discriminate them, prior to proper analysis.

Copyright 2016 Signet Lab, University of Padova https://signet.dei.unipd.it
License: GNU GPLv3 http://www.gnu.org/licenses/gpl.html
"""

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import math
from scipy import signal
import wave
import os


class Signal(object):
    """ Class that defines a signal according to specs.
  
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

    def __init__(self, samples, times=None, samplerate=None):
        """Creates a Wave object.

        samples: ndarray double
        time_s: ndarray double
        samplerate: double Hertz
        """
        if (samples.size != times.size):
            print "Error: samples not associated with time instants"
            return         
   
        self.samples = samples
        if samplerate != None:
            self.samplerate = samplerate
        else:
            self.samplerate = 96000

        if times is None:
            self.time_s = np.arange(len(samples)) / self.framerate
        else:
            self.time_s = np.asanyarray(times)

        self.n_samples = samples.size


class Chirp(Signal):
    """Class that defines a Chirp according to specs.

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
    """Class that defines a Sine according to specs.

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


class Rect(Signal):            
    """Class that defines a train of Rects according to specs.

    This class is just a container for parameters as 
    the writing down is delayed as much as possible.
    The actual waveform samples are obtained by making 
    a Wave object from the Signal object handling it.
    """
    
    def __init__(self, duty_cycle=0.5, period=0.1, amplitude=1, offset=0):
        """Initialize a Sin signal.

        duty_cycle: double ratio of pulse duration to period
        period: double distance between repetion of rects
        amplitude: double amplitude in Volts
        offset: double initial shift of the waveform
        """
        self.duty_cycle = duty_cycle
        self.period = period
        self.amplitude = amplitude

    def evaluate(self, tsamples):
        """Evaluates the signal at the given time instants.

        tsamples: ndarray time samples
        
        returns: float ndarray
        """
        ts =  np.asarray(tsamples)
        pulse_d = duty_cycle * period
        return self.amp * ((ts + offset) % period < pulse_d)


class Recording(object):
    """ Class  that handles wav files and does an initial analysis.

    Initial discrimination of signal is done by calculating the 
    spectrum of a portion of it and by by trsholding it.
    """

    def __init__(self, filename, band=[18000, 34000], th=1):
        """ Object holding data relative to file being read.

        start_f double starting frquency of the band of interest
        stop_f double stop frequency of the band of interest
        th: treshold on the power of the spectrum
        """
        self.filename = filename
        self.start_f = band[0] 
        self.stop_f = band[1]
        self.treshold = th

        rfile = wave.open(filename, 'r')

        params = rfile.getparams()
        #getparams output: [nchann, sampwidth, framerate, nframes, ctype, cname]
     
        # check channels
        if params[0] > 1:
            print "More than one audio channel"
            sys.exit(0)
         
        # check sample width
        datawidth = 'Int' + str(params[1]*8)
         
        # extract samples
        rstring = rfile.readframes(-1)
        rsamples = np.fromstring(rstring, datawidth)

        self.samples = rsamples

        

    def getsamples(self):

        """Obtain samples from recording filename
        """
        return self.samples


    def plotspec(self,filename):
        """Plot spectrogram of the loaded file.

        filename of the audio file to be loaded
        """

        NFFT = 1024       # the length of the windowing segments
        Fs = params[2]    # the sampling frequency

        Pxx, freqs, bins, im = plt.specgram(self.samples, NFFT=NFFT, Fs=Fs,
                                            noverlap=256,
                                            cmap=plt.cm.gist_heat)
        plt.show()
        
        
    def analyze(self):
        """Parse recordings through spectrogram

        This method makes the FFT of the file filename and treshold it.
        If the file pass the teshold test it is marked as 'sendable',
        otherwise it is discarded.

        filename string with, guess... the filename!
        """

        # FFT
        rsamplesFFT = np.fft.fft(self.samples)

        rsamplespower = np.linalg.norm(rsamplesFFT, 2)
 
        if rsamplespower < self.treshold:
            os.remove(self.filename)
            return 1
        else:
            return 0
        

def writeToWAV(waves, filename, framerate=96000, volume=60, resolution=2): 
    """Method that creates a WAV file from the Waves objects it gets as input.

    waves list with all signals that will go in the WAV file
    filename string containing the filename
    volume integer from 0 to 100 indicting volume of the wav
    resolution integer number of bytes encoding a sample
    """

    vol = volume*0.01
    
    n_samples = 0

    for w in waves:
        n_samples = n_samples + w.samples.size

    swidth = 'int' + str(8*resolution)
    wsamples = np.zeros(n_samples, dtype=swidth)
  
    t_ind = 0
    for w in waves:
        wsamples[t_ind:t_ind+w.n_samples] = w.samples*32767*vol
        t_ind = w.n_samples
    
    # open file to write
    wfile = wave.open(filename, 'w')
    
    wfile.setnchannels(1)
    wfile.setframerate(framerate)
    wfile.setsampwidth(resolution)
    wfile.setnframes(wsamples.size)

    # transform to binary
    swsamples = ''
    for i in range(len(wsamples)):
         swsamples += wave.struct.pack('h', wsamples[i])
    
    # write to file
    wfile.writeframes(swsamples)

    # close the file
    wfile.close()


def writeToCSV(waves, filename):
    """Method that creates a CSV file from the Waves objects it gets as input.

    waves list of the waves object to be wrtitten to file
    filename filename of thefile to be produced
    """
    

    n_samples = 0    

    for w in waves:
        n_samples = n_samples + w.samples.size
  
    wsamples = np.zeros(n_samples)
  
    t_ind = 0
    for w in waves:
        wsamples[t_ind:t_ind+w.n_samples] = w.samples
        t_ind = w.n_samples
    
    np.savetxt(filename, wsamples, delimiter=' ')
