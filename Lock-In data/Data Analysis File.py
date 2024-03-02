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


data = pd.read_excel(r"C:\Users\matth\Documents\Phys 382\Lock-In data\EPR Lock-In Data.xlsx",None)
MagResonances = []
FreqResonances = []

def guassDerivative(x,a,b,c): # Where a is the height of a guass peak, b is the centre position and c is the s.d.
      return (a*(x-b)*math.pow(math.e,(-(math.pow((b-x),2))/(2*math.pow(c,2)))))/math.pow(c,2)
      


for i, sheet in enumerate(data):


        
        if "test" not in sheet.lower():
            AmpData = (data[sheet]["Amplitude"]).to_numpy()
            MagneticData = (data[sheet]["MagField"]).to_numpy()   

            maxLoc = MagneticData[np.argmax(AmpData)]
            minLoc = MagneticData[np.argmin(AmpData)]
            MagResonances.append(((minLoc-maxLoc)/2 + maxLoc))
            FreqResonances.append(float(sheet))




print(MagResonances)
print(FreqResonances)

plt.scatter(MagResonances,FreqResonances,marker = ".",s=6)

plt.xlabel("Magnetic Field [mT]")
plt.ylabel("Resonance Frequency [MHz]")

plt.show()