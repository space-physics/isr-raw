from pathlib import Path
import logging
from sys import stderr
from xarray import DataArray
from dateutil.parser import parse
import numpy as np
from numpy import correlate as xcorr
from numpy.fft import fft,fftshift
from datetime import datetime
from pytz import UTC
import h5py
from time import time
#
from .plots import plotbeampattern,plotacf
#
from sciencedates import forceutc

ACFfreqscale=100/6  #100/2
ACFdns=1071/3 #TODO scalefactor

def getazel(f, beamid:int) -> np.ndarray:
    """
    f: h5py HDF5 handle
    beamid: integer beam id number

    returns: azimuth,elevation pair (degrees)
    """
    assert isinstance(beamid,int)

    azelrow = (f['/Setup/BeamcodeMap'][:,0] == beamid).nonzero()[0]
    assert azelrow.size == 1, 'each beam should have a unique az,el'

    azel = f['/Setup/BeamcodeMap'][azelrow,1:3]
    assert azel.size==2

    return azel

def ut2dt(ut) -> np.ndarray:
    assert isinstance(ut, np.ndarray) and ut.ndim in (1,2)

    if ut.ndim==1:
        T=ut
    elif ut.ndim==2:
        T=ut[:,0]
    #return array([datetime64(int(t*1e3),'ms') for t in T]) # datetime64 is too buggy as of Numpy 1.11 and xarray 0.7
    return np.array([datetime.fromtimestamp(t,tz=UTC) for t in T])


def str2dt(tstr) -> list:
    """
    converts parseable string to datetime, pass other suitable types back through.
    FIXME: assumes all elements are of same type as first element.
    can't just do list comprehension in case all None
    """
    if not tstr:
        return

    tstr = np.atleast_1d(tstr)
    assert tstr.ndim == 1

    ut = []

    for t in tstr:
        if t is None or isinstance(t,datetime):
            ut.append(t)
        elif isinstance(t, str):
            ut.append(forceutc(parse(t)))
        elif isinstance(t, (float,int)):
            ut.append(datetime.fromtimestamp(t,tz=UTC))
        else:
            raise TypeError(f'unknown data type {ut[0].dtype}')

    return ut

def findstride(beammat:h5py.Dataset, bid:int) -> bool:
    assert isinstance(bid,int)
    assert beammat.ndim==2
    # NOTE: Pre-2013 files have distinct rows, so touch each value in beamcode!

    return beammat[:]==bid

def filekey(f:h5py.Dataset) -> str:
    # detect old and new HDF5 AMISR files
    if   '/Raw11/Raw/PulsesIntegrated' in f:        # new 2013
        return '/Raw11/Raw'
    elif '/Raw11/RawData/PulsesIntegrated' in f:    # old 2011
        return '/Raw11/RawData'
    elif '/RAW10/Data/Samples' in f:                # 2007
        return '/RAW10/Data/'
    elif '/S/Data/PulsesIntegrated' in f:           # 2007
        return '/S/Data'
    else:
        print('not an old or new file?',file=stderr)

def ftype(fn:Path) -> str:
    """
    returns file type i.e.  'dt0','dt1','dt2','dt3'
    """
    return fn.stem.rsplit('.',1)[-1]

def expfn(fn:Path) -> str:
    """
    returns text string based on file suffix
    """
    ft = ftype(fn)

    if ft   == 'dt0':
        return 'alternating code'
    elif ft == 'dt1':
        return 'downshift plasma line'
    elif ft == 'dt2':
        return 'upshift plasma line'
    elif ft == 'dt3':
        return 'long pulse'
    else:
        raise ValueError(f'unknown file type {ft}')

def cliptlim(t:np.ndarray, tlim):
    assert isinstance(t, np.ndarray) and t.ndim==1
    # FIXME what if tlim has 'NaT'?  as of Numpy 1.11, only Pandas understands NaT with .isnull()

    tlim = str2dt(tlim)

    tind = np.ones(t.size, bool)

    if tlim is not None:
        if tlim[0] is not None:
            tind &= tlim[0] <= t
        if tlim[1] is not None:
            tind &= t <= tlim[1]

    return t[tind],tind


def sampletime(t, bstride):
    """
    read the time of the pulses to the microsecond level
    t: h5py variable
    bstride: 2-D boolean

    returns: 2-D single of UTC time unix epoch
    """
    assert isinstance(t, (np.ndarray, h5py.Dataset)), 'Numpy or h5py array only'
    assert t.ndim == 2

    assert t.shape[0] == bstride.shape[0]  # number of times

    if bstride.sum() == 0:  # selected beam was never used in this file
        t = None
    else:
        t = t[bstride]
        if t.max() > 1.01*t.mean():
            logging.warning('at least one time gap in radar detected')

    return t

# %% plasmaline
def readplasmaline(fn:Path, P:dict):
    """
    inputs:
    fn: d*.dt?.h5 file to load
    beamid: AMISR beam id (scalar)

    outputs:
    spec: Ntime x Nrange x Nfreq
    """
    if not ftype(fn) in ('dt1','dt2'):
        return [None]*3

    tic = time()
    fn = Path(fn).expanduser()
    assert isinstance(P['beamid'],int),'beam specification must be a scalar integer'

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
        with h5py.File(fn,'r',libver='latest') as f:
            T     = ut2dt(f['/Time/UnixTime'].value)
            bind  = findstride(f['/PLFFTS/Data/Beamcodes'], beamid)
            data = f['/PLFFTS/Data/Spectra/Data'].value[bind,:,:].T
            srng  = f['/PLFFTS/Data/Spectra/Range'].value.squeeze()/1e3
            freq  = f['/PLFFTS/Data/Spectra/Frequency'].value.squeeze() + fshift
            azel = getazel(f,beamid)
    except OSError as e: #problem with file
        print('reading error',fn,e, file=stderr)
        return (None,)*2
#%% spectrum compute
    T,tind = cliptlim(T,tlim)

    spec = DataArray(data = data[:,:,tind].transpose(2,0,1),
                     dims=['time','srng','freq'],
                     coords={'time':T, 'srng':srng, 'freq':freq})


    return spec,azel


# %% Power
def samplepower(sampiq,bstride,ut,srng,P:dict):
    """
    returns I**2 + Q**2 of radar received amplitudes
    FIXME: what are sample units?

    speed up indexing by downselecting by altitude, then time
    """
    assert sampiq.ndim == 4
    assert bstride.ndim== 2 and sampiq.shape[:2] == bstride.shape and bstride.dtype==bool
    assert 'zlim' in P, 'did not specifiy zlim'
    zlim = P['zlim']
#%% filter by range
    Nr = srng.size
    zind = np.ones(Nr, bool)
    if zlim[0] is not None:
        zind &= zlim[0]<=srng
    if zlim[1] is not None:
        zind &= srng<=zlim[1]
    srng = srng[zind]
#%% filter by time
    t = ut2dt(ut)

    t,tind = cliptlim(t,P['tlim'])

    sampiq = sampiq[:][bstride,:,:]
    sampiq = sampiq[:,zind,:]
    sampiq = sampiq[tind,:,:]
    power = (sampiq[...,0]**2. + sampiq[...,1]**2.).T


    return DataArray(data=power,
                     dims=['srng','time'],
                     coords={'srng':srng,'time':t})

def readpower_samples(fn:Path, P:dict):
    """
    reads samples (lowest level data) and computes power for a particular beam.
    returns power measurements
    """
    if not ftype(fn) in ('dt0','dt3'):
        return

    assert isinstance(P['beamid'],int),'beam specification must be a scalar integer!'

    try:
      with h5py.File(fn, 'r', libver='latest') as f:
          # scalars need .value, [:] won't work
        isrlla = (f['/Site/Latitude'].value,
                  f['/Site/Longitude'].value,
                  f['/Site/Altitude'].value)
        azel = getazel(f,P['beamid'])
# %% find time and beam pattern
        rawkey = filekey(f)

        if rawkey+'/RadacHeader/BeamCode' in f:
            beampatkey = rawkey+'/RadacHeader/BeamCode'
            timekey = rawkey+'/RadacHeader/RadacTime'
        elif '/RadacHeader/BeamCode' in f:  # old 2007 DT3 files (DT0 2007 didn't have raw data?)
            beampatkey = '/RadacHeader/BeamCode'
            timekey = '/RadacHeader/RadacTime'
        else: # very old 2007 files
            beampatkey = rawkey + '/Beamcodes'
            timekey = '/Time/RadacTime'

        bstride = findstride(f[beampatkey],P['beamid'])

        ut = sampletime(f[timekey],bstride)

        plotbeampattern(f,P,f[beampatkey])
#%%
        srng  = f[rawkey+'/Power/Range'][:].squeeze()/1e3

        if rawkey+'/Samples/Data' in f:
            power = samplepower(f[rawkey+'/Samples/Data'],bstride,ut,srng,P) #I + jQ   # Ntimes x striped x alt x real/comp
        else:
            print(f'raw pulse data not found {fn}', file=stderr)
            power = None

    except OSError as e: #problem with file
        print(f'{fn} OSError when reading: \n {e}', file=stderr)
        power = None

    return power,azel,isrlla

def readsnr_int(fn, bid:int) -> DataArray:
    if not ftype(fn) in ('dt0','dt3'):
        return

    assert isinstance(bid, int),'beam specification must be a scalar integer!'

    try:
        with h5py.File(fn, 'r', libver='latest') as f:
            t = ut2dt(f['/Time/UnixTime'][:])
            rawkey = filekey(f)
            try:
                bind  = f[rawkey+'/Beamcodes'][0,:] == bid
                power = f[rawkey+'/Power/Data'][:,bind,:].squeeze().T
            except KeyError:
                power = f[rawkey+'/Power/Data'][:].T

            srng  = f[rawkey+'/Power/Range'][:].squeeze()/1e3
#%% return requested beam data only
            snrint = DataArray(data=power,
                               dims=['srng','time'],
                               coords={'srng':srng,'time':t})
    except KeyError as e:
        print('integrated pulse data not found',fn,e,file=stderr)
        snrint = None

    return snrint

def snrvtime_fit(fn,bid:int) -> DataArray:
    fn = Path(fn).expanduser()

    with h5py.File(fn, 'r', libver='latest') as f:
        t = ut2dt(f['/Time/UnixTime'][:])
        bind = f['/BeamCodes'][:,0] == bid
        snr = f['/NeFromPower/SNR'][:,bind,:].squeeze().T
        z = f['/NeFromPower/Altitude'][bind,:].squeeze()/1e3
#%% return requested beam data only
        return DataArray(data=snr,
                         dims=['alt','time'],
                         coords={'alt':z,'time':t})


#%% ACF

def acf2psd(acfall,noiseall,Nr,dns):
    """
    acf all:  Nlag x Nslantrange x real/comp

    """
    assert acfall.ndim in (3,2)

    Nlag = acfall.shape[0]
    spec = np.empty((Nr,2*Nlag-1), 'complex128')

    if acfall.ndim == 3: # last dim real,cplx
        acf = (acfall[...,0] + 1j*acfall[...,1]).T / dns / 2.
    elif acfall.ndim == 2 and np.iscomplex(acfall[0,0]):
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
        spec_noise = np.zeros(2*Nlag-1, 'complex128')
        for i in range(Nlag):
            spec_noise += fftshift(fft(np.append(np.conj(acf_noise[i,1:][::-1]),acf_noise[i,:])))
        #
        spec_noise = spec_noise / Nlag
#%% spectrum from ACF
    for i in range(Nr):
        spec[i,:] = fftshift(fft(np.append(np.conj(acf[i,1:][::-1]), acf[i,:])))-spec_noise

    return spec,acf

def readACF(fn:Path, P:dict):
    """
    reads incoherent scatter radar autocorrelation function (ACF)
    """
    if not ftype(fn) in ('dt0','dt3'):
        return

    assert isinstance(P['beamid'],int),'beam specification must be a scalar integer'

    with h5py.File(fn, 'r', libver='latest') as f:
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
            if ft == 'dt3':
                print('try DT0 file for ACF (esp. for 2007 PFISR)')
            return
#%% get ranges
        try:
            srng = f[rk + 'Data/Acf/Range']
            bstride = findstride(f[rk+'Data/Beamcodes'],P['beamid'])
        except KeyError: # old 2007 files
            srng = f[filekey(f) + '/Power/Range']
            bstride = findstride(f['/RadacHeader/BeamCode'], P['beamid'])
#%% get azel
        azel = getazel(f,P['beamid'])
#%% get times
        t,tind = cliptlim(t,P['tlim'])
        if len(t)==0:
            logging.warning(f'did not plot ACF since {fn} not within tlim {P["tlim"]}')

        dt = (t[1]-t[0]).seconds if len(t)>=2 else None
#%% get PSD

        istride = np.column_stack(bstride.nonzero())[tind,:]
        for tt,s in zip(t,istride):
            if noisekey is not None:
                spectrum,acf = acf2psd(acfkey[s[0],s[1],...],
                                       noisekey[s[0],s[1],...],
                                       srng.size, ACFdns)
            elif acfkey.ndim==5:
                spectrum,acf = acf2psd(acfkey[s[0],s[1],...],
                                       noisekey,
                                       srng.size, ACFdns)
            elif acfkey.ndim==4: # TODO raw samples from 2007 file
                raise NotImplementedError('TODO this code not complete--need to have all the lags as a dimension. See Swoboda PhD code for proper computation of lags from complex voltage. https://github.com/jswoboda')
                tdat = acfkey[s[0],s[1],:,0] + 1j*acfkey[s[0],s[1],:,1]
                acfall = xcorr(tdat, tdat, 'full')
                spectrum,acf = acf2psd(acfall,
                                       noisekey,
                                       srng.size, ACFdns)

            specdf = DataArray(data=spectrum,
                               dims=['srng','freq'],
                               coords={'srng': srng.value.squeeze(),
                                       'freq': np.linspace(-ACFfreqscale, ACFfreqscale, spectrum.shape[1])})
            try:
                plotacf(specdf,fn,azel,tt, dt, P)
            except Exception as e:
                logging.error(f'failed to plot ACF due to {e}')

def dt3keys(f):

    rk = '/S/'

    try:
        acfkey = f[rk+'Data/Acf/Data']
        noisekey = f[rk+'Noise/Acf/Data']
    except KeyError:
        acfkey = f[filekey(f) + '/Samples/Data'] #2007 dt3 raw data
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