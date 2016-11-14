#!/usr/bin/env python
"""
NOTE: this date's data files has ~ half-second data gaps that pcolormesh smears horizontally
(this is in general expected pcolormesh behavior)
to quickly mitigate, plot piecewise if wider time spans are necessary.

optical/CMOS_110301_1006.avi is the companion video file

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
from isrutils.looper import simpleloop
#%% users param
P={'path':'~/data/2011-03-01/isr',
   'beamid': 64157,
   'acf': True,
   'zlim_pl': [None,None],
   'vlim_pl': [72,90],
   'flim_pl': [None,None],
   'vlim':  [30,60],
   'vlimacf': (20,50),
    'zlim': (90, None),
    'tlim': ['2011-03-01T10:06:09Z',
             '2011-03-01T10:06:22Z'],
    'tmark': [],
    'odir': 'out/2011-03-01',
  }
#%% iterate over list. Files are ID'd by file extension (See README.rst)
flist = (
#'d0245965.dt3.h5',
#'d0245965.dt0.h5',

'd0245966.dt3.h5',
#'d0245966.dt2.h5',
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
#'d0245972.dt3.h5',
#'d0245972.dt0.h5'
)
simpleloop(flist,P)

