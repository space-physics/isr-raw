#!/usr/bin/env python
from isrutils.looper import simpleloop
#%% users param
P={
'path':'~/data/2013-05-01/isr',
'beamid': 64157,
'acf': False,
'vlimacf': (18,45),
'zlim_pl': [None,None],
'vlim_pl': [72,90],
'flim_pl': [3.5,5.5],
'odir': 'out/2013-05-01',
'vlim': [25, 55],
'zlim': (90, None), # overall data range to READ
'zsum': (200,350), # slant range to sum over for sum plots and detection
'verbose': True,
'scan': True, #looking for turbulence
}
#%% iterate over list. Files are ID'd by file extension (See README.rst)
#flist = ( #long pulse
#         'd0349102.dt0.h5',  ) #alt code
##flist = ('d0349104.dt0.h5', #long pulse
##         'd0349104.dt3.h5' ) #alt code

simpleloop('*.dt3.h5',P)
