#@title Imports
import math
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from scipy import interpolate
from scipy import stats
from scipy import signal
from scipy.optimize import curve_fit
from scipy.optimize import leastsq
from scipy.odr import ODR, Model, Data, RealData
from pylab import *
from openpyxl import Workbook

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy as scipy
from scipy import optimize
from matplotlib.ticker import AutoMinorLocator
from matplotlib import gridspec
import matplotlib.ticker as ticker

"""This program gets the time and channel 1 and 2 from the oscilliscope and writes them to an excel file:

    Put this file along with a spreadsheet named YOURNAMEHERE.xslx

"""


# Needs to be ran on a computer connected to an oscilliscope

# tbs simple plot
# python v3.x, pyvisa v1.8
# should work with TDS2k, TPS2k, and TBS1k series


import time # std module
import pyvisa # http://github.com/hgrecco/pyvisa
import pylab as pl # http://matplotlib.org/
import numpy as np # http://www.numpy.org/


def RootFind(array):
  indexes = []
  prevItem = None
  for i,element in enumerate(array):
    if (prevItem != None):
      if (np.sign(float(prevItem)) != np.sign(float(element))):
        indexes.append(i)
    prevItem = element  

visa_address = 'YOUR VISA ADDRESS HERE: e.g.   USB0::0x0699::0x03C4::C010226::INSTR' # Insert some oscilliscope ref here probably

#To obtain the visa address, go into National INstruments MAX, find the oscilliscope and copy the visa address

rm = pyvisa.ResourceManager()
scope = rm.open_resource(visa_address)
scope.timeout = 10000 # ms
scope.encoding = 'latin_1'
scope.read_termination = '\n'
scope.write_termination = None
scope.write('*cls') # clear ESR

print(scope.query('*idn?')) # Identify oscillsicope model

input("""
Configure the Oscilliscope, press enter to contintue 
""")







while (True):

  runFrequency = input("Please enter the title of this run, if you would like to stop taking data, enter x")
  if(runFrequency.lower() == "x"):
    break



  # io config
  scope.write('header 0')
  scope.write('data:encdg RIBINARY')
  scope.write('data:source CH2') # channel
  scope.write('data:start 1') # first sample
  record = int(scope.query('wfmpre:nr_pt?'))
  scope.write('data:stop {}'.format(record)) # last sample
  scope.write('wfmpre:byt_nr 1') # 1 byte per sample

  # acq config
  scope.write('acquire:state 0') # stop
  t5 = time.perf_counter()
  r = scope.query('*opc?') # sync
  t6 = time.perf_counter()
  print('acquire time: {} s'.format(t6 - t5))

  # data query
  t7 = time.perf_counter()
  bin_wave2 = scope.query_binary_values('curve?', datatype='b', container=np.array)
  vscale1 = float(scope.query('wfmpre:ymult?')) # volts / level
  voff1 = float(scope.query('wfmpre:yzero?')) # reference voltage
  vpos1 = float(scope.query('wfmpre:yoff?')) # reference position (level)

  scope.write('data:source CH1')
  bin_wave1 = scope.query_binary_values('curve?', datatype='b', container=np.array)
  vscale2 = float(scope.query('wfmpre:ymult?')) # volts / level
  voff2 = float(scope.query('wfmpre:yzero?')) # reference voltage
  vpos2 = float(scope.query('wfmpre:yoff?')) # reference position (level)
  t8 = time.perf_counter()
  print('transfer time: {} s'.format(t8 - t7))


  # retrieve scaling factors
  tscale = float(scope.query('wfmpre:xincr?'))
  tstart = float(scope.query('wfmpre:xzero?'))
  vscale = float(scope.query('wfmpre:ymult?')) # volts / level

  # error checking
  r = int(scope.query('*esr?'))
  print('event status register: 0b{:08b}'.format(r))
  r = scope.query('allev?').strip()
  print('all event messages: {}'.format(r))

  total_time = tscale * record
  tstop = tstart + total_time
  scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False)
  # vertical (voltage) - Channel 1 (EPR Signal)
  unscaled_wave1 = np.array(bin_wave1, dtype='double') # data type conversion
  scaled_wave1 = (unscaled_wave1 - vpos1) * vscale1 + voff1
  # vertical (voltage) - Channel 2 (Current)
  unscaled_wave2 = np.array(bin_wave2, dtype='double') # data type conversion
  scaled_wave2 = (unscaled_wave2 - vpos2) * vscale2 + voff2

  rawData = {'Time':scaled_time,'Signal 1':scaled_wave1,'Signal 2':scaled_wave2}
  df = pd.DataFrame(rawData)
  path = r"YOUR FILE PATH HERE.xlsx"
  with pd.ExcelWriter(path,mode='a') as writer:
    df.to_excel(writer, sheet_name=runFrequency)

    


  scope.write('acquire:state 1') # run

scope.close()
rm.close()


