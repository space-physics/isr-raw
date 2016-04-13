from pathlib import Path
import h5py
from pandas import DataFrame
from numpy import (empty,zeros,complex64,complex128,conj,append,sin,radians,linspace,
                   log10,absolute)
from numpy.fft import fft,fftshift
from matplotlib.pyplot import figure,close
#
from .common import ftype,ut2dt,findstride,expfn,writeplots

def compacf(acfall,noiseall,Nr,dns,bstride,ti,tInd):
    bstride=bstride.squeeze()
    assert bstride.size==1 #TODO

    Nlag = acfall.shape[2]
    acf  =      zeros((Nr,Nlag),complex64) #NOT empty, note complex64 is single complex float
    spec =      empty((Nr,2*Nlag-1),complex128)
    try:
        acf_noise = zeros((noiseall.shape[3],Nlag),complex64)
        spec_noise= zeros(2*Nlag-1,complex128)
    except AttributeError:
        acf_noise = None
        spec_noise= 0.

    for i in range(tInd[ti]-1,tInd[ti]+1):
        acf += (acfall[i,bstride,:,:,0] + 1j*acfall[i,bstride,:,:,1]).T
        if acf_noise is not None: #must be is not None
            acf_noise += (noiseall[i,bstride,:,:,0] + 1j*noiseall[i,bstride,:,:,1]).T

    acf = acf/dns/(i-(tInd[ti]-1)+1) #NOT /=
    if acf_noise is not None: #must be is not None
        acf_noise = acf_noise/dns / (i-(tInd[ti]-1)+1)
#%% spectrum noise
    if acf_noise is not None:
        for i in range(Nlag):
            spec_noise += fftshift(fft(append(conj(acf_noise[i,1:][::-1]),acf_noise[i,:])))


        spec_noise = spec_noise / Nlag
#%% spectrum from ACF
    for i in range(Nr):
        spec[i,:] = fftshift(fft(append(conj(acf[i,1:][::-1]), acf[i,:])))-spec_noise


    return spec,acf

def readACF(fn,bid,makeplot,odir,tlim=(None,None),vlim=(None,None)):
    """
    reads incoherent scatter radar autocorrelation function (ACF)
    """
    dns=1071/3 #todo scalefactor
    fn = Path(fn).expanduser()
    assert isinstance(bid,int) # a scalar integer!
    fn = fn.expanduser()

    tInd = list(range(20,30,1)) #TODO pick indices by datetime
    with h5py.File(str(fn),'r',libver='latest') as f:
        t = ut2dt(f['/Time/UnixTime'].value)
        ft = ftype(fn)
        if ft == 'dt3':
            rk = '/S/'
            noiseall = f[rk+'Noise/Acf/Data']
        elif ft == 'dt0':
            rk = '/IncohCodeFl/'
            noiseall = None #TODO hack for dt0
        else:
            raise TypeError('unexpected file type {}'.format(ft))

        srng = f[rk + 'Data/Acf/Range'].value.squeeze()
        bstride = findstride(f[rk+'Data/Beamcodes'],bid)
        bcodemap = DataFrame(index=f['/Setup/BeamcodeMap'][:,0].astype(int),
                             columns=['az','el'],
                             data=f['/Setup/BeamcodeMap'][:,1:3])
        azel = bcodemap.loc[bid,:]

        for i in range(len(tInd)):
            spectrum,acf = compacf(f[rk+'Data/Acf/Data'],noiseall,
                               srng.size,dns,bstride,i,tInd)
            specdf = DataFrame(index=srng,data=spectrum)

            plotacf(specdf,fn,azel,t[tInd[i]],tlim=tlim,vlim=vlim,ctxt='dB',
                    makeplot=makeplot,odir=odir)

def plotacf(spec,fn,azel,t,tlim=(None,None),vlim=(None,None),ctxt='',makeplot=[],odir=''):
    #%% plot axes
    goodz =spec.index.values*sin(radians(azel['el'])) > 60e3
    z = spec.index[goodz].values/1e3 #altitude over N km
    xfreq = linspace(-100/6,100/6,spec.shape[1]) #kHz

    fg = figure()
    ax = fg.gca()
    h=ax.pcolormesh(xfreq,z,10*log10(absolute(spec.values[goodz,:])),
                  vmin=vlim[0],vmax=vlim[1],cmap='cubehelix_r')
    c=fg.colorbar(h,ax=ax)
    c.set_label(ctxt)
    ax.set_xlabel('frequency [kHz]')
    ax.set_ylabel('altitude [km]')
    ax.set_title('{} {}'.format(expfn(fn),t))
    ax.autoscale(True,'both',tight=True)

    writeplots(fg,t,odir,makeplot)

    if not 'show' in makeplot:
        close(fg)
