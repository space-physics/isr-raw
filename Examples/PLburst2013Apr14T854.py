#!/usr/bin/env python
"""
For a particular event, shows the plasma line bursts

"""
from pathlib import Path
from tempfile import gettempdir
from datetime import datetime
from pytz import UTC
# github.com/scivision/isrutils
from isrutils.plasmaline import readplasmaline,plotplasmaline

stem = Path('~/data/2013-04-14/ISR/d0346834').expanduser()
vlim = (70,100)
tlim = (datetime(2013,4,14,8,54,10,tzinfo=UTC),
        datetime(2013,4,14,8,54,50,tzinfo=UTC))
zlim = (None,None)
odir = Path(gettempdir()) / 'plplot'

beamid = 64157

spec,freq = readplasmaline(stem,beamid,tlim)
plotplasmaline(spec,freq,stem,tlim,vlim=vlim,zlim=zlim,makeplot=['png'],odir=odir)
