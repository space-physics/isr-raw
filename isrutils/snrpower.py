#!/usr/bin/env python
from six import integer_types
from . import Path
from numpy import empty,ones
import h5py
from pandas import DataFrame
#
from .common import ut2dt,findstride,sampletime

def samplepower(sampiq,bstride,Np,ut,srng,tlim,zlim):
    """
    returns I**2 + Q**2 of radar received amplitudes
    FIXME: what are sample units?

    I can't index by stride and slant range simultaneously, since h5py 2.5 says
    Only one indexing vector or array is currently allowed for advanced selection
    """
    assert sampiq.ndim == 4
    assert isinstance(zlim[0],(float,integer_types)) and isinstance(zlim[1],(float,integer_types)),'you must specify altitude summation limits --zlim'

    Nr = srng.size
    zind = (zlim[0] <= srng) & (srng <= zlim[1])
    srng = srng[zind]

    Nt = ut.size
#%% load only small bits of the hdf5 file, using advanced indexing. So fast!
    power = empty((Nr,Nt))
    for it in range(Nt//Np):
        power[:,Np*it:Np*(it+1)] = (sampiq[it,bstride,:,0]**2 +
                                    sampiq[it,bstride,:,1]**2).T
#%% NOTE: could also index by read, start with pulse batch before request and end with batch after last request.
    t = ut2dt(ut)

    tind = ones(t.size,dtype=bool)

    if tlim[0] is not None:
        tind &= tlim[0]<=t
    if tlim[1] is not None:
        tind &= t<=tlim[1]
    t = t[tind]
    power = power[:,tind]

    return DataFrame(index=srng, columns=t, data=power[zind,:])

def readpower_samples(fn,bid,zlim,tlim=(None,None)):
    """
    reads samples (lowest level data) and computes power for a particular beam.
    returns a Pandas DataFrame containing power measurements
    """
    fn=Path(fn).expanduser()
    assert isinstance(bid,integer_types) # a scalar integer!

    with h5py.File(str(fn),'r',libver='latest') as f:
#        Nt = f['/Time/UnixTime'].shape[0]
        isrlla = (f['/Site/Latitude'].value,f['/Site/Longitude'].value,f['/Site/Altitude'].value)
        Np = f['/Raw11/Raw/PulsesIntegrated'][0,0] #FIXME is this correct in general?
        ut = sampletime(f['/Time/UnixTime'],Np)
        srng  = f['/Raw11/Raw/Power/Range'].value.squeeze()/1e3
        bstride = findstride(f['/Raw11/Raw/RadacHeader/BeamCode'],bid)
        power = samplepower(f['/Raw11/Raw/Samples/Data'],bstride,Np,ut,srng,tlim,zlim) #I + jQ   # Ntimes x striped x alt x real/comp
#%% return az,el of this beam
        azelrow = f['/Setup/BeamcodeMap'][:,0] == bid
        azel = f['/Setup/BeamcodeMap'][azelrow,1:3].squeeze()

    return power,azel,isrlla

def readsnr_int(fn,bid):
    fn = Path(fn).expanduser()
    assert isinstance(bid,integer_types) # a scalar integer!

    with h5py.File(str(fn),'r',libver='latest') as f:
        t = ut2dt(f['/Time/UnixTime'].value) #yes .value is needed for .ndim
        bind  = f['/Raw11/Raw/Beamcodes'][0,:] == bid
        power = f['/Raw11/Raw/Power/Data'][:,bind,:].squeeze().T
        srng  = f['/Raw11/Raw/Power/Range'].value.squeeze()/1e3
#%% return requested beam data only
    return DataFrame(index=srng,columns=t,data=power)

def snrvtime_fit(fn,bid):
    fn = Path(fn).expanduser()

    with h5py.File(str(fn),'r',libver='latest') as f:
        t = ut2dt(f['/Time/UnixTime'].value)
        bind = f['/BeamCodes'][:,0] == bid
        snr = f['/NeFromPower/SNR'][:,bind,:].squeeze().T
        z = f['/NeFromPower/Altitude'][bind,:].squeeze()/1e3
#%% return requested beam data only
    return DataFrame(index=z,columns=t,data=snr)
