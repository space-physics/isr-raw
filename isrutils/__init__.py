import pathvalidate
from xarray import DataArray
from six import integer_types, string_types
from dateutil.parser import parse
from numpy import atleast_1d, ndarray,ones,array
from datetime import datetime
from pytz import UTC

try:
    from pathlib import Path
    Path().expanduser()
except (ImportError,AttributeError):
    from pathlib2 import Path



def writeplots(fg,t='',odir=None,ctxt=''):
    from matplotlib.pyplot import close

    if odir:
        odir = Path(odir).expanduser()
        odir.mkdir(parents=True,exist_ok=True)


        if isinstance(t,(DataArray)):
            t = datetime.fromtimestamp(t.item()/1e9, tz=UTC)
        elif isinstance(t,(float,integer_types)): # UTC assume
            t = datetime.fromtimestamp(t/1e9, tz=UTC)


        ppth = odir / pathvalidate.sanitize_filename(ctxt + str(t)[:-6] + '.png','-')  #:23 keeps up to millisecond if present.

        print('saving {}'.format(ppth))

        fg.savefig(str(ppth),dpi=100,bbox_inches='tight')

        close(fg)

def ut2dt(ut):
    assert isinstance(ut,ndarray) and ut.ndim in (1,2)

    if ut.ndim==1:
        T=ut
    elif ut.ndim==2:
        T=ut[:,0]
    #return array([datetime64(int(t*1e3),'ms') for t in T]) # datetime64 is too buggy as of Numpy 1.11 and xarray 0.7
    return array([datetime.fromtimestamp(t,tz=UTC) for t in T])


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

def filekey(f):
    # detect old and new HDF5 AMISR files
    if   '/Raw11/Raw/PulsesIntegrated' in f:        # new 2013
        return '/Raw11/Raw'
    elif '/Raw11/RawData/PulsesIntegrated' in f:    # old 2011
        return '/Raw11/RawData'
    elif '/RAW10/Data/Samples' in f:                # older 2007
        return '/RAW10/Data/'
    elif '/S/Data/PulsesIntegrated' in f:
        return '/S/Data'
    else:
        raise KeyError('not an old or new file?')

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