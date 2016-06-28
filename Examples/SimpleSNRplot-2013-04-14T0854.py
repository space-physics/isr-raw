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
zlim=(90, 400)
tlim=(datetime(2013,4,14,8,54,10,tzinfo=UTC),
      datetime(2013,4,14,8,54,50,tzinfo=UTC))

tlim2=(datetime(2013,4,14,8,tzinfo=UTC),
      datetime(2013,4,14,9,tzinfo=UTC))

P={'path':'~/data/2013-04-14/ISR',
   'beamid': 64157,
   't0':None, #datetime(2013,4,14,8,54,tzinfo=UTC)
   'showacf':False,
   'showsamples':True,
   'makeplot': []
  }
#%% iterate over list. Files are ID'd by file extension (See README.rst)
flist = ('d0346834.dt3.h5', #long pulse
         'd0346834.dt0.h5') #alt code

simpleloop(flist,tlim,zlim,P)
#%% 30 sec integration
flist = ('20130413.001_ac_30sec.h5',
         '20130413.001_lp_30sec.h5')

simpleloop(flist,tlim2,zlim,P)

show()
