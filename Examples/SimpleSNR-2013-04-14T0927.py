#!/usr/bin/env python
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
'int': True,
'samples': False,
'odir': 'out/2013-04-14T0927',
'vlim': [30, 60],
'zlim': (90, None),
#'tlim': ('2013-04-14T10:34Z',
 #        '2013-04-14T10:36Z'),
'tmark':[],
'verbose': True,
}
#%%

flist=(#'d0346836.dt3.h5', # 9:13-9:25
       'd0346837.dt3.h5',  # 9:25-9:37
       #'d0346838.dt3.h5', # 9:37-9:50

        #'d0346837.dt1.h5',
       #'d0346842.dt0.h5',

       #'d0346843.dt3.h5',

       #'d0346844.dt3.h5',
       )

simpleloop(flist,P)