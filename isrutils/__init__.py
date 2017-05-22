from pathlib import Path
import logging
from sys import stderr
from xarray import DataArray
from dateutil.parser import parse
from numpy import atleast_1d, ndarray,ones,array
from datetime import datetime
from pytz import UTC
import h5py
from time import time
#
import pathvalidate
#
from .plots import plotbeampattern

def writeplots(fg, t='', odir=None, ctxt='', ext='.png'):
    from matplotlib.pyplot import close

    if odir:
        odir = Path(odir).expanduser()
        odir.mkdir(parents=True,exist_ok=True)


        if isinstance(t,(DataArray)):
            t = datetime.fromtimestamp(t.item()/1e9, tz=UTC)
        elif isinstance(t,(float,int)): # UTC assume
            t = datetime.fromtimestamp(t/1e9, tz=UTC)

            #:-6 keeps up to millisecond if present.
        ppth = odir / pathvalidate.sanitize_filename(ctxt + str(t)[:-6] + ext,'-').replace(' ','')

        print('saving',ppth)

        fg.savefig(str(ppth),dpi=100,bbox_inches='tight')

        close(fg)

def getazel(f, beamid:int) -> ndarray:
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

def ut2dt(ut) -> ndarray:
    assert isinstance(ut,ndarray) and ut.ndim in (1,2)

    if ut.ndim==1:
        T=ut
    elif ut.ndim==2:
        T=ut[:,0]
    #return array([datetime64(int(t*1e3),'ms') for t in T]) # datetime64 is too buggy as of Numpy 1.11 and xarray 0.7
    return array([datetime.fromtimestamp(t,tz=UTC) for t in T])


def str2dt(tstr) -> list:
    """
    converts parseable string to datetime, pass other suitable types back through.
    FIXME: assumes all elements are of same type as first element.
    can't just do list comprehension in case all None
    """
    if not tstr:
        return

    tstr = atleast_1d(tstr)
    assert tstr.ndim == 1

    ut = []

    for t in tstr:
        if t is None or isinstance(t,datetime):
            ut.append(t)
        elif isinstance(t, str):
            ut.append(parse(t))
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

def cliptlim(t,tlim):
    assert isinstance(t,ndarray) and t.ndim==1
    # FIXME what if tlim has 'NaT'?  as of Numpy 1.11, only Pandas understands NaT with .isnull()

    tind = ones(t.size,dtype=bool)

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
    assert isinstance(t, (ndarray, h5py.Dataset)), 'Numpy or h5py array only'
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
        return

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
    zind = ones(Nr,dtype=bool)
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

def readsnr_int(fn, bid:int, ft:str) -> DataArray:
    if not ft in ('dt0','dt3'):
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
#                               dims=['srng','time'],
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