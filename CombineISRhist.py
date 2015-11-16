#!/usr/bin/env python3
"""
plots integrated ISR power over altitude range on top of HiST image stream

Michael Hirsch
"""
from __future__ import division, absolute_import
from six import integer_types
from pathlib2 import Path
from matplotlib.pyplot import show
from datetime import datetime
from pytz import UTC
#
from isrutils.common import boilerplateapi,ftype,projectisrhist
from isrutils.summed import *
from GeoData.utilityfuncs import readNeoCMOS
#
heightkm=110.
epoch = datetime(1970,1,1,tzinfo=UTC)
#
def overlayisrhist(isrfn,odir,tlim,zlim,P):
    """
    0) read ISR raw data
    1) sum over power from in NEIAL altitude range
    2) plot over HiST video
    """
    assert isinstance(isrfn,Path)
    assert isinstance(zlim[0],(float,integer_types))
    ft = ftype(isrfn)
    optfn = Path(P.optfn).expanduser()
    azelfn = Path(P.azelfn).expanduser()
#%% (0,1) read ISR, select power sum
    if ft in ('dt1','dt2'):
        dsum = sumplasmaline(isrfn,p.beamid,p.flim,tlim,zlim)
        plotsumplasmaline(dsum)
    elif ft in ('dt3',):
        dsum,beamazel,isrlla = sumlongpulse(isrfn,p.beamid,tlim,zlim)
#%% (2) load optical data
    utlim = [(l-epoch).total_seconds() for l in tlim]
    optical, coordnames, optazel, optlla, utopt,descr = readNeoCMOS(
                                                                  str(optfn),
                                                                  str(azelfn),
                                                                    treq=utlim)

#%% (3) transform magnetic zenith PFISR to HiST frame, assuming single altitude
    optisrazel = projectisrhist(isrlla,beamazel,optlla,optazel,heightkm)
#%% (4) plot joint
    dojointplot(dsum,beamazel,optical['optical'],coordnames,optazel,optlla,optisrazel,
                utopt,utlim,P.makeplot)



if __name__ == '__main__':
    p,isrfn,odir,tlim = boilerplateapi()

    overlayisrhist(isrfn,odir,tlim,p.zlim,p)

    show()