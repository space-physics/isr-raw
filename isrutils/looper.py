#!/usr/bin/env python
from copy import deepcopy
#
import matplotlib
matplotlib.use('agg') # NOTE comment out this line to enable visible plots
#from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.5)
sns.set_style('ticks')
#

from . import Path
from .common import str2dt
from .switchyard import isrselect
from .plots import plotsnr,plotplasmaline

def simpleloop(flist,P):
#%% api catchall
    if not 'odir' in P:
        P['odir'] = None

    if not 'makeplot' in P:
        P['makeplot'] = []

    if not 'tlim' in P:
        P['tlim'] = [None,None]

    Pint = deepcopy(P) # copy does not work, deepcopy works
    if Pint['vlim'][0] is not None: Pint['vlim'][0] = Pint['vlim'][0] + 15
    if Pint['vlim'][1] is not None: Pint['vlim'][1] = Pint['vlim'][1] + 15

    P['tlim'] = str2dt(P['tlim'])

#%%
   # ax = {}
    for f in flist:
      #  ft = ftype(f)
       # ax[ft] = {}
        specdown,specup,snrsamp,azel,isrlla,snrint,snr30int = isrselect(Path(P['path'])/f, P)
        # 15 sec integration
        plotsnr(snrint,f,Pint,azel)
        # 200 ms integration
        plotsnr(snrsamp,f,P,azel)
#%% plasma line spectrum
        plotplasmaline(specdown,specup,f,P,azel)

#    show()
