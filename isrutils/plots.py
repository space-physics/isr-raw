#!/usr/bin/env python
from time import time
from six import integer_types
import h5py
from datetime import datetime
from pytz import UTC
from numpy import log10,absolute, meshgrid, sin, radians,unique
from numpy.ma import masked_invalid
from pandas import DataFrame
from xarray import DataArray
#
from matplotlib.pyplot import figure,subplots
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.dates import DateFormatter
#
from GeoData.plotting import polarplot
from histutils.findnearest import find_nearest as findnearest
from .common import expfn,timeticks,writeplots,str2dt

def plotsnr(snr,fn,P,azel,ctxt=''):
    if not isinstance(snr,DataArray):
        return

    P['tlim'] = str2dt(P['tlim'])

    assert snr.ndim==2 and snr.shape[1]>0,'you seem to have extracted zero times, look at tlim'

    fg = figure(figsize=(15,12))
    ax = fg.gca()

    #try:
    h=ax.pcolormesh(snr.time, snr.srng,
                    10*masked_invalid(log10(snr.values)),
                    vmin=P['vlim'][0], vmax=P['vlim'][1],
                    cmap='cubehelix_r')
   # except ValueError as e:
    #    print('Windows seems to wrongly get error ValueError: ordinal must be >= 1.  Your error is {}'.format(e))

    ax.autoscale(True,tight=True)

    ax.set_xlim(P['tlim'])
    ax.set_ylim(P['zlim'])

    ax.set_ylabel('slant range [km]')

    ax.set_xlabel('Time [UTC]')
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
#%% date ticks
    fg.autofmt_xdate()
    if P['tlim'][0] is None or P['tlim'][1] is None:
        tdiff = snr.time[-1] - snr.time[0]
    else:
        tdiff = P['tlim'][1] - P['tlim'][0]

    majtick,mintick = timeticks(tdiff)

    ax.xaxis.set_major_locator(majtick)
    ax.xaxis.set_minor_locator(mintick)
    ax.tick_params(axis='both', which='both', direction='out')

    c=fg.colorbar(h,ax=ax,fraction=0.075,shrink=0.5)
    c.set_label('Power [dB]')

    Ts = snr.time[1] - snr.time[0] #NOTE: assuming uniform sample time
    ax.set_title('Az,El {},{}  {}  {}  $T_{{sample}}$={:.3f} sec.'.format(azel[0],azel[1],expfn(fn),
                         str(datetime.fromtimestamp(snr.time[0].item()/1e9))[:10], Ts.item()/1e9))

    try:
      for m in P['tmark']:
        try:
            ax.annotate(m[2],m[:2],
                        xytext=(m[3]*100,50), textcoords='offset points', color='white', ha='left',
                        bbox={'alpha':.2},
                        arrowprops={'facecolor':'white',
                                    'arrowstyle':'-[',
                                    'connectionstyle':"arc3,rad=0.2"})
        except Exception as e:
            print('failed to annotate {}'.format(e))
    except KeyError:
        pass

    fg.tight_layout()
#%% output
    ofn = 'power_'+expfn(fn)+ctxt

    writeplots(fg, snr.time[0].item(), P['odir'],ofn)

    return fg


def plotsnr1d(snr,P):
    if not isinstance(snr,DataArray):
        return

    tind=absolute(snr.time-P['t0']).argmin()
    tind = range(tind-1,tind+2)
    t1 = snr.time[tind]

    S = 10*log10(snr[snr.srng >= P['zlim'][0],t1])
    z = S.index

    ax = figure().gca()
    ax.plot(S.iloc[:,0],z,color='r',label=str(t1[0]))
    ax.plot(S.iloc[:,1],z,color='k',label=str(t1[1]))
    ax.plot(S.iloc[:,2],z,color='b',label=str(t1[2]))
#    ax.set_ylim(zlim)
    ax.autoscale(True,'y',tight=True)
    ax.set_xlim(-5)
    ax.legend()

    ax.set_title(P['fn'])
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

    x,y = meshgrid(S.time.values.astype(float)/1e9,z)

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
    """
    plot PSD derived from ACF.
    """
    #%% plot axes

    fg = figure()
    ax = fg.gca()

    assert 10 <= azel[1] <= 90
    goodz = spec.srng * sin(radians(azel[1])) > 60e3 #actual altitude > 60km
    z = spec.srng[goodz].values / 1e3 #altitude over N km

    h=ax.pcolormesh(spec.freq.values,
                    z,
                    10*log10(absolute(spec[goodz,:].values)),
                    vmin=P['vlimacf'][0],
                    vmax=P['vlimacf'][1],
                    cmap='cubehelix_r')

    ytop = min(z[-1], P['zlim'][1])  if P['zlim'][1] is not None else z[-1]


    ax.set_ylim(P['zlim'][0],ytop)

    c=fg.colorbar(h,ax=ax)
    c.set_label('Power [dB]')
    ax.set_ylabel('altitude [km]')
    ax.set_title('Az,El {},{}  {} {}'.format(azel[0],azel[1], expfn(fn),str(t)[:-6]))
    ax.autoscale(True,axis='x',tight=True)
    ax.set_xlabel('frequency [kHz]')


    writeplots(fg,t,P['odir'],'acf_'+expfn(fn))
#%%

def plotplasmaline(specdown,specup,fn, P, azel):
    if not (isinstance(specdown,DataArray) or isinstance(specup,DataArray)):
        return

    tic = time()

    T = specdown.time
    assert (T==specup.time).all(),'times do not match for downshift and upshift plasma spectrum'

    ptype=None#'mesh'

    for t in T:
        if ptype in ('mesh','surf'): #cannot use subplots for 3d with matplotlib 1.4
            axs=[None,None]

            fg = figure(figsize=(15,5))
            axs[0] = fg.add_subplot(1,2,1,projection='3d')

            fg.suptitle('{} {}'.format(fn.name,t.to_pydatetime()))
        elif P['zlim_pl'] is not None and isinstance(P['zlim_pl'],(float,integer_types)): #lineplot
            fg = figure()
            plotplasmaoverlay(specdown.loc[t,:,:],specup.loc[t,:,:],t,fg,P)
            writeplots(fg,t,P['odir'],'plasmaLineOverlay')
            continue
        else: #pcolor
            fg,axs = subplots(1,2,figsize=(15,5),sharey=True)
            fg.suptitle('Az,El {},{}  Plasma line {}'.format(azel[0],azel[1],
                            str(datetime.fromtimestamp(t.item()/1e9, tz=UTC))[:-6]))
#%%
        for s,ax,fshift in zip((specdown,specup),axs,('down','up')):
            try:
                if ptype in ('mesh','surf'):
                    plotplasmamesh(s.loc[t,:,:], fg,ax,P,ptype)
                else: #pcolor
                    plotplasmatime(s.loc[t,:,:],t, fg,ax,P,fshift)
            except KeyError as e:
                print('E: {} plotting {} {}'.format(e,fshift,t))

        fg.tight_layout()

        # write plots here else you'll double write plots
        writeplots(fg,t,P['odir'],'plasmaLine')

    if P['verbose']:
        print('plasma line plot took {:.1f} sec.'.format(time()-tic))


def plotplasmaoverlay(specdown,specup,t,fg,P):

    ax = fg.gca()

    ialt,alt = findnearest(specdown.srng.values,P['zlim_pl'])

    dBdown = 10*log10(specdown[ialt,:].values)
    if len(P['vlim_pl'])>=4 and P['vlim_pl'][2] is not None:
        dBdown += P['vlim_pl'][2]

    dBup = 10*log10(specup[ialt,:].values)
    if len(P['vlim_pl'])>=4 and P['vlim_pl'][3] is not None:
        dBup += P['vlim_pl'][3]

    ax.plot(-specdown.freq.values/1e6, dBdown)

    ax.plot(specup.freq.values/1e6, dBup)

    ax.set_ylabel('Power [dB]')
    ax.set_xlabel('Doppler frequency [MHz]')

    ax.set_ylim(P['vlim_pl'][:2])
    ax.set_xlim(P['flim_pl'])

    fg.suptitle('Plasma line at {:.0f} km slant range {}'.format(alt, str(t.item)[:19]))


def plotplasmatime(spec,t,fg,ax,P,ctxt):
    if not isinstance(spec,DataArray):
        return

    srng = spec.srng.values
    zgood = srng > 60. # above N km

    h=ax.pcolormesh(spec.freq.values/1e6,srng[zgood],10*log10(spec[zgood,:].values),
                    vmin=P['vlim_pl'][0], vmax=P['vlim_pl'][1],cmap='cubehelix_r')

#    h=ax.imshow(spec.freq.values/1e6,srng[zgood],10*log10(spec[zgood,:].values),
#                    vmin=P['vlim_pl'][0], vmax=P['vlim_pl'][1],cmap='cubehelix_r')

    ax.set_xlabel('Doppler frequency [MHz]')
    if ctxt.startswith('down'):
        ax.set_ylabel('slant range [km]')

    c=fg.colorbar(h,ax=ax,format='%.0f')
    c.set_label('Power [dB]')

    ax.autoscale(True,'both',tight=True) #before manual lim setting
    ax.set_ylim(P['zlim_pl'])
#%%
    xfreq(ax,spec,P['flim_pl'])

    #ax.tick_params(axis='both', which='both', direction='out')

def xfreq(ax,spec,Pflim):
    if spec.freq.values[0] < 0 : # downshift
        flim=[None,None]
        if Pflim[0] is not None:
            flim[1] = -Pflim[0]
        if Pflim[1] is not None:
            flim[0] = -Pflim[1]
    else: #upshift
        flim = Pflim

    ax.set_xlim(flim)


def plotplasmamesh(spec,fg,ax,P,ptype=''):
    if not isinstance(spec,DataArray):
        return

    if not fg and not ax:
        fg = figure()
        ax = fg.gca()
    elif fg and not ax:
        ax = fg.gca()

    srng = spec.index.values
    zgood = srng>P['zlim'][0] # above N km

    S = 10*log10(spec.loc[zgood,:])
    z = S.index.values

    x,y = meshgrid(spec.freq.values/1e6,z)

#    ax3 = figure().gca(projection='3d')
#
#    ax3.scatter(x,y,S.values)
    if ptype==  'surf':
        ax.plot_surface(x,y,S.values,cmap='jet')
    elif ptype=='mesh':
        ax.plot_wireframe(x,y,S.values)

    ax.set_zlim(P['vlim'])
    ax.set_zlabel('Power [dB]')
    ax.set_ylabel('altitude [km]')
    ax.set_xlabel('Frequency [MHz]')
    ax.autoscale(True,'y',tight=True)
    fg.tight_layout()

def plotbeampattern(fn,P,beamkey,beamids=None):
  """
  plots beams used in the file
  """
  try:
    beamcodes = unique(beamkey)  # for some files they're jumbled

    def _pullbeams(f):
        M = f['/Setup/BeamcodeMap']

        azel =  DataFrame(index=M[:,0].astype(int),
                          columns=['az','el'],
                          data=M[:,1:3])

        date = f['/Time/RadacTimeString'][0][0][:10].decode('utf8')

        return azel,date


    if isinstance(fn,h5py.File):
        beams,date = _pullbeams(fn)
    else:
        with h5py.File(str(fn),'r',libver='latest') as f:
            beams,date = _pullbeams(f)



    fg = polarplot(beams.loc[beamcodes,'az'], beams.loc[beamcodes,'el'],
                   title='ISR {} Beam Pattern: {}'.format(beamcodes.size,date),
                   markerarea=27.4)

    print('{} beam pattern {}'.format(beamcodes.size,fn))
    writeplots(fg, odir=P['odir'], ctxt='beams_{}'.format(fn))

  except Exception as e:
      print(e)