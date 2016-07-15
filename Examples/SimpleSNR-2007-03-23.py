#!/usr/bin/env python
"""
Akbari GRL 2012: Anomalous ISR echoes preceding auroral breakup: Evidence for strong Langmuir turbulence  doi:10.1029/2011GL050288
 - used only PFISR magnetic zenith beam
 - 2007-03-23T11:20:00 - 11:20:50 UTC
 - ion line channel of long pulse (d0019275.dt3.h5)
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
P={'path':'~/data/2007-03-23/isr',
   'makeplot': [],
   'beamid': 64157,
   'acf': False,
   'vlimacf': (25,50),
   'int': False,
   'samples': True,
   'odir': 'out/2007-03-23',
  'zlim_pl': [None,400],
  'vlim_pl': [None,90], # FIXME different scale for up and down shift
 #  'zlim_pl': 230.,
 #  'vlim_pl': [71,78,0,-13], #last two numbers are offsets
   'flim_pl': [4.45,4.8], # [MHz] #FIXME slightly different freq. scale than Akbari 2012--how to determine correct scale? Email/word of mouth or? RX/frequency in HDF5 is blank for these files, is used in new 2013 files.
   'vlim': [35,65],
   'zlim': (90, None),
   'tlim': (datetime(2007,3,23,11,20,0,tzinfo=UTC),
            datetime(2007,3,23,11,20,50,tzinfo=UTC)),
  }
#%% iterate over list. Files are ID'd by file extension (See README.rst)
flist = [
        'd0019275.dt0.h5', #ion line of alt code
        'd0019275.dt1.h5', #plasma
        'd0019275.dt3.h5' # ion line of long pulse
        ]

simpleloop(flist,P)

show()
