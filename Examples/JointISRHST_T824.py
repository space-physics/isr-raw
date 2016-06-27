#!/usr/bin/env python3
"""
plots integrated ISR power over altitude range on top of HiST image stream

Michael Hirsch
"""
from pathlib import Path
from collections import namedtuple
from matplotlib.pyplot import show
from pytz import UTC
from datetime import datetime
from tempfile import gettempdir
#
from isrutils.overlayISRopt import overlayisrhist

isrfn='ISR/d0346832.dt0.h5'
zlim=(120, 220)
tlim=(datetime(2013,4,14,8,28,0,tzinfo=UTC),
      datetime(2013,4,14,8,29,10,tzinfo=UTC))
odir = Path(gettempdir()) / (str(tlim[0])+'.mkv')

P = namedtuple('a',['azelfn','optfn','makeplot'])

P.azelfn='~/code/histfeas/precompute/hst0cal.h5'
P.optfn = 'HST/2013-04-14T0827-0830_hst0.h5'
P.makeplot=('png')
P.beamid = 64157


overlayisrhist(isrfn,odir,tlim,zlim,P)

show()
