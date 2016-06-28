#!/usr/bin/env python
from datetime import datetime
from dateutil.parser import parse
from numpy import log10,absolute, meshgrid
from numpy.ma import masked_invalid
from xarray import DataArray
#
from matplotlib.pyplot import figure
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.dates import SecondLocator, DateFormatter
#
from .common import expfn,timeticks

def plotsnr(snr,fn,tlim=None,vlim=(None,None),zlim=(90,None),ctxt=''):
    if not isinstance(snr,DataArray):
        return


    assert snr.ndim==2 and snr.shape[1]>0,'you seem to have extracted zero times, look at tlim'

    fg = figure(figsize=(15,12))
    ax =fg.gca()
    h=ax.pcolormesh(snr.time, snr.srng,
                     10*masked_invalid(log10(snr.values)),
                     vmin=vlim[0], vmax=vlim[1],cmap='jet')
    ax.autoscale(True,tight=True)

    ax.set_xlim(tlim)
    ax.set_ylim(zlim)

    ax.set_ylabel('slant range [km]')

    ax.set_xlabel('Time [UTC]')
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
#%% date ticks
    fg.autofmt_xdate()
    if tlim is None or tlim[0] is None:
        tdiff = snr.time[-1] - snr.time[0]
    else:
        if isinstance(tlim[0],str):
            tlim[0],tlim[1] = parse(tlim[0]), parse(tlim[1])
            tdiff = tlim[1]-tlim[0]
        elif isinstance(tlim[0],datetime):
            tdiff = tlim[1]-tlim[0]

    ticker = timeticks(tdiff)

    ax.xaxis.set_major_locator(ticker)
    ax.tick_params(axis='both', which='both', direction='out')

    c=fg.colorbar(h,ax=ax,fraction=0.075,shrink=0.5)
    c.set_label(ctxt)

    Ts = snr.time[1] - snr.time[0] #NOTE: assuming uniform sample time
    ax.set_title('{}  {}  $T_{{sample}}$={:.3f} sec.'.format(expfn(fn),
                 datetime.utcfromtimestamp(snr.time[0].item()/1e9).strftime('%Y-%m-%d'),
                 Ts.item()/1e9))


    #last command
    fg.tight_layout()

def plotsnr1d(snr,fn,t0,zlim=(90,None)):
    assert isinstance(snr,DataArray)
    tind=absolute(snr.time-t0).argmin()
    tind = range(tind-1,tind+2)
    t1 = snr.time[tind]

    S = 10*log10(snr[snr.srng>=zlim[0],t1])
    z = S.index

    ax = figure().gca()
    ax.plot(S.iloc[:,0],z,color='r',label=str(t1[0]))
    ax.plot(S.iloc[:,1],z,color='k',label=str(t1[1]))
    ax.plot(S.iloc[:,2],z,color='b',label=str(t1[2]))
#    ax.set_ylim(zlim)
    ax.autoscale(True,'y',tight=True)
    ax.set_xlim(-5)
    ax.legend()

    ax.set_title(fn.name)
    ax.set_xlabel('SNR [dB]')
    ax.set_ylabel('altitude [km]')

def plotsnrmesh(snr,fn,t0,vlim,zlim=(90,None)):
    assert isinstance(snr,DataArray)
    tind=absolute(snr.time-t0).argmin()
    tind=range(tind-5,tind+6)
    t1 = snr.time[tind]

    S = 10*log10(snr[snr.srng>=zlim[0],t1])
    z = S.index

    x,y = meshgrid(S.time.values.astype(float),z)

    ax3 = figure().gca(projection='3d')

#    ax3.plot_wireframe(x,y,S.values)
#    ax3.scatter(x,y,S.values)
    ax3.plot_surface(x,y,S.values,cmap='jet')
    ax3.set_zlim(vlim)
    ax3.set_zlabel('SNR [dB]')
    ax3.set_ylabel('altitude [km]')
    ax3.set_xlabel('time')
    ax3.autoscale(True,'y',tight=True)