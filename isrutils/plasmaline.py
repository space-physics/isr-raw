from __future__ import division, absolute_import
from six import integer_types
from pathlib2 import Path
from numpy import empty,log10,nonzero
import h5py
#from pandas import DataFrame
from matplotlib.pyplot import figure
#
from .common import ftype,findstride,ut2dt,_expfn,writeplots

def readplasmaline(fn,beamid,makeplot,odir,tlim,vlim):
    assert isinstance(fn,Path)
    assert isinstance(beamid,integer_types) # a scalar integer!
    fn = fn.expanduser()

    ft = ftype(fn)
    if ft == 'dt2':
        foffs = 5e6
    elif ft =='dt1':
        foffs = -5e6
    else:
        raise TypeError('is this a plasmaline file? {}'.format(ft))

    with h5py.File(str(fn),'r',libver='latest') as f:
        T     = ut2dt(f['/Time/UnixTime'].value)
        bind  = findstride(f['/PLFFTS/Data/Beamcodes'], beamid)
        data = f['/PLFFTS/Data/Spectra/Data'][:,bind,:,:].squeeze().T
        srng  = f['/PLFFTS/Data/Spectra/Range'].value.squeeze()/1e3
        freq  = f['/PLFFTS/Data/Spectra/Frequency'].value.squeeze() + foffs
#%% spectrum compute
    if tlim:
        tind = nonzero((tlim[0] <= T) & (T<=tlim[1]))[0]
    spec = empty((srng.size,freq.size))
    for ti,t in zip(tind,T[tind]):
        for i in range(srng.size):
            spec[i,:] = data[i,:,ti]
        plotplasmaline(spec,srng,freq,fn,t,vlim=vlim,ctxt=_expfn(fn),makeplot=makeplot,odir=odir)



def plotplasmaline(spec,srng,freq,fn,t,
                   tlim=(None,None),vlim=(None,None),ctxt='',makeplot=[],odir=''):
    fg = figure()
    ax = fg.gca()

    zgood = srng>60 # above N km

    h=ax.pcolormesh(freq/1e6,srng[zgood],10*log10(spec[zgood,:]),
                    vmin=vlim[0],vmax=vlim[1],cmap='jet')#'cubehelix_r')
    c=fg.colorbar(h,ax=ax)
    c.set_label(ctxt)
    ax.set_xlabel('frequency [MHz]')
    ax.set_ylabel('slant range [km]')
    ax.set_title('{} {}'.format(_expfn(fn),t))
    ax.tick_params(axis='both', which='both', direction='out')
    ax.autoscale(True,'both',tight=True)

    writeplots(fg,t,odir,makeplot,ctxt.split(' ')[0])
