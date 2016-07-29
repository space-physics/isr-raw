#!/usr/bin/env python
from isrutils.looper import simpleloop
#%% users param
P={
'path':'~/data/2013-04-14/isr',
'makeplot': [],
'beamid': 64157,
'acf': True,
'vlimacf': (20,50),
'zlim_pl': [None,None],
'vlim_pl': [75,95],
'flim_pl': [3.5,5.5],
'odir': 'out/2013-04-14T0824',
'vlim': [30, 60],
'zlim': (90, None),
'tlim': ('2013-04-14T08:23Z',
         '2013-04-14T08:36Z'),
'tmark':[],
'verbose': True,
}
#%%

flist=('d0346832.dt3.h5',
       'd0346832.dt1.h5'
       #'d0346832.dt0.h5'
       )

simpleloop(flist,P)