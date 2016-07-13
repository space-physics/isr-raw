#!/usr/bin/env python
from . import Path
from .switchyard import isrselect
from .plots import plotsnr,plotplasmaline

def simpleloop(flist,P):

    if not 'odir' in P:
        P['odir'] = None

    if not 'makeplot' in P:
        P['makeplot'] = []

    for f in flist:
        specdown,specup,snrsamp,azel,isrlla,snrint,snr30int = isrselect(Path(P['path'])/f, P['beamid'], P)
        # 15 sec integration
        plotsnr(snrint,f,P,ctxt='Power [dB]')
        # 200 ms integration
        plotsnr(snrsamp,f,P,ctxt='Power [dB]')

        # plasma line spectrum
        plotplasmaline(specdown,specup,f,P)
