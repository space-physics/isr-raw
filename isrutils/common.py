from six import integer_types
from numpy import array,nonzero,empty,ndarray
from pathlib2 import Path
from datetime import datetime
from dateutil.parser import parse
from pytz import UTC
from matplotlib.pyplot import close
from argparse import ArgumentParser


def ut2dt(ut):
    assert isinstance(ut,ndarray) and ut.ndim in (1,2)

    if ut.ndim==1:
        T=ut
    elif ut.ndim==2:
        T=ut[:,0]
    return array([datetime.fromtimestamp(t,tz=UTC) for t in T])

def findstride(beammat,bid):
    assert isinstance(bid,integer_types)
    assert len(beammat.shape)==2 #h5py 2.5.0 dataset doesn't have ndim
    #FIXME is using just first row OK? other rows were identical for me.
#    Nt = beammat.shape[0]
#    index = empty((Nt,Np),dtype=int)
#    for i,b in enumerate(beammat):
#        index[i,:] = nonzero(b==bid)[0] #NOTE: candidate for np.s_ ?
    return nonzero(beammat[0,:]==bid)[0]

def ftype(fn):
    assert isinstance(fn,Path)
    return fn.name.split('.')[1]

def _expfn(fn):
    """
    returns text string based on file suffix
    """
    assert isinstance(fn,Path)

    if fn.name.endswith('.dt0.h5'):
        return 'alternating code'
    elif fn.name.endswith('.dt1.h5'):
        return 'downnshifted plasma line'
    elif fn.name.endswith('.dt2.h5'):
        return 'upshifted plasma line'
    elif fn.name.endswith('.dt3.h5'):
        return 'long pulse'

def sampletime(T,Np):
    assert isinstance(T,ndarray)
    assert isinstance(Np,integer_types)
    dtime = empty(Np*T.shape[0])
    i=0
    for t in T: #each row
        dt=(t[1]-t[0]) / Np
        for j in range(Np):
            dtime[i]=t[0]+j*dt
            i+=1
    return dtime

def writeplots(fg,t,odir,makeplot,ctxt=''):
    assert isinstance(odir,Path)

    if 'png' in makeplot:
        ppth = odir/(ctxt+t.strftime('%Y-%m-%dT%H:%M:%S')+'.png')
        print('saving {}'.format(ppth))
        fg.savefig(str(ppth),dpi=100,bbox_inches='tight')
        if 'show' not in makeplot:
            close(fg)

def boilerplateapi(descr='loading,procesing,plotting raw ISR data'):
    p = ArgumentParser(description=descr)
    p.add_argument('fn',help='HDF5 file to read')
    p.add_argument('--t0',help='time to extract 1-D vertical plot')
    p.add_argument('--acf',help='show autocorrelation function (ACF)',action='store_true')
    p.add_argument('--samples',help='use raw samples (lowest level data commnoly available)',action='store_true')
    p.add_argument('--beamid',help='beam id 64157 is magnetic zenith beam',type=int,default=64157)
    p.add_argument('--vlim',help='min,max for SNR plot [dB]',type=float,nargs=2)
    p.add_argument('--zlim',help='min,max for altitude [km]',type=float,nargs=2,default=(90,None))
    p.add_argument('--tlim',help='min,max time range yyyy-mm-ddTHH:MM:SSz',nargs=2)
    p.add_argument('--flim',help='frequency limits to plots',type=float,nargs=2)
    p.add_argument('-m','--makeplot',help='png to write pngs',nargs='+',default=['show'])
    p.add_argument('-o','--odir',help='directory to write files to',default='')
    p = p.parse_args()

    tlim = (parse(p.tlim[0]),parse(p.tlim[1])) if p.tlim else (None,None)

    return p,Path(p.fn).expanduser(),Path(p.odir).expanduser(),tlim