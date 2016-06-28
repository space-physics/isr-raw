#!/usr/bin/env python
"""
2013-05-01
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
zlim=(90, 400)
#tlim=(datetime(2013,5,1,tzinfo=UTC),
#      datetime(2013,5,1,tzinfo=UTC))
tlim=(None,None)


P={'path':'~/data/2013-05-01/isr',
   'beamid': 64157,
   'showacf':False,
   'showsamples':True,
  }
#%% iterate over list. Files are ID'd by file extension (See README.rst)
flist = ('d0346527.dt3.h5', #long pulse
         'd0346527.dt0.h5') #alt code

simpleloop(flist,tlim,zlim,P)

show()
