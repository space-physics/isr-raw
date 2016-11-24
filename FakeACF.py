#!/usr/bin/env python
"""
generate synthetic ACFs for turblent plasma scenarios
"""

from numpy import exp,arange,pi,sqrt
from matplotlib.pyplot import figure,show

f0 = [-5,5]
f = arange(-10,10,.1)

def gaussian(x,x0=0, mu=0, sig=1):
    return  1/(sig*sqrt(2*pi)) * exp(-((x-x0) - mu)** 2./(2*sig**2))

def quiet():
    psd = gaussian(f,-5) + gaussian(f,5)

    ax = figure().gca()
    ax.plot(f,psd)
    ax.set_xlabel('frequency [kHz]')
    ax.set_ylabel('amplitude [unitless]')
    ax.set_title('quiet ISR PSD')


quiet()
show()