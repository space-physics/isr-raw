#!/usr/bin/env python
"""
2013-04-14 08:54 UT event
"""
from isrutils.looper import simpleloop
#%% users param
P={
'path':'~/data/2013-04-14/isr',
'makeplot': [],
'beamid': 64157,
'acf': False,
'vlimacf': (20,50),
'zlim_pl': [None,None],
'vlim_pl': [72,90],
'flim_pl': [3.5,5.5],
'int': True,
'samples': True,
'odir': 'out/2013-04-14T0854',
'vlim': [30, 60],
'zlim': (90, None),
'tlim': ['2013-04-14T08:54:00Z',
         '2013-04-14T08:54:50Z'],
'verbose': True,
#   'tmark': [(datetime(2013,4,14,8,54,30,tzinfo=UTC),300.,'onset',-1),
#             (datetime(2013,4,14,8,54,41,tzinfo=UTC),300.,'quiescence',1)]
  }
#%% iterate over list. Files are ID'd by file extension (See README.rst)
flist = (
#'d0346834.dt3.h5', # 480 us long pulse
'd0346834.dt1.h5',
#'d0346834.dt0.h5', #alt code

#'20130413.001_ac_30sec.h5',
#'20130413.001_lp_30sec.h5'
)

ax = simpleloop(flist,P)
