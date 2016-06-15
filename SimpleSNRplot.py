#!/usr/bin/env python
"""
reading PFISR data down to IQ samples

See README.rst for the data types this file handles.
"""
from matplotlib.pyplot import show
#
from isrutils.common import boilerplateapi
from isrutils.switchyard import isrselect
from isrutils.plots import plotsnr
#%% read data
p,isrfn,odir,tlim = boilerplateapi()
spec,freq,snrsamp,azel,isrlla,snrint,snr30int = isrselect(
                        isrfn,p.beamid,tlim,p.zlim,p.t0,p.acf,p.samples)
#%% plot data
plotsnr(snrint,isrfn,tlim)

show()
