#!/usr/bin/env python
from six import integer_types
from . import Path,ut2dt,cliptlim,filekey
from numpy import ones
import h5py
from xarray import DataArray
#
from .common import findstride,sampletime,getazel
from .plots import plotbeampattern

def samplepower(sampiq,bstride,ut,srng,P):
    """
    returns I**2 + Q**2 of radar received amplitudes
    FIXME: what are sample units?

    speed up indexing by downselecting by altitude, then time
    """
    assert sampiq.ndim == 4
    assert bstride.ndim== 2 and sampiq.shape[:2] == bstride.shape and bstride.dtype==bool
    zlim = P['zlim']
#%% filter by range
    Nr = srng.size
    zind = ones(Nr,dtype=bool)
    if zlim[0] is not None:
        zind &= zlim[0]<=srng
    if zlim[1] is not None:
        zind &= srng<=zlim[1]
    srng = srng[zind]
#%% filter by time
    t = ut2dt(ut)

    t,tind = cliptlim(t,P['tlim'])

    sampiq = sampiq.value[bstride,:,:]
    sampiq = sampiq[:,zind,:]
    sampiq = sampiq[tind,:,:]
    power = (sampiq[...,0]**2. + sampiq[...,1]**2.).T


    return DataArray(data=power,
                     dims=['srng','time'],
                     coords={'srng':srng,'time':t})

def readpower_samples(fn,P):
    """
    reads samples (lowest level data) and computes power for a particular beam.
    returns power measurements
    """
    fn=Path(fn).expanduser()
    assert isinstance(P['beamid'],integer_types),'beam specification must be a scalar integer!'

    try:
      with h5py.File(str(fn),'r',libver='latest') as f:
        isrlla = (f['/Site/Latitude'].value,f['/Site/Longitude'].value,f['/Site/Altitude'].value)
        azel = getazel(f,P['beamid'])

        rawkey = filekey(f)
        try:
            bstride = findstride(f[rawkey+'/RadacHeader/BeamCode'],P['beamid'])
            ut = sampletime(f[rawkey+'/RadacHeader/RadacTime'],bstride)
            plotbeampattern(f,P,f[rawkey+'/RadacHeader/BeamCode'])
        except KeyError:
            bstride = findstride(f['/RadacHeader/BeamCode'],P['beamid']) # old 2007 DT3 files (DT0 2007 didn't have raw data?)
            ut = sampletime(f['/RadacHeader/RadacTime'],bstride)
            plotbeampattern(f,P,f['/RadacHeader/BeamCode'])

        srng  = f[rawkey+'/Power/Range'].value.squeeze()/1e3

        try:
            power = samplepower(f[rawkey+'/Samples/Data'],bstride,ut,srng,P) #I + jQ   # Ntimes x striped x alt x real/comp
        except KeyError:
            return None,azel,isrlla
    except OSError as e: #problem with file
        print('{} OSError when reading: \n {}'.format(fn,e))
        return None,azel,isrlla
    except KeyError as e:
        print('raw pulse data not found {} \n {}'.format(fn,e))
        return None,azel,isrlla

    return power,azel,isrlla

def readsnr_int(fn,bid):
    fn = Path(fn).expanduser()
    assert isinstance(bid,integer_types),'beam specification must be a scalar integer!'

    try:
        with h5py.File(str(fn),'r',libver='latest') as f:
            t = ut2dt(f['/Time/UnixTime'].value) #yes .value is needed for .ndim
            rawkey = filekey(f)
            try:
                bind  = f[rawkey+'/Beamcodes'][0,:] == bid
                power = f[rawkey+'/Power/Data'][:,bind,:].squeeze().T
            except KeyError:
                power = f[rawkey+'/Power/Data'].value.T

            srng  = f[rawkey+'/Power/Range'].value.squeeze()/1e3
    except KeyError as e:
        print('integrated pulse data not found {}  {}'.format(fn,e))
        return
#%% return requested beam data only
    return DataArray(data=power, dims=['srng','time'], coords={'srng':srng,'time':t})

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
