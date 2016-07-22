from six import integer_types, string_types
from h5py import Dataset
from numpy import (array,ndarray,unravel_index,ones,timedelta64,
                   datetime64, asarray,atleast_1d,nanmax,nanmin,nan,isfinite)
from scipy.interpolate import interp1d
from . import Path
from matplotlib.pyplot import close
from matplotlib.dates import MinuteLocator,SecondLocator
from argparse import ArgumentParser
from xarray import DataArray
#
from pymap3d.haversine import angledist
from pymap3d.coordconv3d import aer2ecef,ecef2aer


def projectisrhist(isrlla,beamazel,optlla,optazel,heightkm):
    """
    intended to project ISR beam at a single height into optical data.

    output:
    az,el,slantrange in degrees,meters
    """
    isrlla = asarray(isrlla); optlla=asarray(optlla)
    assert isrlla.size == optlla.size == 3
    x,y,z = aer2ecef(beamazel[0],beamazel[1],heightkm*1e3,isrlla[0],isrlla[1],isrlla[2])
    az,el,srng= ecef2aer(x,y,z,optlla[0],optlla[1],optlla[2])

    return {'az':az,'el':el,'srng':srng}

def timesync(tisr,topt,tlim=[None,None]):
    """
    TODO: for now, assume optical is always faster
    inputs
    tisr: vector of datetime64 for ISR
    topt: vector of datetime64 for camera
    tlim: start,stop UT1 Unix time request

    output
    iisr: indices (integers) of isr to playback at same time as camera
    iopt: indices (integers) of optical to playback at same time as isr
    """
    if isinstance(tisr[0],datetime64):
        tisr = tisr.astype(float)/1e9

    assert ((tisr>1e9) & (tisr<2e9)).all(),'date sanity check'

    if isinstance(tlim[0],datetime64):
        tlim = tlim.astype(float)
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
    # FIXME what if tlim has 'NaT'?  as of Numpy 1.11, only Pandas understands NaT with .isnull()
    tind = ones(t.size,dtype=bool)

    if tlim[0] is not None:
        tind &= datetime64(tlim[0]) <= t
    if tlim[1] is not None:
        tind &= t <= datetime64(tlim[1])

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

def str2dt(ut):
    """
    """
    assert isinstance(ut,(list,tuple,ndarray)) and isinstance(ut[0],string_types)
    return array([datetime64(t) for t in ut])


def ut2dt(ut):
    assert isinstance(ut,ndarray) and ut.ndim in (1,2)

    if ut.ndim==1:
        T=ut
    elif ut.ndim==2:
        T=ut[:,0]
    return array([datetime64(int(t*1e3),'ms') for t in T])

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
    """
    assert isinstance(t,Dataset),'hdf5 only'
    assert t.ndim == 2

    return t.value[bstride]

def writeplots(fg,t,odir,makeplot,ctxt=''):

    if odir:
        odir = Path(odir).expanduser()
        odir.mkdir(parents=True,exist_ok=True)

        if isinstance(t,DataArray):
            t = datetime64(t.item(),'ns')

        ppth = odir / (ctxt+str(t)[:23]+'.png')  #:23 keeps up to millisecond if present.

        print('saving {}'.format(ppth))
        fg.savefig(str(ppth),dpi=100,bbox_inches='tight')
        if 'show' not in makeplot:
            close(fg)

#def timeticks(tdiff:timedelta ):
def timeticks(tdiff):
    if isinstance(tdiff,DataArray): #len==1
        tdiff = timedelta64(int(tdiff.item()),'ns')
    assert isinstance(tdiff,timedelta64)

    if tdiff > timedelta64(20,'m'):
        return MinuteLocator(interval=5)
    elif (timedelta64(1,'m')<tdiff) & (tdiff<=timedelta64(20,'m')):
        return MinuteLocator(interval=1)
    elif (timedelta64(30,'s')<tdiff) &(tdiff<=timedelta64(1,'m')):
        return SecondLocator(interval=5)
    else:
        return SecondLocator(interval=2)

def boilerplateapi(descr='loading,procesing,plotting raw ISR data'):
    p = ArgumentParser(description=descr)
    p.add_argument('isrfn',help='HDF5 file to read')
    p.add_argument('-c','--optfn',help='optical data HDF5 to read') #,nargs='+',default=('',)
    p.add_argument('-a','--azelfn',help='plate scale file hdf5') #,nargs='+',default=('',)
    p.add_argument('--t0',help='time to extract 1-D vertical plot')
    p.add_argument('--acf',help='show autocorrelation function (ACF)',action='store_true')
    p.add_argument('--samples',help='use raw samples (lowest level data commnoly available)',action='store_true')
    p.add_argument('--beamid',help='beam id 64157 is magnetic zenith beam',type=int,default=64157)
    p.add_argument('--vlim',help='min,max for SNR plot [dB]',type=float,nargs=2,default=(None,None))
    p.add_argument('--zlim',help='min,max for altitude [km]',type=float,nargs=2,default=(80.,1000.))
    p.add_argument('--tlim',help='min,max time range yyyy-mm-ddTHH:MM:SSz',nargs=2)
    p.add_argument('--flim',help='frequency limits to plots',type=float,nargs=2,default=(None,None))
    p.add_argument('-m','--makeplot',help='png to write pngs',nargs='+',default=['show'])
    p.add_argument('-o','--odir',help='directory to write files to',default='')
    p = p.parse_args()

    tlim = (datetime64(p.tlim[0]), datetime64(p.tlim[1])) if p.tlim else (None,None)

    return (p,
            Path(p.isrfn).expanduser(),
            Path(p.odir).expanduser(),
            tlim,)
