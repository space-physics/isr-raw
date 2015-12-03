from pathlib2 import Path
from six import integer_types
from datetime import datetime
from pytz import UTC
from isrutils.plasmaline import readplasmaline#,plotplasmaline
from isrutils.summed import sumlongpulse,dojointplot
from GeoData.utilityfuncs import readNeoCMOS
#
heightkm=110.
epoch = datetime(1970,1,1,tzinfo=UTC)
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
    isrfn = Path(isrfn).expanduser()
    optfn = Path(P.optfn).expanduser()
    azelfn = Path(P.azelfn).expanduser()
    assert isinstance(zlim[0],(float,integer_types))

#%% (1) read ISR plasma line
#    plsum = sumplasmaline(isrfn,p.beamid,p.flim,tlim,zlim)
#    plotsumplasmaline(plsum)
    spec,freq = readplasmaline(isrfn,P.beamid,tlim)
    #plotplasmaline(spec,freq,isrfn)
#%% (2-3) read ISR long pulse
    lpsum,beamazel,isrlla = sumlongpulse(isrfn,P.beamid,tlim,zlim)
#%% (4) load optical data
    utlim = [(l-epoch).total_seconds() for l in tlim]

    #hst = []; hstazel=[]; hstlla=[]; hstut=[]
    opt, _, optazel, optlla, optut,_ = readNeoCMOS(str(optfn),str(azelfn),treq=utlim)
    #hst.append(opt['optical']); hstazel.append(optazel)
    #hstlla.append(optlla); hstut.append(optut)
#%% (5) transform magnetic zenith PFISR to HiST frame, assuming single altitude
    # now this happens inside do joint plot
#%% (6) plot joint
    dojointplot(lpsum,spec,freq,beamazel,opt['optical'],optazel,optlla,isrlla,
                heightkm,optut,utlim,P.makeplot,P.odir)