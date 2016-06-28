""" Module for generating signals according to user specifications.

The user inputs some parameters, used for generating signals
to be used in the experiments.
The waveform is then generated and sent down the cable, to the submerged node.
In parallel, signals coming from the hydrophones are passed through
an FFT to allow to discriminate them, prior to proper analysis.

Copyright 2016 UW Signet Lab, University of Padova https://signet.dei.unipd.it
License: GNU GPLv3 http://www.gnu.org/licenses/gpl.html
"""


import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import math
from scipy import signal
import wave
import os
import time
import shutil
import sys

class Signal(object):
    """ Class that defines a signal according to specs.
  
    This class is just a container for parameters of the
    signal. The creation of signal samples is obtained through a Wave object.
    """
        
    def __init__(self):
        """A Signal object basically store parameters"""


    def make_wave(self, start=0, duration=1, samplerate=96000):
        """Method that creates a Wave object from a Signal object.
    
        Args:
            start (float): start time in seconds
            duration (float): duration in seconds
            samplerate (int): samples per second

        Returns: Wave object
        """
        
        n = round(duration*samplerate)
        times = np.linspace(start, start+duration, n)
        samples = self.evaluate(times)
        return Wave(samples, times, samplerate)


class Wave(object):
    """Represents a discrete-time waveform to be written to a file."""

    def __init__(self, samples, times=None, samplerate=None):
        """Creates a Wave object.

        Args:
            samples (double ndarray): samples to be put in the Wave object
            times (ndarray double): time instants correspondignt to the samples
            samplerate (double): samplerate in Hertz
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

        Args:
            startf (float): frequency in Hertz (at time 0)
            stopf (float): frequency in Hertz (at time t1)
            t1 (float): time instant at which stopf is reached
            method (str): indicates the method ['linear','exponential']
        """
        self.startf = startf
        self.stopf = stopf
        self.t1 = t1
        self.method = method

    def evaluate(self, tsamples):
        """Evaluates the signal at the given time instants.

        Args:
            tsamples (double ndarray): time instants

        Returns: float ndarray
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

        Args:
            frequency (double): frequency in Hertz
            amplitude (double): amplitude in Volts
            offset (double): offset initial phase
        """
        self.freq = frequency
        self.amp = amplitude
        self.offset = offset

    def evaluate(self, tsamples):
        """Evaluates the signal at the given time instants.

        Args:
            tsamples (ndarray) time instants
        
        Returns (float ndarray): samples
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
        """Initialize a Rect signal.

        Args:
            duty_cycle (double): ratio of pulse duration to period
            period (double): distance between repetion of rects
            amplitude (double): amplitude in Volts
            offset (double): initial shift of the waveform
        """
        self.duty_cycle = duty_cycle
        self.period = period
        self.amplitude = amplitude
        self.offset = offset

    def evaluate(self, tsamples):
        """Evaluates the signal at the given time instants.

        tsamples: ndarray time samples
        
        returns: float ndarray
        """
        ts =  np.asarray(tsamples)
        pulse_d = self.duty_cycle * self.period
        return self.amp * ((ts + self.offset) % self.period < pulse_d)


class Recording(object):
    """ Class that handles wav files and does an initial analysis.

    Initial discrimination of signal is done by calculating the 
    spectrum of a portion of it and by by trsholding its SNR.
    """

    def __init__(self, band=[9000, 78000], th=1):
        """ Object holding data relative to file being read.

        Args:
            band (double list): the band of interest
            th (float): threshold on the spectrum SNR in dB
        """

        self.start_f = band[0] 
        self.stop_f = band[1]
        self.treshold = th
        self.noisepower = 0
        self.analyzed = []
        

    def getsamples(self, filename):

        """Obtain samples from recording filename

        Args (str): filename of the audio chunk
        Returns (float ndarray): samples of the waveform
        """

        rfile = wave.open(filename, 'r')

        #getparams output: [nchann, sampwidth, framerate, nframes, ctype, cname]
        params = rfile.getparams()
     
        # check channels
        if params[0] > 1:
            print "More than one audio channel"
            sys.exit(0)
         
        # check sample width
        datawidth = 'Int' + str(params[1]*8)
         
        # extract samples
        rstring = rfile.readframes(-1)
        rsamples = np.fromstring(rstring, datawidth)

        return rsamples


    def plotspec(self,filename):
        """Plot spectrogram of the loaded file.

        filename (str): of the audio file to be loaded
        """
     
        # open file
        rfile = wave.open(filename, 'r')

        #getparams output: [nchann, sampwidth, framerate, nframes, ctype, cname]
        params = rfile.getparams()

        # check channels
        if params[0] > 1:
            print "More than one audio channel"
            sys.exit(0)
         
        # check sample width
        datawidth = 'Int' + str(params[1]*8)
         
        # extract samples
        rstring = rfile.readframes(-1)
        rsamples = np.fromstring(rstring, datawidth)

        NFFT = 1024       # the length of the windowing segments
        Fs = params[2]    # the sampling frequency

        Pxx, freqs, bins, im = plt.specgram(rsamples, NFFT=NFFT, Fs=Fs,
                                            noverlap=256,
                                            cmap=plt.cm.gist_heat)
        plt.show()
        
        
    def analyze(self, filename):
        """Parse recordings through spectrogram

        This method makes the FFT of the file filename and treshold it.
        If the file pass the teshold test it is marked as 'sendable',
        otherwise it is discarded.

        Args:
            filename (str): string with, guess... the filename!
        Returns (int): flag indicating the result of the analysis
        """
  
        # open file
        rfile = wave.open(filename, 'r')

        #getparams output: [nchann, sampwidth, framerate, nframes, ctype, cname]
        params = rfile.getparams()
     
        # check channels
        if params[0] > 1:
            print "More than one audio channel"
            sys.exit(0)
         
        # check sample width
        datawidth = 'Int' + str(params[1]*8)
         
        # extract samples
        rstring = rfile.readframes(-1)
        rsamples = np.fromstring(rstring, datawidth)
   
        # FFT
        rsamplesFFT = np.fft.fft(rsamples)
        rsamplespower = np.linalg.norm(rsamplesFFT, 2)
        snr_dB = 10*np.log10(rsamplespower/self.noisepower)
 
        # update queue of analyzed files
        if filename in self.analyzed:
            print "File already analyzed"
        else:
            self.analyzed.append(filename)
 
        # Finally, threshold the track
        if snr_dB < self.treshold:
            #os.remove(filename)
            return 1
        else:
            return 0


    def noise_power(self, filename):
        """Parse known noise sections and retrieve power.

        This method makes the FFT of the file filename and retrieve the noise
        power. It then both updates the value and returns it.

        Args:
            filename (str): string with, guess... the filename!
        Returns (float): frequency power of the analyzed audio chunk
        """

        rfile = wave.open(filename, 'r')

        #getparams output: [nchann, sampwidth, framerate, nframes, ctype, cname]
        params = rfile.getparams()
     
        # check channels
        if params[0] > 1:
            print "More than one audio channel"
            sys.exit(0)
         
        # check sample width
        datawidth = 'Int' + str(params[1]*8)
         
        # extract samples
        rstring = rfile.readframes(-1)
        rsamples = np.fromstring(rstring, datawidth)
   
        # FFT
        rsamplesFFT = np.fft.fft(rsamples)

        rsamplespower = np.linalg.norm(rsamplesFFT, 2)

        self.noisepower = rsamplespower

        return rsamplespower


    def record_stream(self, s_time, duration, s_folder, file_ext='.wav',
                                                                chunk_d=1):
        """ Method that lets the user to analyze files in a real-time fashion.

        Files are analyzed as the are set by the node to the actual folder.
        Args:
             s_time (str): start time in format 'dd.mm.YYYY hh:mm:ss'
             duration (int): time duration of the listening phase in sec
             s_folder (str): source folder for the audio chunks
             chunk_d (double): duration of a chunk of recording in sec
        """

        # Time conversion
        #time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())    
        #s_time = '29.08.2011 11:05:02'
        pattern = '%d.%m.%Y %H:%M:%S'
        s_time_f = int(time.mktime(time.strptime(s_time, pattern)))
        wait_time = s_time_f - int(time.time())
        if wait_time < 0:
            print >> sys.stderr, 'Wrong start time for recording data stream'
            exit(0)
        else:
            print "Recording starting within "+ str(wait_time) + " seconds"
            time.sleep(wait_time)

        # Obtain absolute path
        a_path = os.path.abspath(s_folder)
   
        # Create OK folder for files that pass the threshold test
        print "Recording started"
        dirname = str(s_time_f) + "_stream"
        os.mkdir(a_path + "/" + dirname)
        
        while (time.time() < s_time_f + duration):
       
            time.sleep(chunk_d) 

            # Find out who's there
            dir_ls = os.listdir(a_path)
            files = []
            for l in dir_ls:
                if l.endswith('.wav'):
                    files.append(l)

            for f in files:

                # Absolute path of file
                filename = os.path.join(a_path, f)

                # Check if file has finished writing-off
                writing = True
                file_size = os.path.getsize(filename)
                while (writing):
                    time.sleep(0.4)
                    if file_size < os.path.getsize(filename):
                        file_size = os.path.getsize(filename)
                    else:
                        writing = False

                # Decide if chuck is good
                if not self.analyze(filename):
                    shutil.move(filename, a_path + "/" + dirname)
                else:
                    os.remove(filename)
        

def writeToWAV(waves, filename, framerate=96000, volume=60, resolution=2): 
    """Method that creates a WAV file from the Waves objects it gets as input.

    Args:
        waves (list): list with all signals that will go in the WAV file
        filename (str): string containing the filename
        volume (int): integer from 0 to 100 indicating the volume of the wav
        resolution (int): integer number of bytes encoding a sample
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

    Args:
        waves (list): list of the waves object to be wrtitten to file
        filename (str): filename of thefile to be produced
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
