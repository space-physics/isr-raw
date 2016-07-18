#!/usr/bin/env python
"""
2013-04-14 08:54:54 UT event
"""
from datetime import datetime
from pytz import UTC
from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.5)
sns.set_style('ticks')
#
from isrutils.looper import simpleloop
#%% users param


P={'path':'~/data/2013-04-14/isr',
   'makeplot': [],
   'beamid': 64157,
   'acf': False,
   'vlimacf': (20,50),
   'zlim_pl': [None,None],
   'vlim_pl': [None,None],
   'flim_pl': [None,None],
   'int': False,
   'samples': True,
   'odir': 'out/2013-04-14',
   'vlim': [30, 60],
   'zlim': (90, None),
   'tlim': (datetime(2013,4,14,8,54,0,tzinfo=UTC),
            datetime(2013,4,14,8,54,50,tzinfo=UTC)),
   'tmark':[],
#   'tmark': [(datetime(2013,4,14,8,54,30,tzinfo=UTC),300.,'onset',-1),
#             (datetime(2013,4,14,8,54,41,tzinfo=UTC),300.,'quiescence',1)]
  }
#%% iterate over list. Files are ID'd by file extension (See README.rst)
flist = (
'd0346834.dt3.h5', # 480 us long pulse
#'d0346834.dt1.h5',
#'d0346834.dt0.h5', #alt code

#'20130413.001_ac_30sec.h5',
#'20130413.001_lp_30sec.h5'
)

ax = simpleloop(flist,P)

show()
