"""
summed measurements and plots
"""
from __future__ import division,absolute_import
from pandas import Panel4D,DataFrame
from numpy import absolute
from matplotlib.pyplot import figure
#
from .plasmaline import readplasmaline
from .common import timeticks
from .snrpower import readpower_samples

#%% dt3
def sumlongpulse(fn,beamid,tlim,zlim):
    snrsamp = readpower_samples(fn,beamid)
    assert isinstance(snrsamp,DataFrame)
    z = snrsamp.index

    zind = (zlim[0] <= z) & (z <= zlim[1])
    return snrsamp.loc[zind,:].sum(axis=0)

def plotsumlongpulse(lpsum,tlim):
    fg = figure()
    ax = fg.gca()
    lpsum.plot(ax=ax)
    ax.set_ylabel('summed power')
    ax.set_xlabel('time [UTC]')
    ax.set_title('long pluse summed over altitude (200..350)km')

    ax.set_yscale('log')
    ax.grid(True)

#%% plasma line
def sumplasmaline(fn,beamid,flim,tlim,zlim):
    spec,freq = readplasmaline(fn,beamid,tlim)
    assert isinstance(spec,Panel4D)
    assert isinstance(flim[0],float)

    z = spec.major_axis
    specsum = DataFrame(index=spec.items,columns=spec.labels)

    zind = (zlim[0] <= z) & (z <= zlim[1])

    for s in spec:
        find = (flim[0] <= absolute(freq[s]/1e6)) & (absolute(freq[s]/1e6) < flim[1])
        specsum.loc[:,s] = spec.loc[:,:,zind,find].sum(axis=3).sum(axis=2)

    return specsum

def plotsumplasmaline(plsum):
    assert isinstance(plsum,DataFrame)

    fg = figure()
    ax = fg.gca()
    plsum.plot(ax=ax)
    ax.set_ylabel('summed power')
    ax.set_xlabel('time [UTC]')
    ax.set_title('plasma line summed over altitude (200..350)km and frequency (3.5..5.5)MHz')

    ax.xaxis.set_major_locator(timeticks(plsum.columns[-1]-plsum.columns[0]))
