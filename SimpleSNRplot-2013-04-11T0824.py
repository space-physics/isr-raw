#!/usr/bin/env python3
"""
reading PFISR data down to IQ samples

See README.rst for the data types this file handles.
"""
from tempfile import gettempdir
from datetime import datetime
from pytz import UTC
from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.5)
#
from isrutils.switchyard import isrselect
#%%
path = '~/Dropbox/aurora_data/StudyEvents/2013-04-14/ISR/'
zlim=(90, 400)
tlim=(datetime(2013,4,14,8,23,0,tzinfo=UTC),
      datetime(2013,4,14,8,36,0,tzinfo=UTC))
isrfn2a= path+'20130413.001_ac_30sec.h5'
isrfn2l= path+'20130413.001_lp_30sec.h5'
tlim2=(datetime(2013,4,14,8,tzinfo=UTC),
      datetime(2013,4,14,9,tzinfo=UTC))
t0 = None#datetime(2013,4,14,8,54,tzinfo=UTC)
odir = gettempdir()
beamid = 64157
vlim=None
showacf=False
showsamples=True
makeplot=('show')
#%%
#long pulse 234ms and 12ms power plots
isrselect(path+'d0346832.dt3.h5',odir,beamid,tlim,vlim,zlim,t0,showacf,showsamples,makeplot)
#alternating code 234ms and 12ms power plots
isrselect(path+'d0346832.dt0.h5',odir,beamid,tlim,vlim,zlim,t0,showacf,showsamples,makeplot)
#isrselect(isrfn2a,odir,beamid,tlim2,vlim,zlim,t0,showacf,showsamples,makeplot)
#isrselect(isrfn2l,odir,beamid,tlim2,vlim,zlim,t0,showacf,showsamples,makeplot)
show()
