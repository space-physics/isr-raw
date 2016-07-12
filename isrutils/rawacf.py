from __future__ import division
from six import integer_types
from . import Path
import logging
import h5py
from xarray import DataArray
from numpy import (empty,zeros,complex128,conj,append,linspace)
from numpy.fft import fft,fftshift
#
from .common import ftype,ut2dt,findstride
from .plots import plotacf

def compacf(acfall,noiseall,Nr,dns,bstride):
    """
    acf all: Ntime x ? x Nlag x ? x real/comp

    """
    assert bstride.ndim == 2
    assert acfall.ndim == 5

    Nlag = acfall.shape[2]
    spec = empty((Nr,2*Nlag-1),complex128)

    acfall = acfall.value[bstride,:,:,:].sum(axis=0)
    acf = (acfall[:,:,0] + 1j*acfall[:,:,1]).T / dns / 2.

    try:
        noiseall = noiseall.value[bstride,:,:,:].sum(axis=0)
        acf_noise = (noiseall[:,:,0] + 1j*noiseall[:,:,1]).T / dns / 2.
    except TypeError:
        acf_noise= None
        spec_noise= 0.
#%% spectrum noise
    if acf_noise is not None:
        spec_noise = zeros(2*Nlag-1,complex128)
        for i in range(Nlag):
            spec_noise += fftshift(fft(append(conj(acf_noise[i,1:][::-1]),acf_noise[i,:])))
        #
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

        if not rk in f:
           logging.warning('{} does not exist in {}'.format(rk,fn))
           return

        srng = f[rk + 'Data/Acf/Range'].value.squeeze()
        bstride = findstride(f[rk+'Data/Beamcodes'],P['beamid'])
#        bcodemap = DataArray(data=f['/Setup/BeamcodeMap'][:,1:3],
#                             dims=['beamcode','azel'],
#                             coords={'beamcode':f['/Setup/BeamcodeMap'][:,0].astype(int),
 #                                    'azel':['az','el']}
#                            )
        i = (P['beamid'] == f['/Setup/BeamcodeMap'][:,0]).nonzero()[0].item()
        azel = f['/Setup/BeamcodeMap'][i,1:3]

        for i in range(len(tInd)):
            spectrum,acf = compacf(f[rk+'Data/Acf/Data'],
                                   noiseall,
                                   srng.size, dns, bstride)
            specdf = DataArray(data=spectrum,
                               dims=['srng','freq'],
                               coords={'srng':srng,
                                       'freq':linspace(-freqscalefact,freqscalefact,spectrum.shape[1])})
            try:
                plotacf(specdf,fn,azel,t[tInd[i]], P, ctxt='dB')
            except Exception as e:
                print('failed to plot ACF due to {}'.format(e))
