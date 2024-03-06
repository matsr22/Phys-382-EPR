print(2 in range(2,0))
import time
print(int(time.time()))
import matplotlib
from matplotlib import pyplot as plt 

import numpy as np


print(np.linspace(0,10,11))

print(r"\pm")
matplotlib.use('Agg')
plt.plot([0,1,2,3],[0,1,2,3])
plt.savefig(r"C:\Users\matth\Documents\Phys 382\Lock-In data\Finalised Plots\testimage2.png",metadata = {"Description":"This is a test","Title":"Exact Title"},format = "png")