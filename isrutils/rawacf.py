from __future__ import division
from six import integer_types
from . import Path
import logging
import h5py
from xarray import DataArray
from numpy import (empty,zeros,complex64,complex128,conj,append,linspace)
from numpy.fft import fft,fftshift
#
from .common import ftype,ut2dt,findstride
from .plots import plotacf

def compacf(acfall,noiseall,Nr,dns,bstride,ti,tInd):
    bstride=bstride.item()

    Nlag = acfall.shape[2]
    acf  = zeros((Nr,Nlag),complex64) #NOT empty, note complex64 is single complex float
    spec = empty((Nr,2*Nlag-1),complex128)
    try:
        acf_noise = zeros((noiseall.shape[3],Nlag),complex64)
        spec_noise= zeros(2*Nlag-1,complex128)
    except AttributeError:
        acf_noise = None
        spec_noise= 0.

#    acfall = acfall.value[bstride,:,:,:]
#    acf = (acfall[...,0] + 1j*acfall[...,1]).sum(axis=0).T / dns / 2.

    for i in range(tInd[ti]-1,tInd[ti]+1):
        acf += (   acfall[i,bstride,:,:,0] +
                1j*acfall[i,bstride,:,:,1]).T
        if acf_noise is not None: #must be is not None
            acf_noise += (   noiseall[i,bstride,:,:,0] +
                          1j*noiseall[i,bstride,:,:,1]).T

    acf = acf/dns/(i-(tInd[ti]-1)+1) #NOT /=
    if acf_noise is not None: #must be is not None
        acf_noise = acf_noise/dns / (i-(tInd[ti]-1)+1)
#%% spectrum noise
    if acf_noise is not None:
        for i in range(Nlag):
            spec_noise += fftshift(fft(append(conj(acf_noise[i,1:][::-1]),acf_noise[i,:])))


        spec_noise = spec_noise / Nlag
#%% spectrum from ACF
    for i in range(Nr):
        spec[i,:] = fftshift(fft(append(conj(acf[i,1:][::-1]), acf[i,:])))-spec_noise


    return spec,acf

def readACF(fn,P):
    """
    reads incoherent scatter radar autocorrelation function (ACF)
    """
    freqscalefact=100/2  #100/6

    dns=1071/3 #TODO scalefactor
    fn = Path(fn).expanduser()
    assert isinstance(P['beamid'],integer_types),'beam specification must be a scalar integer'

    with h5py.File(str(fn),'r',libver='latest') as f:
        t = ut2dt(f['/Time/UnixTime'].value)

        tInd = range(1,t.size-1) #list(range(20,30,1)) #TODO pick indices by datetime

        ft = ftype(fn)
        if ft == 'dt3':
            rk = '/S/'
            try:
                noiseall = f[rk+'Noise/Acf/Data']
            except KeyError:
                logging.warning('{} does not exist in {}'.format(rk,fn))
                return
        elif ft == 'dt0':
            rk = '/IncohCodeFl/'
            noiseall = None #TODO hack for dt0
        else:
            raise TypeError('unexpected file type {}'.format(ft))

        try:
            f[rk]
        except KeyError:
           logging.warning('{} does not exist in {}'.format(rk,fn))
           return

        srng = f[rk + 'Data/Acf/Range'].value.squeeze()
        bstride = findstride(f[rk+'Data/Beamcodes'],P['beamid'])
        bcodemap = DataArray(data=f['/Setup/BeamcodeMap'][:,1:3],
                             dims=['beamcode','azel'],
                             coords={'beamcode':f['/Setup/BeamcodeMap'][:,0].astype(int),
                                     'azel':['az','el']}
                            )
        azel = bcodemap.loc[P['beamid'],:]

        for i in range(len(tInd)):
            spectrum,acf = compacf(f[rk+'Data/Acf/Data'],
                                   noiseall,
                                   srng.size,dns,bstride,i,tInd)
            specdf = DataArray(data=spectrum,
                               dims=['srng','freq'],
                               coords={'srng':srng,
                                       'freq':linspace(-freqscalefact,freqscalefact,spectrum.shape[1])})
            try:
                plotacf(specdf,fn,azel,t[tInd[i]], P, ctxt='dB')
            except Exception as e:
                print('failed to plot ACF due to {}'.format(e))
