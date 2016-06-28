#!/usr/bin/env python
"""
2013-04-14 08:54 UT event
"""
from isrutils import Path
from tempfile import gettempdir
from datetime import datetime
from pytz import UTC
from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.5)
#
from isrutils.switchyard import isrselect
from isrutils.plots import plotsnr
#%%
path = Path('~/data/2013-04-14/ISR')
zlim=(90, 400)
tlim=(datetime(2013,4,14,8,54,10,tzinfo=UTC),
      datetime(2013,4,14,8,54,50,tzinfo=UTC))

tlim2=(datetime(2013,4,14,8,tzinfo=UTC),
      datetime(2013,4,14,9,tzinfo=UTC))

t0 = None#datetime(2013,4,14,8,54,tzinfo=UTC)

odir = gettempdir()

beamid = 64157
vlim=None
showacf=False
showsamples=True
makeplot=('show')

#%% long pulse 234ms and 12ms power plots
isrfn = path/'d0346834.dt3.h5'
spec,freq,snrsamp,azel,isrlla,snrint,snr30int = isrselect(
        isrfn,beamid,tlim,zlim,t0,showacf,showsamples)
plotsnr(snrint,isrfn,tlim)
#%% alternating code 234ms and 12ms power plots
isrfn = path/'d0346834.dt0.h5'
spec,freq,snrsamp,azel,isrlla,snrint,snr30int = isrselect(
        isrfn,beamid,tlim,zlim,t0,showacf,showsamples)
plotsnr(snrint,isrfn,tlim)
#%% alt code 30 sec
#spec,freq,snrsamp,azel,isrlla,snrint,snr30int = isrselect(
#        path/'20130413.001_ac_30sec.h5',beamid,tlim2,zlim,t0,showacf,showsamples)
# long pulse 30 sec
#spec,freq,snrsamp,azel,isrlla,snrint,snr30int = isrselect(
#        path/'20130413.001_lp_30sec.h5',beamid,tlim2,zlim,t0,showacf,showsamples)

show()
