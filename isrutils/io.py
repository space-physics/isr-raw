from . import Path
import pathvalidate
from xarray import DataArray
from six import integer_types
from datetime import datetime
from pytz import UTC
from matplotlib.pyplot import close

def writeplots(fg,t='',odir=None,ctxt=''):

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