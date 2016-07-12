#!/usr/bin/env python
from . import Path
#
from .plasmaline import readplasmaline#,plotplasmaline
from .summed import sumlongpulse,dojointplot
#
from GeoData.utilityfuncs import readNeoCMOS
#
heightkm=110.
#
def overlayisrhist(isrfn,odir,tlim,zlim,P):
    """
    1) read ISR plasma line
    2) read ISR long pulse
    3) sum over power from in NEIAL altitude range
    4) load HiST video
    5) register ISR to HST
    6) plot overlay joint data
    """
    if P.optfn and P.azelfn:
        optfn = Path(P.optfn).expanduser()
        azelfn = Path(P.azelfn).expanduser()
    else:
        optfn = azelfn = None
#%% (1) read ISR plasma line
#    plsum = sumplasmaline(isrfn,p.beamid,p.flim,tlim,zlim)
#    plotsumplasmaline(plsum)
    spec,freq = readplasmaline(isrfn,P.beamid,tlim)
    #plotplasmaline(spec,freq,isrfn,P)
#%% (2-3) read ISR long pulse
    lpsum,beamazel,isrlla = sumlongpulse(isrfn,P.beamid,tlim,zlim)
#%% (4) load optical data
    if optfn is not None:
        utlim = [l.timestamp() for l in tlim]

        #hst = []; hstazel=[]; hstlla=[]; hstut=[]
        opt, _, optazel, optlla, optut = readNeoCMOS(optfn,azelfn,treq=utlim)[:5]
        #hst.append(opt['optical']); hstazel.append(optazel)
        #hstlla.append(optlla); hstut.append(optut)
        optdat = opt['optical']
    else:
        optdat=optazel=optlla=optut=utlim=None
#%% (5) transform magnetic zenith PFISR to HiST frame, assuming single altitude
    # now this happens inside do joint plot
#%% (6) plot joint
    dojointplot(lpsum,spec,freq,beamazel,optdat,optazel,optlla,isrlla,isrfn,zlim,
                heightkm,optut,utlim,P.makeplot,odir)