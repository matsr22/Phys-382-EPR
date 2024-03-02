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
import winsound

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy as scipy
from scipy import optimize
from matplotlib.ticker import AutoMinorLocator
from matplotlib import gridspec
import matplotlib.ticker as ticker




# Needs to be ran on a computer connected to an oscilliscope

# tbs simple plot
# python v3.x, pyvisa v1.8
# should work with TDS2k, TPS2k, and TBS1k series


import time # std module
import pyvisa # http://github.com/hgrecco/pyvisa
import pylab as pl # http://matplotlib.org/
import numpy as np # http://www.numpy.org/

#workbook = Workbook()
#sheet = workbook.active
#workbook.save(filename="EPRData.xlsx")

print("Hello World")
visa_address_scope = 'USB0::0x0699::0x03C4::C010226::INSTR' # Insert some oscilliscope ref here probably
visa_address_current = 'USB0::0x05E6::0x2200::9208344::INSTR'
rm = pyvisa.ResourceManager()
scope = rm.open_resource(visa_address_scope)

currentSource = rm.open_resource(visa_address_current)

scope.timeout = 10000 # ms
scope.encoding = 'latin_1'
scope.read_termination = '\n'
scope.write_termination = None
scope.write('*cls') # clear ESR

currentSource.encoding = 'latin_1'
currentSource.read_termination = '\n'
currentSource.write_termination = None
currentSource.write('*cls') # clear ESR

print(scope.query('*idn?')) # Identify oscillsicope model

runType = input("If this is a testing run enter t, if data collection enter d")
initalCurrent = 0
stopCurrent = 1
maxVolts = 25

if(runType == 't'):
  currentStep1=currentStep2=currentStep3 = 0.01
  currentThresh1 = currentThresh2 = currentThresh3 = currentThresh4 = initalCurrent-0.01

if(runType == 'd'):
  currentStep1 = 0.02
  currentStep2 = 0.005
  currentStep3 = 0.001
  currentThresh1 = 0.2950000000000001
  currentThresh2 = 0.37000000000000016
  currentThresh3 = 0.4200000000000002
  currentThresh4 = 0.5210000000000001


# Setting the inital vals on the current source


currentStep = currentStep1


currentCurrent = initalCurrent

print("CURR "+str(initalCurrent)+"A")
currentSource.write("OUTPUT:STATE ON")
currentSource.write("CURR "+str(initalCurrent)+"A")
currentSource.write("VOLT "+str(maxVolts)+"V")

graphDataX=[]
graphDataY=[]

runFrequency = input("Please enter the frequency of this run (In MHZ)")



while (currentCurrent<stopCurrent):

  if (runType == 'd'):
    if(currentThresh1<currentCurrent<currentThresh2):
      currentStep=currentStep2
    elif(currentThresh2<currentCurrent<currentThresh3):
      currentStep=currentStep3
    elif(currentThresh3<currentCurrent<currentThresh4):
      currentStep=currentStep2
    elif(currentCurrent>currentThresh4):
      currentStep=currentStep1


  # io config
  scope.write('header 0')
  scope.write('data:encdg RIBINARY')
  scope.write('data:source CH1') # channel
  scope.write('data:start 1') # first sample
  record = int(scope.query('wfmpre:nr_pt?'))
  scope.write('data:stop {}'.format(record)) # last sample
  scope.write('wfmpre:byt_nr 1') # 1 byte per sample

  scope.write('acquire:state 0') # stop
  scope.write('acquire:stopafter SEQUENCE') # single
  scope.write('acquire:state 1') # run

  # acq config
  #t5 = time.perf_counter()
  #r = scope.query('*opc?') # sync
  #t6 = time.perf_counter()
  #print('acquire time: {} s'.format(t6 - t5))

  # data query
  bin_wave1 = scope.query_binary_values('curve?', datatype='b', container=np.array)
  vscale1 = float(scope.query('wfmpre:ymult?')) # volts / level
  voff1 = float(scope.query('wfmpre:yzero?')) # reference voltage
  vpos1 = float(scope.query('wfmpre:yoff?')) # reference position (level)




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
  print("total oscilliscope time = " + str(total_time ))
  tstop = tstart + total_time
  scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False)
  # vertical (voltage) - Channel 1 (EPR Signal)
  unscaled_wave1 = np.array(bin_wave1, dtype='double') # data type conversion
  scaled_wave1 = (unscaled_wave1 - vpos1) * vscale1 + voff1


  avWave = np.average(scaled_wave1)
  graphDataY.append(avWave)
  magScaleFactor = 4.23
  graphDataX.append(magScaleFactor*currentCurrent)

  currentCurrent+=currentStep
  currentSource.write("CURR "+str(currentCurrent)+"A")

  time.sleep(total_time*0.4)

scope.write('data:start 1')
rawData = {'MagField':graphDataX,'Amplitude':graphDataY}
df = pd.DataFrame(rawData)
path = r"C:\Users\matth\Documents\Phys 382\Lock-In data\EPR Lock-In Data - Vary Amp Freq.xlsx"
with pd.ExcelWriter(path,mode='a') as writer:
  df.to_excel(writer, sheet_name=(runFrequency))

winsound.Beep(2500,400)
currentDatas = np.array(graphDataX)/magScaleFactor

maxLoc = currentDatas[np.argmax(graphDataY)]
minLoc = currentDatas[np.argmin(graphDataY)]
minMaxRange = minLoc - maxLoc

centre = ((minMaxRange)/2) + maxLoc # Resonance magnetic location
point1 = maxLoc - minMaxRange*1.5 
point2 = maxLoc - minMaxRange*0.2 
point3 = minLoc+minMaxRange*0.2 
point4 = minLoc + minMaxRange*1.5 


print("Centre: {}".format(centre))
print("Point 1: {}".format(point1))
print("Point 2: {}".format(point2))
print("Point 3: {}".format(point3))
print("Point 4: {}".format(point4))


plt.scatter(graphDataX,graphDataY,s=8)
plt.xlabel("Magnetic Field (mT)")
plt.ylabel("Signal")#
plt.title("Frequency: "+ str(runFrequency))
plt.savefig(str(int(time.time()))+".png")
plt.show()


    


currentSource.write("CURR "+str(0)+"A")
currentSource.close()
scope.close()
rm.close()

