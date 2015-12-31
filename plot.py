import random as rand
import urllib2
import re
import copy as cp
import numpy as np 
import matplotlib.pyplot as plt

freq=40
plt.figure
 
#create data
x_series = [5,9,12,15,18,21]

y_series_1 = [x**2 for x in x_series]
y_series_3 = [x for x in x_series]
y_series_2 = [x for x in x_series]

mi,ma=min(y_series_1[0],y_series_2[0]),max(y_series_1[len(y_series_1)-1],y_series_2[len(y_series_2)-1])

#plot data
plt.plot( x_series , y_series_1 , label="approximate solution" )
plt.plot( x_series , y_series_2 , label="LP solution" )

plt.xlabel("number of Vms" , fontsize=25 )
plt.ylabel("host active at this stage",fontsize=25)
plt.title("",fontsize=25)
 
#add limits to the x and y axis
plt.xlim(x_series[0]-1, x_series[len(x_series)-1]+1)
plt.ylim(mi, ma) 
 
#create legend
plt.legend(loc="upper right")
 
#save figure to png
# plt.savefig("example.png")
plt.show()
