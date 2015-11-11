#!/usr/bin/env python3
"""
reading PFISR data down to IQ samples

See README.rst for the data types this file handles.

Designed for Python 3.5+, may work with older versions.
"""
from __future__ import division
from six import integer_types
from pathlib2 import Path
from datetime import datetime,timedelta
from pytz import UTC
from dateutil.parser import parse
from numpy import (array,log10,absolute, meshgrid,empty,nonzero,zeros,zeros_like,
                   complex64,complex128,conj,append,sin,radians,linspace)
from numpy.ma import masked_invalid
from numpy.fft import fft,fftshift
import h5py
from pandas import DataFrame
from matplotlib.pyplot import figure,show,close
from matplotlib.dates import MinuteLocator,SecondLocator
from mpl_toolkits.mplot3d import Axes3D
#import seaborn as sns
#sns.color_palette(sns.color_palette("cubehelix"))
#sns.set(context='poster', style='ticks')
#sns.set(rc={'image.cmap': 'cubehelix_r'}) #for contour


def ut2dt(ut):
    if ut.ndim==1:
        T=ut
    elif ut.ndim==2:
        T=ut[:,0]
    return array([datetime.fromtimestamp(t,tz=UTC) for t in T])

def sampletime(T,Np):
    dtime = empty(Np*T.shape[0])
    i=0
    for t in T: #each row
        dt=(t[1]-t[0]) / Np
        for j in range(Np):
            dtime[i]=t[0]+j*dt
            i+=1
    return dtime

def findstride(beammat,bid):
    #FIXME is using just first row OK? other rows were identical for me.
#    Nt = beammat.shape[0]
#    index = empty((Nt,Np),dtype=int)
#    for i,b in enumerate(beammat):
#        index[i,:] = nonzero(b==bid)[0] #NOTE: candidate for np.s_ ?
    return nonzero(beammat[0,:]==bid)[0]

def samplepower(sampiq,bstride,Np,Nr,Nt):
    """
    returns I**2 + Q**2 of radar received amplitudes
    FIXME: what are sample units?
    """
    assert len(sampiq.shape) == 4 #h5py 2.5.0 doesn't have ndim, don't want .value to avoid reading whole dataset

    power = empty((Nr,Np*Nt))
    i=0
    for it in range(Nt):
        for ip in range(Np):
            power[:,i] = (sampiq[it,bstride[ip],:,0]**2 +
                          sampiq[it,bstride[ip],:,1]**2)

            i+=1

    return power

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


        spec_noise = spec_noise/ Nlag
#%% spectrum from ACF
    for i in range(Nr):
        spec[i,:] = fftshift(fft(append(conj(acf[i,1:][::-1]), acf[i,:])))-spec_noise


    return spec,acf

def readACF(fn,bid,makeplot,odir):
    """
    reads incoherent scatter radar autocorrelation function (ACF)
    """
    dns=1071/3 #todo scalefactor
    assert isinstance(fn,Path)
    assert isinstance(bid,integer_types) # a scalar integer!
    fn = fn.expanduser()

    tInd = list(range(20,30,1)) #TODO pick indices by datetime
    with h5py.File(str(fn),'r',libver='latest') as f:
        Nt = f['/Time/UnixTime'].shape[0]
        t = ut2dt(f['/Time/UnixTime'].value)
        ft = ftype(fn)
        if ft == 'dt3':
            rk = '/S/'
            noiseall = f[rk+'Noise/Acf/Data']
        elif ft == 'dt0':
            rk = '/IncohCodeFl/'
            s=f[rk+'Data/Acf/Data'].shape
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
            plotacf(specdf,fn,azel,t[tInd[i]],tlim=p.tlim,vlim=vlim,ctxt='dB',
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
    ax.set_title('{} {}'.format(_expfn(fn),t))
    ax.autoscale(True,'both',tight=True)

    if 'png' in makeplot:
        ppth = odir/(t.strftime('%Y-%m-%dT%H:%M:%S')+'.png')
        print('saving {}'.format(ppth))
        fg.savefig(str(ppth),dpi=100,bbox_inches='tight')

    if not 'show' in makeplot:
        close(fg)


def readpower_samples(fn,bid):
    """
    reads samples (lowest level data) and computes power for a particular beam.
    returns a Pandas DataFrame containing power measurements
    """
    assert isinstance(fn,Path)
    assert isinstance(bid,integer_types) # a scalar integer!
    fn = fn.expanduser()

    with h5py.File(str(fn),'r',libver='latest') as f:
        Nt = f['/Time/UnixTime'].shape[0]
        Np = f['/Raw11/Raw/PulsesIntegrated'][0,0] #FIXME is this correct in general?
        ut = sampletime(f['/Time/UnixTime'],Np)
        srng  = f['/Raw11/Raw/Power/Range'].value.squeeze()/1e3
        bstride = findstride(f['/Raw11/Raw/RadacHeader/BeamCode'],bid)
        power = samplepower(f['/Raw11/Raw/Samples/Data'],bstride,Np,srng.size,Nt) #I + jQ   # Ntimes x striped x alt x real/comp

    t = ut2dt(ut)
    return DataFrame(index=srng, columns=t, data=power)


def readsnr_int(fn,bid):
    assert isinstance(fn,Path)
    fn = fn.expanduser()

    with h5py.File(str(fn),'r',libver='latest') as f:
        t = ut2dt(f['/Time/UnixTime'].value) #yes .value is needed for .ndim
        bind  = f['/Raw11/Raw/Beamcodes'][0,:] == bid
        power = f['/Raw11/Raw/Power/Data'][:,bind,:].squeeze().T
        srng  = f['/Raw11/Raw/Power/Range'].value.squeeze()/1e3
#%% return requested beam data only
    return DataFrame(index=srng,columns=t,data=power)

def snrvtime_fit(fn,bid):
    assert isinstance(fn,Path)
    fn = fn.expanduser()

    with h5py.File(str(fn),'r',libver='latest') as f:
        t = ut2dt(f['/Time/UnixTime'].value)
        bind = f['/BeamCodes'][:,0] == bid
        snr = f['/NeFromPower/SNR'][:,bind,:].squeeze().T
        z = f['/NeFromPower/Altitude'][bind,:].squeeze()/1e3
#%% return requested beam data only
    return DataFrame(index=z,columns=t,data=snr)

def plotsnr(snr,fn,tlim=None,vlim=(None,None),zlim=(90,None),ctxt=''):
    assert isinstance(snr,DataFrame)

    fg = figure(figsize=(10,12))
    ax =fg.gca()
    h=ax.pcolormesh(snr.columns.values,snr.index.values,
                     10*log10(masked_invalid(snr.values)),
                     vmin=vlim[0], vmax=vlim[1],cmap='cubehelix_r')
    ax.autoscale(True,tight=True)

    ax.set_xlim(tlim)
    ax.set_ylim(zlim)

    ax.set_ylabel('altitude [km]')
    ax.set_xlabel('Time [UTC]')
#%% date ticks
    fg.autofmt_xdate()
    if tlim:
        tlim[0],tlim[1] = parse(tlim[0]), parse(tlim[1])
        tdiff = tlim[1]-tlim[0]
    else:
        tdiff = snr.columns[-1] - snr.columns[0]

    if tdiff>timedelta(minutes=20):
        ticker = MinuteLocator(interval=5)
    elif (timedelta(minutes=1)<tdiff) & (tdiff<=timedelta(minutes=20)):
        ticker = MinuteLocator(interval=1)
    else:
        ticker = SecondLocator(interval=5)

    ax.xaxis.set_major_locator(ticker)
    ax.tick_params(axis='both', which='both', direction='out')

    c=fg.colorbar(h,ax=ax,fraction=0.075,shrink=0.5)
    c.set_label(ctxt)

    ts = snr.columns[1] - snr.columns[0]
    ax.set_title('{}  {}  $T_{{sample}}$={:.3f} sec.'.format(_expfn(fn), snr.columns[0].strftime('%Y-%m-%d'),ts.total_seconds()))


    #last command
    fg.tight_layout()

def _expfn(fn):
    """
    returns text string based on file suffix
    """
    if fn.name.endswith('.dt0.h5'):
        return 'alternating code'
    elif fn.name.endswith('.dt1.h5'):
        return 'downnshifted plasma line'
    elif fn.name.endswith('.dt2.h5'):
        return 'upshifted plasma line'
    elif fn.name.endswith('.dt3.h5'):
        return 'long pulse'


def plotsnr1d(snr,fn,t0,zlim=(90,None)):
    assert isinstance(snr,DataFrame)
    tind=absolute(snr.columns-t0).argmin()
    tind = range(tind-1,tind+2)
    t1 = snr.columns[tind]

    S = 10*log10(snr.loc[snr.index>=zlim[0],t1])
    z = S.index

    ax = figure().gca()
    ax.plot(S.iloc[:,0],z,color='r')
    ax.plot(S.iloc[:,1],z,color='k')
    ax.plot(S.iloc[:,2],z,color='b')
#    ax.set_ylim(zlim)
    ax.autoscale(True,'y',tight=True)
    ax.set_xlim(-5)

    ax.set_title(fn.name)
    ax.set_xlabel('SNR [dB]')
    ax.set_ylabel('altitude [km]')

def plotsnrmesh(snr,fn,t0,vlim,zlim=(90,None)):
    assert isinstance(snr,DataFrame)
    tind=absolute(snr.columns-t0).argmin()
    tind=range(tind-5,tind+6)
    t1 = snr.columns[tind]

    S = 10*log10(snr.loc[snr.index>=zlim[0],t1])
    z = S.index

    x,y = meshgrid(S.columns.values.astype(float),z)

    ax3 = figure().gca(projection='3d')

#    ax3.plot_wireframe(x,y,S.values)
#    ax3.scatter(x,y,S.values)
    ax3.plot_surface(x,y,S.values,cmap='jet')
    ax3.set_zlim(vlim)
    ax3.set_zlabel('SNR [dB]')
    ax3.set_ylabel('altitude [km]')
    ax3.set_xlabel('time')
    ax3.autoscale(True,'y',tight=True)

def ftype(fn):
    return fn.name.split('.')[1]

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='demo of loading raw ISR data')
    p.add_argument('fn',help='HDF5 file to read')
    p.add_argument('--t0',help='time to extract 1-D vertical plot')
    p.add_argument('--acf',help='show autocorrelation function (ACF)',action='store_true')
    p.add_argument('--samples',help='use raw samples (lowest level data commnoly available)',action='store_true')
    p.add_argument('--beamid',help='beam id 64157 zenith beam',type=int,default=64157)
    p.add_argument('--vlim',help='min,max for SNR plot [dB]',type=float,nargs=2)
    p.add_argument('--zlim',help='min,max for altitude [km]',type=float,nargs=2,default=(90,None))
    p.add_argument('--tlim',help='min,max time range yyyy-mm-ddTHH:MM:SSz',nargs=2)
    p.add_argument('-m','--makeplot',help='png to write pngs',nargs='+',default=['show'])
    p.add_argument('-o','--odir',help='directory to write files to',default='')
    p = p.parse_args()

#%%
    fn = Path(p.fn).expanduser()
    odir = Path(p.odir).expanduser()

#%% raw (lowest common level)
    if ftype(fn) in ('dt0','dt3') and p.samples:
        vlim = p.vlim if p.vlim else (32,60)
        snrsamp = readpower_samples(fn,p.beamid)
        plotsnr(snrsamp,fn,tlim=p.tlim,vlim=vlim,ctxt='Power [dB]')
    elif ftype(fn) in ('dt0','dt3') and p.acf:
        vlim = p.vlim if p.vlim else (20,45)
        readACF(fn,p.beamid,p.makeplot,odir)
#%% 12 second (numerous integrated pulses)
    elif ftype(fn) in ('dt0','dt3'):
        vlim = p.vlim if p.vlim else (47,70)
        snr12sec = readsnr_int(fn,p.beamid)
        plotsnr(snr12sec,fn,vlim=vlim,ctxt='SNR [dB]')
#%% 30 second integegration plots
    else:
        vlim = p.vlim if p.vlim else (-20,None)
        snr = snrvtime_fit(fn,p.beamid)

        if p.t0:
            plotsnr1d(snr,fn,p.t0,p.zlim)
        plotsnr(snr,fn,p.tlim,vlim)
        plotsnrmesh(snr,fn,p.t0,vlim,p.zlim)

    show()
