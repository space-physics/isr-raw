#!/usr/bin/env python
"""
2013-04-14 08:24 UT event
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
'vlim_pl': [75,95],
'flim_pl': [3.5,5.5],
'int': False,
'samples': True,
'odir': 'out/2013-04-14T1033',
'vlim': [30, 60],
'zlim': (90, None),
'tlim': (None,None),
#'tlim': ('2013-04-14T10:33Z',
#         '2013-04-14T10:41Z'),
'tmark':[],
'verbose': True,
}
#%%

flist=(#'d0346842.dt3.h5',
        'd0346842.dt1.h5',
       #'d0346842.dt0.h5',

       #'d0346843.dt3.h5',

       #'d0346844.dt3.h5',
       )

simpleloop(flist,P)