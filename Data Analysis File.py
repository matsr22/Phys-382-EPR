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

def sinusoidal(x,A,w,phi):
      return A*math.sin(x*w+phi)

data = pd.read_excel(r"C:\Users\matth\Documents\Phys 382\EPRData.xlsx",None)
MagResonances = np.array([])
FreqResonances = np.array([])

for i, sheet in enumerate(data):

        timeData = (data[sheet]["Time"]).to_numpy()
        EPRData = (data[sheet]["EPR signal"]).to_numpy()
        MagneticData = (data[sheet]["Magnetic Signal"]).to_numpy()
        
        dataRange = (np.max(-EPRData)-np.min(-EPRData))
        t, dict = signal.find_peaks(-EPRData,height=np.max(-EPRData)-dataRange*0.2,prominence=dataRange*0.001)
        t=np.array(t)
        print(t)
        if len(MagResonances) > 0:
            MagResonances=np.append(MagResonances,MagneticData[t])
            FreqResonances=np.append(FreqResonances,([float(sheet) for i in range(len(t))]))
        else:
              MagResonances=t
              FreqResonances=([float(sheet) for i in range(len(t))])

MagResonances = MagResonances*(1.25663706212E-6)*math.pow(0.8,1.5)*(320.0/(6.7E-2))
print(MagResonances)
print(FreqResonances)

plt.scatter(MagResonances,FreqResonances,marker = ".",s=6)

plt.xlabel("Magnetic Field [mT]")
plt.ylabel("Resonance Frequency [MHz]")

plt.show()