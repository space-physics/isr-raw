#!/usr/bin/env python
"""
2013-04-14 08:24 UT event
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
tlim=(datetime(2013,4,14,8,23,0,tzinfo=UTC),
      datetime(2013,4,14,8,36,0,tzinfo=UTC))

P={'path':'~/data/2013-04-14/ISR',
   'beamid': 64157,
   't0':None, #datetime(2013,4,14,8,54,tzinfo=UTC)
   'showacf':False,
   'showsamples':True,
   'makeplot': []
  }
#%%

flist=('d0346832.dt3.h5',
       'd0346832.dt0.h5')

simpleloop(flist,tlim,zlim,P)

show()
