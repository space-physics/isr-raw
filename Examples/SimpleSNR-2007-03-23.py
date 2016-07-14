#!/usr/bin/env python
"""
Akbari GRL 2012: Anomalous ISR echoes preceding auroral breakup: Evidence for strong Langmuir turbulence  doi:10.1029/2011GL050288

"""
from datetime import datetime
from pytz import UTC
from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.5)
#
from isrutils.looper import simpleloop
#%% users param
P={'path':'~/data/2007-03-23/isr',
   'makeplot': [],
   'beamid': 64157,
   'acf': True,
   'vlimacf': (20,50),
   'int': True,
   'samples': True,
   'odir': '',#'out/2007-03-23',
   'zlim_pl': 230.,
   'vlim': [35,65],
   'zlim': (90, 400),
   'tlim': (datetime(2007,3,23,11,20,0,tzinfo=UTC),datetime(2007,3,23,11,20,30,tzinfo=UTC)),
  }
#%% iterate over list. Files are ID'd by file extension (See README.rst)
flist = [
        'd0019275.dt0.h5', #ion alt
        #'d0019275.dt1.h5', #plasma
        #'d0019275.dt3.h5'   #ion long
        ]

simpleloop(flist,P)

show()
