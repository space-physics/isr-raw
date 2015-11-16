from __future__ import division,absolute_import
from pathlib2 import Path
from six import integer_types
from dateutil.parser import parse
from numpy import (log10,absolute, meshgrid,empty,nonzero)
from numpy.ma import masked_invalid
import h5py
from pandas import DataFrame
from matplotlib.pyplot import figure
from mpl_toolkits.mplot3d import Axes3D
#
from .common import ut2dt,findstride,_expfn,sampletime,timeticks

def samplepower(sampiq,bstride,Np,ut,srng,tlim,zlim):
    """
    returns I**2 + Q**2 of radar received amplitudes
    FIXME: what are sample units?

    I can't index by stride and slant range simultaneously, since h5py 2.5 says
    Only one indexing vector or array is currently allowed for advanced selection
    """
    assert len(sampiq.shape) == 4 #h5py 2.5.0 doesn't have ndim, don't want .value to avoid reading whole dataset
    assert isinstance(zlim[0],float) and isinstance(zlim[1],float),'you must specify altitude summation limits --zlim'

    Nr = srng.size
    zind = (zlim[0] <= srng) & (srng <= zlim[1])
    srng = srng[zind]

    Nt = ut.size
#%% load only small bits of the hdf5 file, using advanced indexing. So fast!
    power = empty((Nr,Nt))
    for it in range(Nt//Np):
        power[:,Np*it:Np*(it+1)] = (sampiq[it,bstride,:,0]**2 +
                                    sampiq[it,bstride,:,1]**2).T
#%% NOTE: could also index by read, start with pulse batch before request and end with batch after last request.
    t = ut2dt(ut)
    if tlim[0] is not None and tlim[1] is not None:
        tind = (tlim[0]<=t) & (t<=tlim[1])
        t = t[tind]
        power = power[:,tind]

    return DataFrame(index=srng, columns=t, data=power[zind,:])

def readpower_samples(fn,bid,tlim,zlim):
    """
    reads samples (lowest level data) and computes power for a particular beam.
    returns a Pandas DataFrame containing power measurements
    """
    assert isinstance(fn,Path)
    assert isinstance(bid,integer_types) # a scalar integer!
    fn = fn.expanduser()

    with h5py.File(str(fn),'r',libver='latest') as f:
#        Nt = f['/Time/UnixTime'].shape[0]
        lla = (f['/Site/Latitude'].value,f['/Site/Longitude'].value,f['/Site/Altitude'].value)
        Np = f['/Raw11/Raw/PulsesIntegrated'][0,0] #FIXME is this correct in general?
        ut = sampletime(f['/Time/UnixTime'],Np)
        srng  = f['/Raw11/Raw/Power/Range'].value.squeeze()/1e3
        bstride = findstride(f['/Raw11/Raw/RadacHeader/BeamCode'],bid)
        power = samplepower(f['/Raw11/Raw/Samples/Data'],bstride,Np,ut,srng,tlim,zlim) #I + jQ   # Ntimes x striped x alt x real/comp
#%% return az,el of this beam
        azelrow = f['/Setup/BeamcodeMap'][:,0] == bid
        azel = f['/Setup/BeamcodeMap'][azelrow,1:3].squeeze()

    return power,azel,lla


def readsnr_int(fn,bid):
    assert isinstance(fn,Path)
    assert isinstance(bid,integer_types) # a scalar integer!
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

    ticker = timeticks(tdiff)

    ax.xaxis.set_major_locator(ticker)
    ax.tick_params(axis='both', which='both', direction='out')

    c=fg.colorbar(h,ax=ax,fraction=0.075,shrink=0.5)
    c.set_label(ctxt)

    ts = snr.columns[1] - snr.columns[0]
    ax.set_title('{}  {}  $T_{{sample}}$={:.3f} sec.'.format(_expfn(fn), snr.columns[0].strftime('%Y-%m-%d'),ts.total_seconds()))


    #last command
    fg.tight_layout()

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
