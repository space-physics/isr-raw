#!/usr/bin/env python
"""
"""
from isrutils import Path
from datetime import datetime
from pytz import UTC
from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.5)
#
from isrutils.looper import simpleloop
#%% users param
P={'path':'~/data/2007-03-23',
   'makeplot': [],
   'beamid': 64157,
   'acf': False,
   'vlimacf': (20,50),
   'samples': False,
   'odir': 'out/acf',
   'zlim_pl': 230.,
   'vlim': (None,None),
   'zlim': (90, 400),
   'tlim': (None,datetime(2007,3,23,11,11,30,tzinfo=UTC)),
  }
#%% iterate over list. Files are ID'd by file extension (See README.rst)
flist = sorted(Path(P['path']).expanduser().glob('*.dt*.h5'))

simpleloop(flist,P)

show()
