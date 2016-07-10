#!/usr/bin/env python
from six import integer_types
from . import Path
from numpy import empty,ones
import h5py
from xarray import DataArray
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

    Nr = srng.size

    zind = ones(Nr,dtype=bool)
    if zlim[0] is not None:
        zind &= zlim[0]<=srng
    if zlim[1] is not None:
        zind &= srng<=zlim[1]
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
    power = power[zind,:]

    #return DataFrame(index=srng, columns=t, data=power[zind,:])
    return DataArray(data=power,
                     dims=['srng','time'],
                     coords={'srng':srng,'time':t})

def readpower_samples(fn,bid,zlim,tlim=(None,None)):
    """
    reads samples (lowest level data) and computes power for a particular beam.
    returns a Pandas DataFrame containing power measurements
    """
    fn=Path(fn).expanduser()
    assert isinstance(bid,integer_types),'beam specification must be a scalar integer!'

    try:
      with h5py.File(str(fn),'r',libver='latest') as f:
#        Nt = f['/Time/UnixTime'].shape[0]
        isrlla = (f['/Site/Latitude'].value,f['/Site/Longitude'].value,f['/Site/Altitude'].value)

        rawkey = _filekey(f)
        Np = f[rawkey+'/PulsesIntegrated'][0,0] #FIXME is this correct in general?
        ut = sampletime(f['/Time/UnixTime'],Np)
        srng  = f[rawkey+'/Power/Range'].value.squeeze()/1e3
        bstride = findstride(f[rawkey+'/RadacHeader/BeamCode'],bid)
        power = samplepower(f[rawkey+'/Samples/Data'],bstride,Np,ut,srng,tlim,zlim) #I + jQ   # Ntimes x striped x alt x real/comp
#%% return az,el of this beam
        azelrow = f['/Setup/BeamcodeMap'][:,0] == bid
        azel = f['/Setup/BeamcodeMap'][azelrow,1:3].squeeze()
    except OSError as e: #problem with file
        print('{} reading error {}'.format(fn,e))
        return (None,)*3
    except KeyError as e:
        print('raw pulse data not found {}  {}'.format(fn,e))

    return power,azel,isrlla

def readsnr_int(fn,bid):
    fn = Path(fn).expanduser()
    assert isinstance(bid,integer_types),'beam specification must be a scalar integer!'

    try:
      with h5py.File(str(fn),'r',libver='latest') as f:
        t = ut2dt(f['/Time/UnixTime'].value) #yes .value is needed for .ndim
        rawkey = _filekey(f)
        bind  = f[rawkey+'/Beamcodes'][0,:] == bid
        power = f[rawkey+'/Power/Data'][:,bind,:].squeeze().T
        srng  = f[rawkey+'/Power/Range'].value.squeeze()/1e3
    except KeyError as e:
      print('integrated pulse data not found {}  {}'.format(fn,e))
      return
#%% return requested beam data only
    return DataArray(data=power,
                     dims=['srng','time'],
                     coords={'srng':srng,'time':t})

def _filekey(f):
    # detect old and new HDF5 AMISR files -- 2011: old. 2013: new.
    if '/Raw11/Raw/PulsesIntegrated' in f: #new
        return '/Raw11/Raw'
    elif '/Raw11/RawData/PulsesIntegrated' in f: #old
        return '/Raw11/RawData'
    elif '/S/Data/PulsesIntegrated' in f:
        return '/S/Data'
    else:
        raise KeyError('not an old or new file?')

def snrvtime_fit(fn,bid):
    fn = Path(fn).expanduser()

    with h5py.File(str(fn),'r',libver='latest') as f:
        t = ut2dt(f['/Time/UnixTime'].value)
        bind = f['/BeamCodes'][:,0] == bid
        snr = f['/NeFromPower/SNR'][:,bind,:].squeeze().T
        z = f['/NeFromPower/Altitude'][bind,:].squeeze()/1e3
#%% return requested beam data only
        return DataArray(data=snr,
                         dims=['alt','time'],
                         coords={'alt':z,'time':t})
