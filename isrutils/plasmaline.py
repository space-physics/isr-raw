#!/usr/bin/env python
from six import integer_types
from time import time
from . import Path
import h5py
from xarray import DataArray
#
from .common import findstride,ut2dt,cliptlim,getazel

def readplasmaline(fn,P):
    """
    inputs:
    fn: d*.dt?.h5 file to load
    beamid: AMISR beam id (scalar)

    outputs:
    spec: Ntime x Nrange x Nfreq
    """
    tic = time()
    fn = Path(fn).expanduser()
    assert isinstance(P['beamid'],integer_types),'beam specification must be a scalar integer'

    #['downshift','upshift'] # by definition of dt1,dt2
    #fshift = (('dt1',-5e6),('dt2',5e6))
    FREQSHIFT = (-5e6,5e6)

#%% read downshift spectrum
    specdown,azel = readplasma(fn.parent / (fn.stem.split('.')[0] + '.dt1.h5'), P['beamid'], FREQSHIFT[0], P['tlim'])
#%% read upshift spectrum
    specup,azel =   readplasma(fn.parent / (fn.stem.split('.')[0] + '.dt2.h5'), P['beamid'], FREQSHIFT[1], P['tlim'])

    if P['verbose']:
        print('Took {:.1f} sec. to read plasma data'.format(time()-tic))

    return specdown,specup,azel

def readplasma(fn,beamid,fshift,tlim):
    try:
        with h5py.File(str(fn),'r',libver='latest') as f:
            T     = ut2dt(f['/Time/UnixTime'].value)
            bind  = findstride(f['/PLFFTS/Data/Beamcodes'], beamid)
            data = f['/PLFFTS/Data/Spectra/Data'].value[bind,:,:].T
            srng  = f['/PLFFTS/Data/Spectra/Range'].value.squeeze()/1e3
            freq  = f['/PLFFTS/Data/Spectra/Frequency'].value.squeeze() + fshift
            azel = getazel(f,beamid)
    except OSError as e: #problem with file
        print('{} reading error {}'.format(fn,e))
        return (None,)*2
#%% spectrum compute
    T,tind = cliptlim(T,tlim)

    spec = DataArray(data = data[:,:,tind].transpose(2,0,1),
                     dims=['time','srng','freq'],
                     coords={'time':T, 'srng':srng, 'freq':freq})


    return spec,azel