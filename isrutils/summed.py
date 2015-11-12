"""
summed measurements and plots
"""
from __future__ import division,absolute_import
from pandas import Panel4D,DataFrame
from numpy import absolute
#
from isrutils.plasmaline import readplasmaline


def sumplasmaline(flim,zlim):
    spec,freq = readplasmaline(fn,p.beamid,tlim)
    assert isinstance(spec,Panel4D)
    assert isinstance(flim[0],float)

    z = spec.major_axis
    specsum = DataFrame(index=spec.items,columns=spec.labels)

    sind = (zlim[0] <= z) & (z <= zlim[1])

    for s in spec:
        find = (flim[0] <= absolute(freq[s]/1e6)) & (absolute(freq[s]/1e6) < flim[1])
        specsum.loc[:,s] = spec.loc[:,:,sind,find].sum(axis=3).sum(axis=2)

    return specsum

def plotsumplasmaline(plsum):

