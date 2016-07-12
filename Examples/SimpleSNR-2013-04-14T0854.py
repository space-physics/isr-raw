#!/usr/bin/env python
"""
2013-04-14 08:54:54 UT event
"""
from datetime import datetime
from pytz import UTC
from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.5)
#
from isrutils.looper import simpleloop
#%% users param


P={'path':'~/data/2013-04-14/isr',
   'makeplot': [],
   'beamid': 64157,
   'acf': False,
   'vlimacf': (20,50),
   'samples': True,
   'odir': 'out/try',
   'vlim': (22,55),
   'zlim': (90, 400),
   'tlim': (datetime(2013,4,14,8,54,10,tzinfo=UTC),
            datetime(2013,4,14,8,54,50,tzinfo=UTC)),
  }
#%% iterate over list. Files are ID'd by file extension (See README.rst)
flist = (
'd0346834.dt3.h5', #long pulse
#'d0346834.dt0.h5', #alt code
#'20130413.001_ac_30sec.h5',
#'20130413.001_lp_30sec.h5'
)

simpleloop(flist,P)

show()
