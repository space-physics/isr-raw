#!/usr/bin/env python
from copy import deepcopy
from . import Path
from .switchyard import isrselect
from .plots import plotsnr,plotplasmaline

def simpleloop(flist,P):

    if not 'odir' in P:
        P['odir'] = None

    if not 'makeplot' in P:
        P['makeplot'] = []

    Pint = deepcopy(P) # copy does not work, deepcopy works
    if Pint['vlim'][0] is not None: Pint['vlim'][0] = Pint['vlim'][0] + 30
    if Pint['vlim'][1] is not None: Pint['vlim'][1] = Pint['vlim'][1] + 30

    for f in flist:
        specdown,specup,snrsamp,azel,isrlla,snrint,snr30int = isrselect(Path(P['path'])/f, P['beamid'], P)
        # 15 sec integration
        plotsnr(snrint,f,Pint,ctxt='Power [dB]')
        # 200 ms integration
        plotsnr(snrsamp,f,P,ctxt='Power [dB]')

        # plasma line spectrum
        plotplasmaline(specdown,specup,f,P)
