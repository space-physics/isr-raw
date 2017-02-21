#!/usr/bin/env python
"""
This isn't in __init__.py due to matplotlib & seaborn imports.
"""
from pathlib import Path
from copy import deepcopy
from numpy import asarray
#
import matplotlib
matplotlib.use('agg') # NOTE comment out this line to enable visible plots
#from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.75)
sns.set_style('ticks')
#

from . import str2dt
from .switchyard import isrselect
from .rawacf import readACF
from .plots import plotsnr,plotplasmaline,plotsumionline

def simpleloop(flist, P:dict):
#%% parse user directory / file list input
    if not flist: # just a directory was specified
        flist = Path(P['path']).expanduser().glob('*dt*.h5')
    elif isinstance(flist,str):
        if flist[0] == '*' and flist.endswith('.h5'): #glob pattern
            flist = Path(P['path']).expanduser().glob(flist)
    elif isinstance(flist,(Path,str)): # a single file was specified
        flist = [flist]
    else: # a list or tuple of files was specified
        pass

    flist=sorted(flist) #in case glob
    assert len(flist)>0, f'no files found in {P["path"]}'
    print(f'examining {len(flist)} files in {P["path"]}\n')
#%% api catchall
    if not 'odir' in P:
        P['odir'] = None

    if not 'verbose' in P:
        P['verbose'] = False

    if not 'scan' in P:
        P['scan'] = False

    if not 'medthres' in P:
        P['medthres'] = 2. # N times the median is declared a detection



    if not 'tlim' in P:
        P['tlim'] = [None,None]

    for p in ('flim_pl','vlim_pl','vlim','vlimacf','vlimacfslice'):
        if p in P:
            P[p] = asarray(P[p])
        else:
            P[p] = (None,None)


    Pint = deepcopy(P) # copy does not work, deepcopy works
    if Pint['vlim'][0] is not None: Pint['vlim'][0] = Pint['vlim'][0] + 15
    if Pint['vlim'][1] is not None: Pint['vlim'][1] = Pint['vlim'][1] + 15

    P['tlim'] = str2dt(P['tlim'])
#%% loop over files
    for f in flist:
        # read data
        specdown,specup,snrsamp,azel,isrlla,snrint,snr30int,ionsum = isrselect(Path(P['path'])/f, P)
#%% plot
        # summed ion line over altitude range
        hit = plotsumionline(ionsum,None,f,P)

        if hit and not P['acf']: # if P['acf'], it was already plotted. Otherwise, we plot only if hit
            readACF(fn,P)

        if hit or not P['scan']:
            # 15 sec integration
            plotsnr(snrint,f,Pint,azel,ctxt='int_')
            # 200 ms integration
            plotsnr(snrsamp,f,P,azel)
            # plasma line spectrum
            plotplasmaline(specdown,specup,f,P,azel)
