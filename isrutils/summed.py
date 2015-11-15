"""
summed measurements and plots
"""
from __future__ import division,absolute_import
from pandas import Panel4D,DataFrame,Series
from numpy import absolute,nan
from matplotlib.pyplot import figure,draw,pause
#import matplotlib.animation as anim
#
from .plasmaline import readplasmaline
from .common import timeticks
from .snrpower import readpower_samples

#%% joint isr optical plot
def dojointplot(ds,f1,a1,optical,coordnames,dataloc,sensorloc,utopt):
    """
    f1,a1: radar   figure,axes
    f2,a2: optical figure,axes
    """
    assert isinstance(ds,(Series,DataFrame))
#%% form optical data


#%% setup plots
    T = ds.index
    h1 = a1.axvline(nan)

    f2 = figure()
    a2 = f2.gca()
    h2 = a2.imshow(optical[0,...],origin='lower',interpolation='none',cmap='gray')
    t2 = a2.set_title('')

    for i,t in enumerate(T):
#%% update isr plot
        h1.set_xdata(t)
#%% update hist plot
        h2.set_data(optical[i,...])
        h2.set_label('{}'.format(t))
#%% anim
        draw(); pause(0.01)
#
#    def update(t):
#        h.set_xdata(t)
#        return h,
#
#    line_ani = anim.FuncAnimation(fig=f1, func=update, frames=T.size,
#                                   interval=50, blit=False)

#%% dt3
def sumlongpulse(fn,beamid,tlim,zlim):
    snrsamp = readpower_samples(fn,beamid,tlim,zlim)
    assert isinstance(snrsamp,DataFrame)

    return snrsamp.sum(axis=0)

def plotsumlongpulse(dsum):
    assert isinstance(dsum,Series)
    fg = figure()
    ax = fg.gca()

    dsum.plot(ax=ax)
    ax.set_ylabel('summed power')
    ax.set_xlabel('time [UTC]')
    ax.set_title('long pulse summed over altitude (200..350)km')

    ax.set_yscale('log')
    ax.grid(True)

    ax.xaxis.set_major_locator(timeticks(dsum.index[-1] - dsum.index[0]))
    return fg,ax

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
