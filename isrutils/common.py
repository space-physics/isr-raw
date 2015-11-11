from numpy import array,nonzero
from datetime import datetime
from pytz import UTC

def ut2dt(ut):
    if ut.ndim==1:
        T=ut
    elif ut.ndim==2:
        T=ut[:,0]
    return array([datetime.fromtimestamp(t,tz=UTC) for t in T])

def findstride(beammat,bid):
    #FIXME is using just first row OK? other rows were identical for me.
#    Nt = beammat.shape[0]
#    index = empty((Nt,Np),dtype=int)
#    for i,b in enumerate(beammat):
#        index[i,:] = nonzero(b==bid)[0] #NOTE: candidate for np.s_ ?
    return nonzero(beammat[0,:]==bid)[0]

def ftype(fn):
    return fn.name.split('.')[1]

def _expfn(fn):
    """
    returns text string based on file suffix
    """
    if fn.name.endswith('.dt0.h5'):
        return 'alternating code'
    elif fn.name.endswith('.dt1.h5'):
        return 'downnshifted plasma line'
    elif fn.name.endswith('.dt2.h5'):
        return 'upshifted plasma line'
    elif fn.name.endswith('.dt3.h5'):
        return 'long pulse'
