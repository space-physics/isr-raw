from __future__ import division
from . import Path, ftype,ut2dt,cliptlim,filekey
import h5py
import logging
from xarray import DataArray
from numpy import (empty,zeros,complex128,conj,append,linspace,column_stack,iscomplex)
from numpy import correlate as xcorr
from numpy.fft import fft,fftshift
#
from .common import findstride,getazel
from .plots import plotacf

freqscalefact=100/6  #100/2
dns=1071/3 #TODO scalefactor

def acf2psd(acfall,noiseall,Nr,dns):
    """
    acf all:  Nlag x Nslantrange x real/comp

    """
    assert acfall.ndim in (3,2)

    Nlag = acfall.shape[0]
    spec = empty((Nr,2*Nlag-1),complex128)

    if acfall.ndim == 3: # last dim real,cplx
        acf = (acfall[...,0] + 1j*acfall[...,1]).T / dns / 2.
    elif acfall.ndim == 2 and iscomplex(acfall[0,0]):
        acf = acfall / dns / 2.
    else:
        raise TypeError('is this really ACF? I expect complex 2-D matrix')

    try:
        acf_noise = (noiseall[...,0] + 1j*noiseall[...,1]).T / dns / 2.
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
    fn = Path(fn).expanduser()
    assert isinstance(P['beamid'],int),'beam specification must be a scalar integer'

    with h5py.File(str(fn),'r',libver='latest') as f:
        t = ut2dt(f['/Time/UnixTime'].value)

        ft = ftype(fn)
        noisekey = None
#%%
        if ft == 'dt3':
            rk,acfkey,noisekey = dt3keys(f)
        elif ft == 'dt0':
            rk,acfkey = dt0keys(f)
        else:
            raise TypeError('unexpected file type {}'.format(ft))

        if acfkey is None or rk not in f:
            return
#%% get ranges
        try:
            srng = f[rk + 'Data/Acf/Range']
            bstride = findstride(f[rk+'Data/Beamcodes'],P['beamid'])
        except KeyError: # old 2007 files
            srng = f[filekey(f)+'/Power/Range']
            bstride = findstride(f['/RadacHeader/BeamCode'],P['beamid'])
#%% get azel
        azel = getazel(f,P['beamid'])
#%% get times
        t,tind = cliptlim(t,P['tlim'])

        dt = (t[1]-t[0]).seconds
#%% get PSD
        istride = column_stack(bstride.nonzero())[tind,:]
        for tt,s in zip(t,istride):
            if noisekey is not None:
                spectrum,acf = acf2psd(acfkey[s[0],s[1],...],
                                       noisekey[s[0],s[1],...],
                                       srng.size, dns)
            elif acfkey.ndim==5:
                spectrum,acf = acf2psd(acfkey[s[0],s[1],...],
                                       noisekey,
                                       srng.size, dns)
            elif acfkey.ndim==4: # TODO raw samples from 2007 file
                raise NotImplementedError('TODO this code not complete--need to have all the lags as a dimension. See Swoboda PhD code for proper computation of lags from complex voltage. https://github.com/jswoboda')
                tdat = acfkey[s[0],s[1],:,0] + 1j*acfkey[s[0],s[1],:,1]
                acfall = xcorr(tdat, tdat, 'full')
                spectrum,acf = acf2psd(acfall,
                                       noisekey,
                                       srng.size, dns)

            specdf = DataArray(data=spectrum,
                               dims=['srng','freq'],
                               coords={'srng':srng.value.squeeze(),
                                       'freq':linspace(-freqscalefact,freqscalefact,spectrum.shape[1])})
            try:
                plotacf(specdf,fn,azel,tt, dt, P)
            except Exception as e:
                logging.error('failed to plot ACF due to {}'.format(e))

def dt3keys(f):

    rk = '/S/'

    try:
        acfkey = f[rk+'Data/Acf/Data']
        noisekey = f[rk+'Noise/Acf/Data']
    except KeyError:
        acfkey = f[filekey(f)+'/Samples/Data'] #2007 dt3 raw data
        noisekey=None

    return rk,acfkey,noisekey

def dt0keys(f):
    try:
        rk = '/IncohCodeFl/'
        acfkey = f[rk+'Data/Acf/Data']
    except KeyError: # note for March 2011 PFISR, /S/ was in DT3 only not DT0, per Hassan
        try:
            rk = '/S/'
            acfkey = f[rk+'Data/Acf/Data'] # 2007 dt0 acf data
        except KeyError:
            acfkey=None
            logging.error('did not find ACF in {}. Try the .dt3 file (esp. if 2011 data)'.format(f.filename))

    return rk,acfkey