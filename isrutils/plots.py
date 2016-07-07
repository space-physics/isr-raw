#!/usr/bin/env python
from datetime import datetime
from dateutil.parser import parse
from numpy import log10,absolute, meshgrid, sin, radians
from numpy.ma import masked_invalid
from xarray import DataArray
#
from matplotlib.pyplot import figure,subplots
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.dates import SecondLocator, DateFormatter
#
from .common import expfn,timeticks,writeplots

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
    if not isinstance(snr,DataArray):
        return

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

def plotsnrmesh(snr,fn,P):
    if not isinstance(snr,DataArray):
        return

    tind=absolute(snr.time-P['t0']).argmin()
    tind=range(tind-5,tind+6)
    t1 = snr.time[tind]

    S = 10*log10(snr[snr.srng >= P['zlim'][0],t1])
    z = S.index

    x,y = meshgrid(S.time.values.astype(float),z)

    ax3 = figure().gca(projection='3d')

#    ax3.plot_wireframe(x,y,S.values)
#    ax3.scatter(x,y,S.values)
    ax3.plot_surface(x,y,S.values,cmap='jet')
    ax3.set_zlim(P['vlim'])
    ax3.set_zlabel('SNR [dB]')
    ax3.set_ylabel('altitude [km]')
    ax3.set_xlabel('time')
    ax3.autoscale(True,'y',tight=True)


def plotacf(spec,fn,azel,t,P,ctxt=''):
    #%% plot axes
    goodz = spec.srng * sin(radians(azel.loc['el'])) > 60e3 #actual altitude > 60km
    z = spec.srng[goodz].values / 1e3 #altitude over N km

    fg = figure()
    ax = fg.gca()
    h=ax.pcolormesh(spec.freq.values,z,10*log10(absolute(spec[goodz,:].values)),
                                                         vmin=P['vlimacf'][0],
                                                         vmax=P['vlimacf'][1],
                                                         cmap='jet')#cmap='cubehelix_r')

    if P['zlim'][1] is not None:
        ytop = min(z[-1], P['zlim'][1])

    ax.set_ylim(P['zlim'][0],ytop)

    c=fg.colorbar(h,ax=ax)
    c.set_label(ctxt)
    ax.set_xlabel('frequency [kHz]')
    ax.set_ylabel('altitude [km]')
    ax.set_title('{} {}'.format(expfn(fn),t.strftime('%Y-%m-%dT%H:%M:%S')))
    ax.autoscale(True,axis='x',tight=True)

    writeplots(fg,t,P['odir'],P['makeplot'])

def plotplasmaline(spec,Freq,fn, tlim=None,vlim=(None,None),zlim=(None,None),makeplot=[],odir=''):
    if not isinstance(spec,DataArray):
        return

    ptype=None#'mesh'
    Nshift = spec.freqshift.size

    for t in spec.time:
        if ptype in ('mesh','surf'): #cannot use subplots for 3d with matplotlib 1.4
            axs=[None,None]

            fg = figure(figsize=(15,5))
            axs[0] = fg.add_subplot(1,Nshift,1,projection='3d')
            if Nshift>1:
                axs[1] = fg.add_subplot(1,Nshift,2,projection='3d')

            fg.suptitle('{} {}'.format(fn.name,t.to_pydatetime()))
        else: #pcolor
            fg,axs = subplots(1,Nshift,figsize=(15,5),sharey=True)

        if Nshift == 1:
            axs = [axs]
#%%
        for s,ax,F in zip(spec.freqshift,axs,Freq.freqshift):
            if ptype in ('mesh','surf'):
                plotplasmamesh(spec.loc[s,t,:,:],Freq.loc[:,F].values,fg,ax,vlim,zlim,ptype)
            else: #pcolor
                plotplasmatime(spec.loc[s,t,:,:],Freq.loc[:,F].values,t,fn,
                               fg,ax,tlim,vlim,s,makeplot)

        writeplots(fg,t,odir,makeplot,'plasmaLine')

def plotplasmatime(spec,freq,t,fn,fg,ax,tlim,vlim,ctxt,makeplot):
    if not isinstance(spec,DataArray):
        return

    if not fg and not ax:
        fg = figure()
        ax = fg.gca()
        isown = False
    elif fg and not ax:
        ax = fg.gca()
        isown = False
    else:
        isown = True

    srng = spec.srng.values
    zgood = srng > 60. # above N km

    h=ax.pcolormesh(freq/1e6,srng[zgood],10*log10(spec[zgood,:].values),
                    vmin=vlim[0],vmax=vlim[1],cmap='jet')#'cubehelix_r')

    if not isown or ctxt.item().startswith('down'):
        ax.set_ylabel('slant range [km]')

    c=fg.colorbar(h,ax=ax)
    c.set_label('Power [dB]')

    ax.set_xlabel('Doppler frequency [MHz]')
    ax.set_title('{} {}'.format(expfn(fn), datetime.fromtimestamp(t.item()/1e9)))
    ax.tick_params(axis='both', which='both', direction='out')
    ax.autoscale(True,'both',tight=True)
    fg.tight_layout()

def plotplasmamesh(spec,freq,fg,ax,vlim,zlim=(90,None),ptype=''):
    if not isinstance(spec,DataArray):
        return

    if not fg and not ax:
        fg = figure()
        ax = fg.gca()
    elif fg and not ax:
        ax = fg.gca()

    srng = spec.index.values
    zgood = srng>zlim[0] # above N km

    S = 10*log10(spec.loc[zgood,:])
    z = S.index.values

    x,y = meshgrid(freq/1e6,z)

#    ax3 = figure().gca(projection='3d')
#
#    ax3.scatter(x,y,S.values)
    if ptype==  'surf':
        ax.plot_surface(x,y,S.values,cmap='jet')
    elif ptype=='mesh':
        ax.plot_wireframe(x,y,S.values)

    ax.set_zlim(vlim)
    ax.set_zlabel('Power [dB]')
    ax.set_ylabel('altitude [km]')
    ax.set_xlabel('Frequency [MHz]')
    ax.autoscale(True,'y',tight=True)
    fg.tight_layout()
