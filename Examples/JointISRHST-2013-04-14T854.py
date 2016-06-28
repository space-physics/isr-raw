#!/usr/bin/env python
"""
plots integrated ISR power over altitude range on top of HiST image stream
"""
from isrutils import Path
from collections import namedtuple
from matplotlib.pyplot import show
from pytz import UTC
from datetime import datetime
from tempfile import gettempdir
#
from isrutils.overlayISRopt import overlayisrhist

isrfn='~/data/2013-04-14/ISR/d0346834.dt3.h5'
zlim=(200, 350)
tlim=(datetime(2013,4,14,8,54,10,tzinfo=UTC),
      datetime(2013,4,14,8,54,50,tzinfo=UTC))
odir = Path(gettempdir()) / (str(tlim[0])+'.mkv')

P = namedtuple('a',['azelfn','optfn','makeplot'])

P.azelfn='~/code/histfeas/precompute/hst0cal.h5'
P.optfn ='~/data/2013-04-14/HST/2013-04-14T8-54_hst0.h5'
P.makeplot=('png')
P.beamid = 64157


overlayisrhist(isrfn,odir,tlim,zlim,P)

show()