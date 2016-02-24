from h5py import Dataset
from numpy import (array,nonzero,empty,ndarray,int32,unravel_index,datetime64,
                   asarray,atleast_1d,nanmax,nanmin,nan,isfinite)
from scipy.interpolate import interp1d
from pathlib import Path
from datetime import datetime,timedelta
from dateutil.parser import parse
from pytz import UTC
from pandas import Timestamp
from matplotlib.pyplot import close
from matplotlib.dates import MinuteLocator,SecondLocator
from argparse import ArgumentParser
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
    assert len(isrlla) == len(optlla.dtype) == 3
    x,y,z = aer2ecef(beamazel[0],beamazel[1],heightkm*1e3,isrlla[0],isrlla[1],isrlla[2])
    az,el,srng= ecef2aer(x,y,z,optlla['lat'],optlla['lon'],optlla['alt_m'])

    return {'az':az,'el':el,'srng':srng}

def timesync(tisr,topt,tlim):
    """
    TODO: for now, assume optical is always faster
    inputs
    tisr: vector of UT1 Unix time for ISR
    topt: vector of UT1 Unix time for camera
    tlim: start,stop UT1 Unix time request

    output
    iisr: indices (integers) of isr to playback at same time as camera
    iopt: indices (integers) of optical to playback at same time as isr
    """

    if isinstance(tisr[0],datetime64):
        tisr = Timestamp(tisr) #FIXME untested
# separate comparison
    if isinstance(tisr[0],(datetime,Timestamp)):
        tisr = array([t.timestamp() for t in tisr]) #must be ndarray
    assert isinstance(tisr[0],float), 'datetime64 is not wanted here, lets use ut1_unix float for minimum conversion effort'

    if tlim is None:
        tlim = (nan,nan)
    if topt is None:
        topt = (nan,nan)
#%% interpolate isr indices to opt (assume opt is faster, a lot of duplicates iisr)
    tstart = nanmax([tlim[0],tisr[0], topt[0]])
    tend   = nanmin([tlim[1],tisr[-1],topt[-1]])

    if topt is not None and isfinite(topt[0]):
        f = interp1d(tisr,range(tisr.size),'nearest',assume_sorted=True)

        # optical:  typically treq = topt
        ioptreq = nonzero((tstart<=topt) & (topt<=tend))[0]

        toptreq = topt[ioptreq]
        iisrreq = f(toptreq).astype(int)

        #tisrreq = tisr[(tstart<=tisr) & (tisr<=tend)]
    else:
        ioptreq = (None,)*tisr.size
        iisrreq = nonzero((tstart<=tisr) & (tisr<=tend))[0]


    return iisrreq,ioptreq


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
    assert len(azimg.shape) == 2 and len(elimg.shape) == 2 #no ndim in h5py 2.5
    assert isinstance(az[0],float) and isinstance(el[0],float)

    adist = angledist(azimg,elimg,az,el)
    return unravel_index(adist.argmin(), azimg.shape)


def ut2dt(ut):
    assert isinstance(ut,ndarray) and ut.ndim in (1,2)

    if ut.ndim==1:
        T=ut
    elif ut.ndim==2:
        T=ut[:,0]
    return array([datetime.fromtimestamp(t,tz=UTC) for t in T])

def findstride(beammat:Dataset,bid:int):
    assert isinstance(bid,int)
    assert len(beammat.shape)==2 #h5py 2.5.0 dataset doesn't have ndim
    #FIXME is using just first row OK? other rows were identical for me.
#    Nt = beammat.shape[0]
#    index = empty((Nt,Np),dtype=int)
#    for i,b in enumerate(beammat):
#        index[i,:] = nonzero(b==bid)[0] #NOTE: candidate for np.s_ ?
    return nonzero(beammat[0,:]==bid)[0]

def ftype(fn:Path)->str:
    return fn.stem.rsplit('.',1)[-1]

def expfn(fn:Path)->str:
    """
    returns text string based on file suffix
    """
    fn=Path(fn)

    if ftype(fn)=='dt0':
        return 'alternating code'
    elif ftype(fn)=='dt1':
        return 'downshifted plasma line'
    elif ftype(fn)=='dt2':
        return 'upshifted plasma line'
    elif ftype(fn)=='dt3':
        return 'long pulse'

def sampletime(T,Np:int)->float:
    assert isinstance(T,(ndarray,Dataset))
    assert len(T.shape) ==2 and T.shape[1] == 2 #no ndim h5py 2.5
    assert isinstance(Np,(int,int32)), 'any integer will do'
    dtime = empty(Np*T.shape[0])
    i=0
    for t in T: #each row
        dt=(t[1]-t[0]) / Np
        for j in range(Np):
            dtime[i]=t[0]+j*dt
            i+=1
    return dtime

def writeplots(fg,t,odir,makeplot,ctxt=''):

    if 'png' in makeplot:
        odir = Path(odir).expanduser()
        odir.mkdir(parents=True,exist_ok=True)
        ppth = odir/(ctxt+t.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'.png')
        print('saving {}'.format(ppth))
        fg.savefig(str(ppth),dpi=100,bbox_inches='tight')
        if 'show' not in makeplot:
            close(fg)

def timeticks(tdiff:timedelta ):
    assert isinstance(tdiff,timedelta)

    if tdiff>timedelta(minutes=20):
        return MinuteLocator(interval=5)
    elif (timedelta(minutes=1)<tdiff) & (tdiff<=timedelta(minutes=20)):
        return MinuteLocator(interval=1)
    else:
        return SecondLocator(interval=5)

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

    tlim = (parse(p.tlim[0]),parse(p.tlim[1])) if p.tlim else (None,None)

    return (p,
            Path(p.isrfn).expanduser(),
            Path(p.odir).expanduser(),
            tlim,)
