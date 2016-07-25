#!/usr/bin/env python
from copy import deepcopy
#
import matplotlib
matplotlib.use('agg') # NOTE comment out this line to enable visible plots
from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.5)
sns.set_style('ticks')
#
from . import Path
from .common import ftype
from .switchyard import isrselect
from .plots import plotsnr,plotplasmaline

def simpleloop(flist,P):

    if not 'odir' in P:
        P['odir'] = None

    if not 'makeplot' in P:
        P['makeplot'] = []

    Pint = deepcopy(P) # copy does not work, deepcopy works
    if Pint['vlim'][0] is not None: Pint['vlim'][0] = Pint['vlim'][0] + 30
    if Pint['vlim'][1] is not None: Pint['vlim'][1] = Pint['vlim'][1] + 30

    ax = {}
    for f in flist:
        ft = ftype(f)
        ax[ft] = {}
        specdown,specup,snrsamp,azel,isrlla,snrint,snr30int = isrselect(Path(P['path'])/f, P)
        # 15 sec integration
        ax[ft]['snrint'] = plotsnr(snrint,f,Pint)
        # 200 ms integration
        ax[ft]['snrraw'] = plotsnr(snrsamp,f,P)

#%% plasma line spectrum
        plotplasmaline(specdown,specup,f,P)
#%% ACF
    show()
