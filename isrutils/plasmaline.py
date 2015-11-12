from __future__ import division, absolute_import
from six import integer_types
from pathlib2 import Path
from numpy import log10,nonzero
import h5py
from pandas import Panel4D,DataFrame
from matplotlib.pyplot import figure,subplots
#
from .common import findstride,ut2dt,_expfn,writeplots

def readplasmaline(fn,beamid,makeplot,odir,tlim,vlim):
    assert isinstance(fn,Path)
    assert isinstance(beamid,integer_types) # a scalar integer!
    fn = fn.expanduser()

    fiter = (('dt1',-5e6),('dt2',5e6))
    dshift = ['downshift','upshift']
    spec = None


    for F,s in zip(fiter,dshift):
        filename = fn.parent / (fn.name.split('.')[0] + '.' + F[0] + '.h5')
        with h5py.File(str(filename),'r',libver='latest') as f:
            T     = ut2dt(f['/Time/UnixTime'].value)
            bind  = findstride(f['/PLFFTS/Data/Beamcodes'], beamid)
            data = f['/PLFFTS/Data/Spectra/Data'][:,bind,:,:].squeeze().T
            srng  = f['/PLFFTS/Data/Spectra/Range'].value.squeeze()/1e3
            freq  = f['/PLFFTS/Data/Spectra/Frequency'].value.squeeze() + F[1]
    #%% spectrum compute
        if tlim:
            tind = nonzero((tlim[0] <= T) & (T<=tlim[1]))[0]
        else:
            tind = range(len(T))

        if spec is None:
            spec = Panel4D(labels=dshift,items=T[tind],
                       major_axis=srng,minor_axis=range(freq.size))
            Freq = DataFrame(columns=dshift)
        Freq[s] = freq

        for ti,t in zip(tind,T[tind]):
            for i,r in enumerate(srng):
                spec.loc[s,t,r,:] = data[i,:,ti]

    return spec,Freq


def plotplasmaline(spec,Freq,fn, tlim=(None,None),vlim=(None,None),makeplot=[],odir=''):

    for t in spec.items:
        fg,axs = subplots(1,2,figsize=(15,5),sharey=True)
        for s,ax,F in zip(spec,axs,Freq):
            plotplasmatime(spec.loc[s,t,:,:],Freq[F].values,t.to_pydatetime(),fn,fg,ax,tlim,vlim,s,makeplot,odir)

        writeplots(fg,t,odir,makeplot,s.split(' ')[0])

def plotplasmatime(spec,freq,t,fn,fg,ax,tlim,vlim,ctxt,makeplot,odir):

    if not fg and not ax:
        fg = figure()
        ax = fg.gca()
    elif fg and not ax:
        ax = fg.gca()

    srng = spec.index.values

    zgood = srng>60 # above N km

    h=ax.pcolormesh(freq/1e6,srng[zgood],10*log10(spec.values[zgood,:]),
                    vmin=vlim[0],vmax=vlim[1],cmap='jet')#'cubehelix_r')

    if ctxt.startswith('down'):
        ax.set_ylabel('slant range [km]')
    else:
        c=fg.colorbar(h,ax=ax)
        c.set_label('Power [dB]')

    ax.set_xlabel('Doppler frequency [MHz]')
    ax.set_title('{} {}'.format(_expfn(fn),t))
    ax.tick_params(axis='both', which='both', direction='out')
    ax.autoscale(True,'both',tight=True)
    fg.tight_layout()
