#!/usr/bin/env python
from pathlib import Path
import logging
from sys import stderr
from time import time
import h5py
from datetime import datetime
import numpy as np
from numpy.ma import masked_invalid
import xarray
from matplotlib.pyplot import figure, subplots, gcf
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.dates import DateFormatter
from matplotlib.pyplot import draw, pause, show
from matplotlib.colors import LogNorm
from matplotlib.cm import jet
import matplotlib.animation as anim
import matplotlib.gridspec as gridspec
import pathvalidate
import isrutils
from GeoData.plotting import polarplot
from sciencedates import find_nearest as findnearest
# from sciencedates.ticks import timeticks
from GeoData.plotting import plotazelscale
from .common import findindex2Dsphere, timesync, projectisrhist


ALTMIN = 60e3  # meters


def writeplots(fg, t='', odir=None, ctxt='', ext='.png'):
    from matplotlib.pyplot import close

    if odir:
        odir = Path(odir).expanduser()
        odir.mkdir(parents=True, exist_ok=True)

        if isinstance(t, xarray.DataArray):
            t = datetime.utcfromtimestamp(t.item()/1e9)
        elif isinstance(t, (float, int)):
            t = datetime.utcfromtimestamp(t/1e9)

        # :-6 keeps up to millisecond if present.
        ppth = odir / pathvalidate.sanitize_filename(ctxt + str(t)[:-6] + ext, '-').replace(' ', '')

        print('saving', ppth)

        fg.savefig(ppth, dpi=100, bbox_inches='tight')

        close(fg)

# %% joint isr optical plot


def dojointplot(ds, spec, freq, beamazel, optical, optazel, optlla, isrlla, heightkm, utopt, P):
    """
    ds: radar data

    f1,a1: radar   figure,axes
    f2,a2: optical figure,axes
    """
    vidnorm = LogNorm()

    assert isinstance(ds, xarray.DataArray)

# %% setup master figure
    fg = figure(figsize=(8, 12))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
# %% setup radar plot(s)
    a1 = fg.add_subplot(gs[1])
    plotsumionline(ds, a1, isrutils.expfn(P['isrfn']), P['zlim'])

    h1 = a1.axvline(np.nan, color='k', linestyle='--')
    t1 = a1.text(0.05, 0.95, 'time=', transform=a1.transAxes, va='top', ha='left')
# %% setup top optical plot
    if optical is not None:
        a0 = fg.add_subplot(gs[0])
        clim = compclim(optical, lower=10, upper=99.99)
        h0 = a0.imshow(optical[0, ...], origin='lower', interpolation='none', cmap='gray',
                       norm=vidnorm, vmin=clim[0], vmax=clim[1])
        a0.set_axis_off()
        t0 = a0.set_title('')

# %% plot magnetic zenith beam
        azimg = optazel[:, 1].reshape(optical.shape[1:])
        elimg = optazel[:, 2].reshape(optical.shape[1:])

        optisrazel = projectisrhist(isrlla, beamazel, optlla, optazel, heightkm)

        br, bc = findindex2Dsphere(azimg, elimg, optisrazel['az'], optisrazel['el'])

        # hollow beam circle
    #    a2.scatter(bc,br,s=500,marker='o',facecolors='none',edgecolor='red', alpha=0.5)

        # beam data, filled circle
        s0 = a0.scatter(bc, br, s=2700, alpha=0.6, linewidths=3,
                        edgecolors=jet(np.linspace(ds.min().item(), ds.max().item())))

        a0.autoscale(True, tight=True)
        fg.tight_layout()
# %% time sync
    tisr = ds.time.values
    Iisr, Iopt = timesync(tisr, utopt, P['tlim'])
# %% iterate
    first = True
    Writer = anim.writers['ffmpeg']
    writer = Writer(fps=5,
                    metadata=dict(artist='Michael Hirsch, Ph.D.'),
                    codec='ffv1')

    ofn = Path(P['odir']).expanduser() / ('joint_' +
                                          pathvalidate.sanitize_filename(str(datetime.fromtimestamp(utopt[0]))[:-3]) + '.mkv')

    print(f'writing {ofn}')
    with writer.saving(fg, str(ofn), 150):
        for iisr, iopt in zip(Iisr, Iopt):
            ctisr = tisr[iisr]
# %% update isr plot
            h1.set_xdata(ctisr)
            t1.set_text('isr: {}'.format(ctisr))
# %% update hist plot
            if iopt is not None:
                ctopt = datetime.utcfromtimestamp(utopt[iopt])
                h0.set_data(optical[iopt, ...])
                t0.set_text('optical: {}'.format(ctopt))
                s0.set_array(ds.loc[ctisr])  # FIXME circle not changing magnetic zenith beam color? NOTE this is isr time index
# %% anim
            if first and iopt is not None:
                plotazelscale(optical[iopt, ...], azimg, elimg)
                show()
                first = False
            #
            draw()
            pause(0.01)

            writer.grab_frame(facecolor='k')

            if ofn.suffix == '.png':
                try:
                    writeplots(fg, ctopt, ofn, ctxt='joint')
                except UnboundLocalError:
                    writeplots(fg, ctisr, ofn, ctxt='isr')


def compclim(imgs, lower: float=0.5, upper: float=99.9, Nsamples: int=50):
    """
    inputs:
    images: Nframe x ypix x xpix grayscale image stack (have not tried with 4-D color)
    lower,upper: percentage (0,100)% to clip
    Nsamples: number of frames to test across the image stack (don't use too many for memory reasons)
    """
    sampind = np.linspace(0, imgs.shape[0], Nsamples, endpoint=False, dtype=int)

    clim = np.percentile(imgs[sampind, ...], [lower, upper])
    if upper == 100.:
        clim[1] = imgs.max()  # consider all images
    return clim


def plotsnr(snr, fn, P, azel, ctxt=''):
    if not isinstance(snr, xarray.DataArray) or min(snr.shape) < 2:
        return

    P['tlim'] = isrutils.str2dt(P['tlim'])

    if 'int' in ctxt:
        vlim = P['vlimint']
    else:
        vlim = P['vlim']

    assert snr.ndim == 2 and snr.shape[1] > 0, f'you seem to have extracted zero times, look at tlim {P["tlim"]}'

    fg = figure()  # figsize=(30,12))
    ax = fg.gca()

    try:
        h = ax.pcolormesh(snr.time, snr.srng,
                          10*masked_invalid(np.log10(snr.values)),
                          vmin=vlim[0], vmax=vlim[1],
                          cmap='cubehelix_r')
    except ValueError as e:
        print(e, file=stderr)
        return

    ax.autoscale(True, tight=True)

    ax.set_xlim(P['tlim'])
    ax.set_ylim(P['zlim'])

    ax.set_ylabel('slant range [km]')

    ax.set_xlabel('Time [UTC]')
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
# %% date ticks
    fg.autofmt_xdate()

    # tdiff = snr.time[-1] - snr.time[0]

    # majtick,mintick = timeticks(tdiff)
    # ax.xaxis.set_major_locator(majtick)
    # ax.xaxis.set_minor_locator(mintick)
    ax.tick_params(axis='both', which='both', direction='out')

    c = fg.colorbar(h, ax=ax, fraction=0.075, shrink=0.5)
    c.set_label('Power [dB]')

    # Ts = f'{(snr.time[1] - snr.time[0]).item()/1e9:.3f}' if snr.time.size >= 2 else ''

    ax.set_title(f'Az,El {azel[0]:.1f},{azel[1]:.1f}  {isrutils.expfn(fn)}'
                 '{str(datetime.fromtimestamp(snr.time[0].item()/1e9))[:10]}'
                 '$T_{{sample}}$={Ts} sec.')

    try:
        for m in P['tmark']:
            try:
                ax.annotate(m[2], m[:2],
                            xytext=(m[3]*100, 50), textcoords='offset points', color='white', ha='left',
                            bbox={'alpha': .2},
                            arrowprops={'facecolor': 'white',
                                        'arrowstyle': '-[',
                                        'connectionstyle': "arc3,rad=0.2"})
            except Exception as e:
                logging.error(f'failed to annotate {e}')
    except KeyError:
        pass

    # if you get RuntimeError here, will also error on savefig
    fg.tight_layout()
# %% output
    ofn = ctxt + 'power_' + isrutils.expfn(fn)

    writeplots(fg, snr.time[0].item(), P['odir'], ofn)

    return fg


def plotsnr1d(snr, P):
    if not isinstance(snr, xarray.DataArray):
        return

    tind = abs(snr.time-P['t0']).argmin()
    tind = range(tind-1, tind+2)
    t1 = snr.time[tind]

    S = 10 * np.log10(snr[snr.srng >= P['zlim'][0], t1])
    z = S.index

    ax = figure().gca()
    ax.plot(S.iloc[:, 0], z, color='r', label=str(t1[0]))
    ax.plot(S.iloc[:, 1], z, color='k', label=str(t1[1]))
    ax.plot(S.iloc[:, 2], z, color='b', label=str(t1[2]))
#    ax.set_ylim(zlim)
    ax.autoscale(True, 'y', tight=True)
    ax.set_xlim(-5)
    ax.legend()

    ax.set_title(P['fn'])
    ax.set_xlabel('SNR [dB]')
    ax.set_ylabel('altitude [km]')


def plotsnrmesh(snr, fn, P):
    if not isinstance(snr, xarray.DataArray):
        return

    tind = abs(snr.time-P['t0']).argmin()
    tind = range(tind-5, tind+6)
    t1 = snr.time[tind]

    S = 10 * np.log10(snr[snr.srng >= P['zlim'][0], t1])
    z = S.index

    x, y = np.meshgrid(S.time.values.astype(float)/1e9, z)

    ax3 = figure().gca(projection='3d')

#    ax3.plot_wireframe(x,y,S.values)
#    ax3.scatter(x,y,S.values)
    ax3.plot_surface(x, y, S.values, cmap='jet')
    ax3.set_zlim(P['vlim'])
    ax3.set_zlabel('SNR [dB]')
    ax3.set_ylabel('altitude [km]')
    ax3.set_xlabel('time')
    ax3.autoscale(True, 'y', tight=True)


def plotacf(spec: xarray.DataArray, fn: Path, azel, t, dt, P: dict):
    """
    plot PSD derived from ACF.
    """
    if not isinstance(spec, xarray.DataArray):
        return
# %% alt vs freq
    fg = figure()
    ax = fg.gca()

    assert 10 <= azel[1] <= 90, 'possibly invalid elevation angle for this beam'
    goodz = spec.srng * np.sin(np.radians(azel[1])) > ALTMIN  # actual altitude > 60km
    z = spec.srng[goodz].values / 1e3  # slant ranges where altitude > zmin km

    h = ax.pcolormesh(spec.freq.values,
                      z,
                      10 * np.log10(abs(spec[goodz, :].values)),
                      vmin=P['vlimacf'][0],
                      vmax=P['vlimacf'][1],
                      cmap='cubehelix_r')

    ytop = min(z[-1], P['zlim'][1]) if P['zlim'][1] is not None else z[-1]

    ax.set_ylim(P['zlim'][0], ytop)

    c = fg.colorbar(h, ax=ax)
    c.set_label('Power [dB]')
    ax.set_ylabel('slant range [km]')
    ax.set_title('ISR PSD: Az,El {:.1f},{:.1f}  {} $T_s$: {} [sec.] \n {}'.format(
        azel[0], azel[1], isrutils.expfn(fn), dt, str(t)[:-6]))
    ax.autoscale(True, axis='x', tight=True)
    ax.set_xlabel('frequency [kHz]')

    writeplots(fg, t, P['odir'], ' acf_' + isrutils.expfn(fn))
# %% freq at alt
    if 'zslice' in P:
        plotzslice(spec, P['zslice'], P['vlimacfslice'], azel, fn, dt, t, P['odir'], 'acfslice_' + isrutils.expfn(fn))


def plotzslice(psd, zslice, vlim, azel, fn, dt, t, odir, stem, ttxt=None, flim=(None, None)):
    assert psd.ndim == 2, 'single time,  spectrum vs srng and freq'

#    if psd.srng[-1]<100000: # km or m
#        zslice = zslice / 1000 # NOT /= or it modifies original dict!!

    if zslice[0] is None or zslice[1] is None:  # didn't specify zslice
        return

    fg = figure()
    ax = fg.gca()

    iz = findnearest(psd.srng, zslice)[0]

    freq = psd.freq.values
    if abs(freq).max() > 1000:  # MHz
        freq /= 1e6
    if freq[freq.size//2] < 0 and flim[0] is not None:
        flim = -flim

    ax.plot(freq,
            10 * np.log10(abs(psd.isel(srng=slice(iz[0], iz[1])).sum(dim='srng'))))

    ax.set_xlim(flim)
    if flim[-1] is not None and flim[-1] < 0:
        ax.invert_xaxis()  # have to do it here after set_xlim

    for v in vlim:  # not is None doesn't work for numpy.array
        if v is not None:
            v += 10
    ax.set_ylim(vlim)

    ax.set_xlabel('frequency: $f_c + f$ [kHz]')
    ax.set_ylabel('Power [dB]')

    if ttxt is None:
        ttxt = isrutils.expfn(fn)

    ax.set_title(f'Az,El {azel[0]:.1f},{azel[1]:.1f}  @ {zslice[0]}..{zslice[1]} km  {ttxt}  $T_s$: {dt} [sec.] {str(t)[:-6]} \n')

    writeplots(fg, t, odir, stem, ext='.eps')


def plotplasmaline(specdown, specup, fn, P, azel):
    tic = time()

    spec = [s for s in (specdown, specup) if isinstance(s, xarray.DataArray)]
    Nspec = len(spec)
    if Nspec == 0:
        return

    T = spec[0].time
    dT = (T[1]-T[0]).item()/1e9 if T.size >= 2 else ''

    for s in spec:
        assert (s.time == T).all(), 'times do not match for downshift and upshift plasma spectrum'

    ptype = None  # 'mesh'

    for t in T:
        fg = None
        t = datetime.utcfromtimestamp(t.item()/1e9)

        if ptype in ('mesh', 'surf'):  # cannot use subplots for 3d with matplotlib 1.4
            axs = [None, None]

            fg = figure(figsize=(15, 5))
            axs[0] = fg.add_subplot(1, Nspec, 1, projection='3d')

            fg.suptitle(f'{fn.name} {t.to_pydatetime()}', y=1.01)
        elif 'zslice' in P:  # lineplot
            print(P['zslice'])
            # fg = figure()
            # plotplasmaoverlay(specdown,specup,t,fg,P)
            # writeplots(fg,t,P['odir'],'plasmaLineOverlay')
            # continue
#            import pdb; pdb.set_trace()
            if isinstance(specdown, xarray.DataArray):
                plotzslice(specdown.sel(time=t), P['zslice'], P['vlim_pl'], azel, fn, dT, t,
                           P['odir'], 'plasmaDOWNslice', 'downshifted plasma line', P['flim_pl'])
            if isinstance(specup, xarray.DataArray):
                plotzslice(specup.sel(time=t), P['zslice'], P['vlim_pl'], azel, fn, dT, t,
                           P['odir'], 'plasmaUPslice', 'upshifted plasma line', P['flim_pl'])

        if fg is None:
            fg, axs = subplots(Nspec, 1, figsize=(15, Nspec*7.5))
            axs = np.atleast_1d(axs)

            fg.suptitle('Az,El {:.1f},{:.1f}  Plasma line {}  $T_{{sample}}$: {} [sec.]'.format(azel[0], azel[1], t, dT), y=1.01)
# %%
        for s, ax, fshift in zip(spec, axs, ('down', 'up')):
            try:
                if ptype in ('mesh', 'surf'):
                    plotplasmamesh(s.sel(time=t), fg, ax, P, ptype)
                else:  # pcolor
                    plotplasmatime(s.sel(time=t), t, fg, ax, P, fshift)
            except KeyError as e:
                logging.error(f'{e} plotting {fshift} {t}')

        fg.tight_layout()

        # write plots here else you'll double write plots
        writeplots(fg, t, P['odir'], 'plasmaLine')

    if P['verbose']:
        print('plasma line plot took {:.1f} sec.'.format(time()-tic))


def plotplasmaoverlay(specdown, specup, t, fg, P: dict):

    ax = fg.gca()

    ialt, alt = findnearest(specdown.srng.values, P['zlim_pl'])
# %%
    try:
        dBdown = 10 * np.log10(specdown.sel(time=t)[ialt, :].values)
        if len(P['vlim_pl']) >= 4 and P['vlim_pl'][2] is not None:
            dBdown += P['vlim_pl'][2]
    except AttributeError:
        pass
# %%
    try:
        dBup = 10 * np.log10(specup.sel(time=t)[ialt, :].values)
        if len(P['vlim_pl']) >= 4 and P['vlim_pl'][3] is not None:
            dBup += P['vlim_pl'][3]
    except AttributeError:
        pass

    ax.plot(-specdown.freq.values/1e6, dBdown)

    ax.plot(specup.freq.values/1e6, dBup)

    ax.set_ylabel('Power [dB]')
    ax.set_xlabel('frequency: $f_c + f$ [MHz]')

    ax.set_ylim(P['vlim_pl'][:2])
    ax.set_xlim(P['flim_pl'])

    fg.suptitle('Plasma line at {:.0f} km slant range {}'.format(alt, str(t.item)[:19]))


def plotplasmatime(spec: xarray.DataArray, t, fg, ax, P: dict, ctxt):
    if not isinstance(spec, xarray.DataArray):
        return

    srng = spec.srng.values
    zgood = srng > 60.  # above N km

    hi = ax.pcolormesh(spec.freq.values/1e6, srng[zgood], 10*np.log10(spec[zgood, :].values),
                       vmin=P['vlim_pl'][0], vmax=P['vlim_pl'][1], cmap='cubehelix_r')

#    h=ax.imshow(spec.freq.values/1e6,srng[zgood],10*log10(spec[zgood,:].values),
#                    vmin=P['vlim_pl'][0], vmax=P['vlim_pl'][1],cmap='cubehelix_r')

    ax.set_xlabel('frequency: $f_c + f$ [MHz]')
    ax.set_ylabel('slant range [km]')

    # if hi.colorbar is None:
    fg.colorbar(hi, ax=ax, format='%.0f').set_label('Power [dB]')

    ax.autoscale(True, 'both', tight=True)  # before manual lim setting
    ax.set_ylim(P['zlim_pl'])
# %%
    xfreq(ax, spec, P['flim_pl'])

    # ax.tick_params(axis='both', which='both', direction='out')


def xfreq(ax, spec, Pflim):
    if spec.freq.values[0] < 0:  # downshift
        flim = [None, None]
        if Pflim[0] is not None:
            flim[1] = -Pflim[0]
        if Pflim[1] is not None:
            flim[0] = -Pflim[1]
    else:  # upshift
        flim = Pflim

    ax.set_xlim(flim)


def plotplasmamesh(spec, fg, ax, P, ptype=''):
    if not isinstance(spec, xarray.DataArray):
        return

    if not fg and not ax:
        fg = figure()
        ax = fg.gca()
    elif fg and not ax:
        ax = fg.gca()

    srng = spec.index.values
    zgood = srng > P['zlim'][0]  # above N km

    S = 10 * np.log10(spec.loc[zgood, :])  # FIXME .sel()
    z = S.index.values

    x, y = np.meshgrid(spec.freq.values/1e6, z)

#    ax3 = figure().gca(projection='3d')
#
#    ax3.scatter(x,y,S.values)
    if ptype == 'surf':
        ax.plot_surface(x, y, S.values, cmap='jet')
    elif ptype == 'mesh':
        ax.plot_wireframe(x, y, S.values)

    ax.set_zlim(P['vlim'])
    ax.set_zlabel('Power [dB]')
    ax.set_ylabel('altitude [km]')
    ax.set_xlabel('frequency: $f_c + f$ [MHz]')
    ax.autoscale(True, 'y', tight=True)
    fg.tight_layout()


def plotbeampattern(fn, P, beamkey, beamids=None):
    """
    plots beams used in the file
    """
    if P['scan'] or P['odir'] is None:
        return

    beamcodes = np.unique(beamkey)  # for some files they're jumbled

    def _pullbeams(f, beamcodes=None):
        M = f['/Setup/BeamcodeMap']

        azel = xarray.DataArray(data=M[:, 1:3],
                                dims=['beamid', 'azel'],
                                coords={'beamid': M[:, 0].astype(int),
                                        'azel': ['az', 'el']}
                                )

        if beamcodes is not None:
            azel = azel.loc[beamcodes, :]

        date = f['/Time/RadacTimeString'][0][0][:10].decode('utf8')

        return azel, date

    if isinstance(fn, h5py.File):
        beams, date = _pullbeams(fn, beamcodes)
        h5fn = Path(fn.filename).name
    else:
        with h5py.File(fn, 'r', libver='latest') as f:
            beams, date = _pullbeams(f, beamcodes)
        h5fn = Path(fn).name

    fg = polarplot(beams.loc[:, 'az'], beams.loc[:, 'el'],  # FIXME .sel()
                   title=f'ISR {beamcodes.size} Beam Pattern: {date}',
                   markerarea=27.4)

    logging.info(f'{beamcodes.size} beam pattern {fn}')
    writeplots(fg, odir=P['odir'], ctxt=f'beams_{h5fn}', ext='.eps')


def plotsumionline(dsum, ax, fn, P):
    if dsum is None or dsum.size < 2:
        return

    assert isinstance(dsum, xarray.DataArray) and dsum.ndim == 1, 'incorrect input type'
# %% threshold
    med = np.median(dsum.values)
    medthres = P['medthres'] * med

    if (dsum > medthres).any():
        hit = True
    else:
        hit = False

    if not hit and P['scan']:
        return hit
# %% plot

    if not ax:
        fg = figure()
        ax = fg.gca()
    else:
        fg = gcf()

    ax.plot(dsum.time.values, dsum.values, label='$\sum_{range} |P_{rx}|$')

    ax.axhline(med, color='gold', linestyle='--', label='median')

    ax.axhline(medthres, color='red', linestyle='--', label='threshold')

    ax.set_ylabel('summed power')
    ax.set_xlabel('time [UTC]')
    ax.set_title(f'{isrutils.expfn(fn)} summed over range: ({P["zsum"][0]}..{P["zsum"][1]}) km')

    ax.set_yscale('log')
    ax.grid(True)
    ax.legend(loc='upper right')

    fg.autofmt_xdate()
# %% save plot efficiently
    if dsum.size <= 1000:
        ext = '.eps'
    else:
        ext = '.png'  # EPS is slow with tons of points

    writeplots(fg, dsum.time[0].item(), P['odir'], 'summedAlt', ext=ext)

    return hit


def plotsumplasmaline(plsum):
    assert isinstance(plsum, xarray.DataArray)

    fg = figure()
    ax = fg.gca()
    plsum.plot(ax=ax)
    ax.set_ylabel('summed power')
    ax.set_xlabel('time [UTC]')
    ax.set_title('plasma line summed over altitude (200..350)km and frequency (3.5..5.5)MHz')

    # ax.xaxis.set_major_locator(timeticks(plsum.time[-1]-plsum.time[0])[0])
