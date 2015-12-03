#!/usr/bin/env python3
"""
plots integrated ISR power over altitude range on top of HiST image stream

Michael Hirsch
"""
from __future__ import division, absolute_import
from matplotlib.pyplot import show
#
from isrutils.overlayISRopt import overlayisrhist
from isrutils.common import boilerplateapi

if __name__ == '__main__':

    p,isrfn,odir,tlim = boilerplateapi()

    overlayisrhist(isrfn,odir,tlim,p.zlim,p)

    show()