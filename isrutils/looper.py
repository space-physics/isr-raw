#!/usr/bin/env python
from . import Path
from .switchyard import isrselect
from .plots import plotsnr

def simpleloop(flist,tlim,zlim,vlim,P):

    path = Path(P['path'])
    try:
        t0 = P['t0']
    except KeyError:
        t0 = None

    for f in flist:
        spec,freq,snrsamp,azel,isrlla,snrint,snr30int = isrselect(
            path/f, P['beamid'], tlim, zlim, t0, P['showacf'],
            P['showsamples'])
        # 15 sec integration
        plotsnr(snrint,f,tlim,vlim)
        # 200 ms integration
        plotsnr(snrsamp,f,tlim,vlim)
