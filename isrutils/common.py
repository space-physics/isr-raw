from . import Path
from six import integer_types, string_types
from datetime import datetime
from dateutil.parser import parse
from pytz import UTC
from h5py import Dataset
from numpy import (array,ndarray,unravel_index,ones, datetime64, asarray,atleast_1d,nanmax,nanmin,nan,isfinite)
from scipy.interpolate import interp1d
from argparse import ArgumentParser
#
from pymap3d.haversine import angledist
from pymap3d.coordconv3d import aer2ecef,ecef2aer

EPOCH = datetime(1970,1,1,0,0,0,tzinfo=UTC)

def projectisrhist(isrlla,beamazel,optlla,optazel,heightkm):
    """
    intended to project ISR beam at a single height into optical data.

    output:
    az,el,slantrange in degrees,meters
    """
    isrlla = asarray(isrlla); optlla=asarray(optlla)
    assert isrlla.size == optlla.size == 3
    x,y,z = aer2ecef(beamazel[0],beamazel[1],heightkm*1e3,isrlla[0],isrlla[1],isrlla[2])
    try:
        az,el,srng = ecef2aer(x,y,z,optlla[0],optlla[1],optlla[2])
    except IndexError:
        az,el,srng = ecef2aer(x,y,z,optlla['lat'],optlla['lon'],optlla['alt_km'])

    return {'az':az,'el':el,'srng':srng}

def getazel(f,beamid):
    """
    f: h5py HDF5 handle
    beamid: integer beam id number

    returns: azimuth,elevation pair (degrees)
    """
    assert isinstance(beamid,integer_types)

    azelrow = (f['/Setup/BeamcodeMap'][:,0] == beamid).nonzero()[0]
    assert azelrow.size == 1, 'each beam should have a unique az,el'

    azel = f['/Setup/BeamcodeMap'][azelrow,1:3]
    assert azel.size==2
    return azel

def timesync(tisr,topt,tlim=[None,None]):
    """
    TODO: for now, assume optical is always faster
    inputs
    tisr: vector of datetime for ISR
    topt: vector of datetime for camera
    tlim: start,stop UT1 Unix time request

    output
    iisr: indices (integers) of isr to playback at same time as camera
    iopt: indices (integers) of optical to playback at same time as isr
    """
    if isinstance(tisr[0],datetime):
        tisr = array([t.timestamp() for t in tisr]) #must be ndarray
    elif isinstance(tisr[0],datetime64):
        tisr = tisr.astype(float)/1e9

    assert ((tisr>1e9) & (tisr<2e9)).all(),'date sanity check'

    if isinstance(tlim[0],datetime):
        tlim = array([t.timestamp() for t in tlim])

    assert isinstance(tisr[0],float), 'datetime64 is not wanted here, lets use ut1_unix float for minimum conversion effort'
# separate comparison
    if topt is None:
        topt = (nan,nan)
#%% interpolate isr indices to opt (assume opt is faster, a lot of duplicates iisr)
    tstart = nanmax([tlim[0], tisr[0], topt[0]])
    tend   = nanmin([tlim[1], tisr[-1], topt[-1]])

    if topt is not None and isfinite(topt[0]):
        f = interp1d(tisr,range(tisr.size),'nearest',assume_sorted=True)

        # optical:  typically treq = topt
        ioptreq = ((tstart<=topt) & (topt<=tend)).nonzero()[0]

        toptreq = topt[ioptreq]
        iisrreq = f(toptreq).astype(int)

        #tisrreq = tisr[(tstart<=tisr) & (tisr<=tend)]
    else:
        ioptreq = (None,)*tisr.size
        iisrreq = ((tstart<=tisr) & (tisr<=tend)).nonzero()[0]

    return iisrreq,ioptreq

def cliptlim(t,tlim):
    assert isinstance(t,ndarray) and t.ndim==1
    assert len(tlim) == 2
    # FIXME what if tlim has 'NaT'?  as of Numpy 1.11, only Pandas understands NaT with .isnull()
    tind = ones(t.size,dtype=bool)

    if tlim[0] is not None:
        tind &= tlim[0] <= t
    if tlim[1] is not None:
        tind &= t <= tlim[1]

    return t[tind],tind


def findindex2Dsphere(azimg,elimg,az,el):
    """
    finds nearest row,column index of projection on 2-D sphere.
    E.g. an astronomical or auroral camera image

    inputs:
    azimg: azimuth of image pixels (deg)
    elimg: elevation of image pixels (deg)
    az: azimuth of point you seek to find the index for (deg)
    el: elevation of point you seek to find the index for (deg)

    output:
    row, column of 2-D image closest to az,el


    brute force method of finding the row,col with the closest az,el using haversine method
    useful for:
    azimuth, elevation
    right ascension, declination
    latitude, longitude
    """
    az = atleast_1d(az); el = atleast_1d(el)
    assert azimg.ndim == 2 and elimg.ndim == 2
    assert isinstance(az[0],float) and isinstance(el[0],float)

    adist = angledist(azimg,elimg,az,el)
    return unravel_index(adist.argmin(), azimg.shape)

def str2dt(tstr):
    """
    converts parseable string to datetime, pass other suitable types back through.
    FIXME: assumes all elements are of same type as first element.
    can't just do list comprehension in case all None
    """
    tstr = atleast_1d(tstr)
    assert tstr.ndim == 1

    ut = []

    for t in tstr:
        if t is None or isinstance(t,datetime):
            ut.append(t)
        elif isinstance(t,string_types):
            ut.append(parse(t))
        elif isinstance(t,(float,integer_types)):
            ut.append(datetime.fromtimestamp(t,tz=UTC))
        else:
            raise TypeError('unknown data type {}'.format(ut[0].dtype))

    return ut

def ut2dt(ut):
    assert isinstance(ut,ndarray) and ut.ndim in (1,2)

    if ut.ndim==1:
        T=ut
    elif ut.ndim==2:
        T=ut[:,0]
    #return array([datetime64(int(t*1e3),'ms') for t in T]) # datetime64 is too buggy as of Numpy 1.11 and xarray 0.7
    return array([datetime.fromtimestamp(t,tz=UTC) for t in T])

#def findstride(beammat:Dataset,bid:int):
def findstride(beammat, bid):
    assert isinstance(bid,integer_types)
    assert beammat.ndim==2
    # NOTE: Pre-2013 files have distinct rows, so touch each value in beamcode!

#    Nt = beammat.shape[0]
#    index = empty((Nt,Np),dtype=int)
#    for i,b in enumerate(beammat):
#        index[i,:] = nonzero(b==bid)[0] #NOTE: candidate for np.s_ ?

#    return column_stack(beammat[:]==bid).nonzero()
    return beammat[:]==bid #boolean

def ftype(fn):
    """
    returns file type i.e.  'dt0','dt1','dt2','dt3'
    """
    return Path(fn).stem.rsplit('.',1)[-1]

def expfn(fn):
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
        ValueError('unknown file type {}'.format(ft))

def sampletime(t,bstride):
    """
    read the time of the pulses to the microsecond level
    t: h5py variable
    bstride: 2-D boolean

    returns: 2-D single of UTC time unix epoch
    """
    assert isinstance(t,Dataset),'hdf5 only'
    assert t.ndim == 2

    return t.value[bstride]

def boilerplateapi(descr='loading, processing, plotting raw ISR data'):
    p = ArgumentParser(description=descr)
    p.add_argument('-i','--isrfn',help='HDF5 file (or path) to read')
    p.add_argument('-c','--optfn',help='optical data HDF5 to read') #,nargs='+',default=('',)
    p.add_argument('-a','--azelfn',help='plate scale file hdf5') #,nargs='+',default=('',)
    p.add_argument('--t0',help='time to extract 1-D vertical plot')
    p.add_argument('--acf',help='show autocorrelation function (ACF)',action='store_true')
    p.add_argument('--beamid',help='beam id 64157 is magnetic zenith beam',type=int,default=64157)
    p.add_argument('--vlim',help='min,max for SNR plot [dB]',type=float,nargs=2,default=(None,None))
    p.add_argument('--zlim',help='min,max for altitude [km]',type=float,nargs=2,default=(90.,None))
    p.add_argument('--tlim',help='min,max time range yyyy-mm-ddTHH:MM:SSz',nargs=2,default=[None,None])
    p.add_argument('--flim',help='frequency limits to plots',type=float,nargs=2,default=(None,None))
    p.add_argument('-o','--odir',help='directory to write files to',default='')
    p = p.parse_args()

    return p