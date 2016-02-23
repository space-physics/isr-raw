#!/usr/bin/env python3
"""
reading PFISR data down to IQ samples

See README.rst for the data types this file handles.
"""
from matplotlib.pyplot import show
#
from isrutils.common import boilerplateapi
from isrutils.switchyard import isrselect
#%%
p,isrfn,odir,tlim = boilerplateapi()
isrselect(isrfn,odir,p.beamid,tlim,p.vlim,p.zlim,p.t0,p.acf,p.samples,p.makeplot)
show()
