#!/usr/bin/env python
"""
2011-03-01 10:06
d0245964 (quiescent)
d0245965 10:04:40-10:05:47 (F-region turb)
d0245966 10:05:47-10:06:53 (heavy E/F-region turb)
d0245967 F-region turb
d0245968 one tick of F-region turb @ 10:08:30
d0245969 F-region turb long-pulse only 10:09
d0245970 375km turb 10:10:53
d0245971 quiescent
d0245972 quiescent
"""
from datetime import datetime
from pytz import UTC
from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.5)
#
from isrutils.looper import simpleloop
#%% users param
vlim=(22,55)
zlim=(90, 400)
#tlim=(datetime(2011,3,1,10,6,tzinfo=UTC),
#      datetime(2013,3,1,10,7,tzinfo=UTC))
tlim=(None,None)


P={'path':'c:/data/2011-03-01/isr',
   'beamid': 64157,
   'showacf':False,
   'showsamples':True,
  }
#%% iterate over list. Files are ID'd by file extension (See README.rst)
flist = (
#'d0245965.dt3.h5',
#'d0245965.dt0.h5',
#'d0245966.dt3.h5',
#'d0245966.dt0.h5',
#'d0245967.dt3.h5',
#'d0245967.dt0.h5',
#'d0245968.dt3.h5',
#'d0245968.dt0.h5',
#'d0245969.dt3.h5',
#'d0245969.dt0.h5',
#'d0245970.dt3.h5',
#'d0245970.dt0.h5',
#'d0245971.dt3.h5',
#'d0245971.dt0.h5',
'd0245972.dt3.h5',
'd0245972.dt0.h5')

simpleloop(flist,tlim,zlim,vlim,P)

show()
