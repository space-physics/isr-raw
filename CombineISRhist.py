#!/usr/bin/env python3
"""
plots integrated ISR power over altitude range on top of HiST image stream

Michael Hirsch
"""
from __future__ import division, absolute_import
from pathlib2 import Path
from matplotlib.pyplot import show
#
from isrutils.common import boilerplateapi,ftype
from isrutils.summed import *

def overlayisrhist(fn,odir,tlim,zlim,p):
    """
    0) read ISR raw data
    1) sum over power from in NEIAL altitude range
    2) plot over HiST video
    """
    assert isinstance(fn,Path)
    assert isinstance(zlim[0],float)
    ft = ftype(fn)
#%% (0) read ISR, select power sum
    if ft in ('dt1','dt2'):
        plsum = sumplasmaline(fn,p.beamid,p.flim,tlim,zlim)
        plotsumplasmaline(plsum)
    elif ft in ('dt3',):
        lpsum = sumlongpulse(fn,p.beamid,tlim,zlim)
        plotsumlongpulse(lpsum,tlim)



if __name__ == '__main__':
    p,fn,odir,tlim = boilerplateapi()

    overlayisrhist(fn,odir,tlim,p.zlim,p)

    show()