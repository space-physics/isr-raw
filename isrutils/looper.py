#!/usr/bin/env python
from . import Path
from .switchyard import isrselect
from .plots import plotsnr,plotplasmaline

def simpleloop(flist,P):

    tlim,vlim = P['tlim'],P['vlim']

    path = Path(P['path'])

    for f in flist:
        spec,freq,snrsamp,azel,isrlla,snrint,snr30int = isrselect(path/f, P['beamid'], P)
        # 15 sec integration
        plotsnr(snrint,f,tlim,vlim)
        # 200 ms integration
        plotsnr(snrsamp,f,tlim,vlim)

        # plasma line spectrum
        plotplasmaline(spec,freq,f,tlim)
