#!/usr/bin/env python
from pathlib import Path
#
import matplotlib
matplotlib.use('agg') # NOTE comment out this line to enable visible plots
#
from . import  str2dt
from .plasmaline import readplasmaline#,plotplasmaline
from .summed import sumionline,dojointplot
from .snrpower import readpower_samples
#
from GeoData.utilityfuncs import readNeoCMOS
#
heightkm=110.
#
def overlayisrhist(P):
    """
    1) read ISR plasma line
    2) read ISR long pulse
    3) sum over power from in NEIAL altitude range
    4) load HiST video
    5) register ISR to HST
    6) plot overlay joint data
    """
    if P['optfn'] and P['azelfn']:
        optfn = Path(P['optfn']).expanduser()
        azelfn = Path(P['azelfn']).expanduser()
    else:
        optfn = azelfn = None

    P['tlim'] = str2dt(P['tlim'])
#%% (1) read ISR plasma line
#    plsum = sumplasmaline(isrfn,p.beamid,p.flim,tlim,zlim)
#    plotsumplasmaline(plsum)
    spec,freq = readplasmaline(P['isrfn'],P)
    #plotplasmaline(spec,freq,isrfn,P)
#%% (2-3) read ISR long pulse
    snrsamp,beamazel,isrlla = readpower_samples(P['isrfn'],P)
    lpsum = sumionline(snrsamp,P)
#%% (4) load optical data
    if optfn is not None:
        #hst = []; hstazel=[]; hstlla=[]; hstut=[]
        opt, _, optazel, optlla, optut = readNeoCMOS(optfn,azelfn, treq=P['tlim'])[:5]
        #hst.append(opt['optical']); hstazel.append(optazel)
        #hstlla.append(optlla); hstut.append(optut)
        optdat = opt['optical']
    else:
        optdat=optazel=optlla=optut=None
#%% (5) transform magnetic zenith PFISR to HiST frame, assuming single altitude
    # now this happens inside do joint plot
#%% (6) plot joint
    dojointplot(lpsum,spec,freq,beamazel,optdat,optazel,optlla,isrlla, heightkm,optut,P)
