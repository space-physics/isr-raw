#!/usr/bin/env python
"""
2013-04-11

d0346521: 10:43-10:55
d0346522: 10:55-11:07
d0345623: 11:07-11:19
d0345624: 11:19-11:31
d0345625: 11:31-11:44
d0345626: 11:44-11:56
d0345627: 11:56-12:08
"""
from datetime import datetime
from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.5)
#
from isrutils.looper import simpleloop
#%% users param
zlim=(90, 400)
zlim=(90, 400)
#tlim=(datetime(2013,4,11,11,30),
#      datetime(2013,4,11,12,0))
tlim=(None,None)


P={'path':'~/data/2013-04-11/isr',
   'beamid': 64157,
   'showacf':False,
   'showsamples':True,
  }
#%% iterate over list. Files are ID'd by file extension (See README.rst)
flist = ('d0346527.dt3.h5', #long pulse
         'd0346527.dt0.h5') #alt code

simpleloop(flist,tlim,zlim,P)

show()
