#!/usr/bin/env python
from .switchyard import isrselect
from .plots import plotsnr

def simpleloop(flist,tlim,zlim,P):

    for f in flist:
        spec,freq,snrsamp,azel,isrlla,snrint,snr30int = isrselect(
            P['path']/f,P['beamid'],tlim,zlim,P['t0'],P['showacf'],P['showsamples'])
        # 15 sec integration
        plotsnr(snrint,f,tlim)
        # 200 ms integration
        plotsnr(snrsamp,f,tlim)