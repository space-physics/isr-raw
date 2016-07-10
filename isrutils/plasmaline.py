#!/usr/bin/env python
import logging
from six import integer_types
from pathlib import Path
from numpy import nonzero,empty
import h5py
from xarray import DataArray
#
from .common import findstride,ut2dt

def readplasmaline(fn,beamid,tlim):
    """
    inputs:
    fn: d*.dt?.h5 file to load
    beamid: AMISR beam id (scalar)

    outputs:
    spec: 4-D Panel: 2 x Ntime x Nrange x Nfreq.  1st axis is down-,up-shift index
    Freq: 2-D DataFrame: Nfreq x 2.  Column 1: downshift freq, Column 2: upshift freq
    """

    fn = Path(fn).expanduser()
    assert isinstance(beamid,integer_types),'beam specification must be a scalar integer'

    dshift=['downshift','upshift'] # by definition of dt1,dt2
    fiter = (('dt1',-5e6),('dt2',5e6))
    spec = None
    fshift=[]

    for F,s in zip(fiter,dshift):
        filename = fn.parent / ('.'.join((fn.stem.split('.')[0], F[0], 'h5')))
        try:
            with h5py.File(str(filename),'r',libver='latest') as f:
                T     = ut2dt(f['/Time/UnixTime'].value)
                bind  = findstride(f['/PLFFTS/Data/Beamcodes'], beamid) #NOTE: what if beam pattern changes during file?
                data = f['/PLFFTS/Data/Spectra/Data'][:,bind,:,:].squeeze().T
                srng  = f['/PLFFTS/Data/Spectra/Range'].value.squeeze()/1e3
                freq  = f['/PLFFTS/Data/Spectra/Frequency'].value.squeeze() + F[1]
        except OSError as e: #problem with file
            print('{} reading error {}'.format(fn,e))
            continue
        #
        fshift.append(s) # only if file was read
    #%% spectrum compute
        if tlim is None or tlim[0] is None:
            tind = range(len(T))
        else:
            tind = nonzero((tlim[0] <= T) & (T<=tlim[1]))[0]

        if spec is None:
            spec = DataArray(data = empty((len(dshift),len(tind),srng.size,freq.size)),
                             dims=['freqshift','time','srng','freq'],
                             coords={'freqshift':dshift, 'time':T[tind],'srng':srng})
            Freq = DataArray(data = empty((freq.size,len(dshift))),
                             dims=['freq','freqshift'],
                             coords={'freqshift':dshift})
        Freq.loc[:,s] = freq

        for ti,t in zip(tind,T[tind]):
            try:
                for i,r in enumerate(srng):
                    spec.loc[s,t,r,:] = data[i,:,ti]
            except KeyError:
                logging.error('problem reading {} at {}'.format(s,t))

#%% in case up or down not used
    spec = spec.loc[fshift,...]
    Freq = Freq.loc[:,fshift]

    return spec,Freq
