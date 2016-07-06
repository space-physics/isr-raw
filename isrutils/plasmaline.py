#!/usr/bin/env python
from six import integer_types,string_types
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

    dshift=('downshift','upshift') # by definition of dt1,dt2
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
#            spec = Panel4D(labels=fshift,items=T[tind], major_axis=srng,minor_axis=range(freq.size))
 #           Freq = DataFrame(columns=fshift)
            spec = DataArray(data = empty((len(fshift),len(tind),srng.size,freq.size)),
                             dims=['freqshift','time','srng','freq'],
                             coords={'freqshift':fshift, 'time':T[tind],'srng':srng})
            Freq = DataArray(data = empty((freq.size,len(fshift))),
                             dims=['freq','freqshift'],
                             coords={'freqshift':fshift})
        Freq.loc[:,s] = freq

        for ti,t in zip(tind,T[tind]):
            for i,r in enumerate(srng):
                spec.loc[s,t,r,:] = data[i,:,ti]

    return spec,Freq
