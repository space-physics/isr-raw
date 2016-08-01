#!/usr/bin/env python
from isrutils.looper import simpleloop
#%% users param
P={
'path':'~/data/2015-10-07/isr',
'makeplot': [],
'beamid': 64157,
'acf': True,
'vlimacf': (18,45),
'zlim_pl': [None,None],
'vlim_pl': [72,90],
'flim_pl': [3.5,5.5],
'odir': 'out/2015-10-07',
'vlim': [25, 55],
'zlim': (90, None),
'verbose': True,
}
#%%

flist=(
       )

simpleloop(flist,P)