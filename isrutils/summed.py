#!/usr/bin/env python
"""
summed measurements and plots
"""
from . import Path, writeplots,expfn
import pathvalidate
from xarray import DataArray
from datetime import datetime
from pytz import UTC
from numpy import absolute,nan,linspace,percentile
from matplotlib.pyplot import figure,draw,pause,show
from matplotlib.cm import jet
import matplotlib.gridspec as gridspec
from matplotlib.colors import LogNorm
import matplotlib.animation as anim
#
from .plasmaline import readplasmaline
from .common import findindex2Dsphere,timesync,projectisrhist
from .snrpower import readpower_samples
from .plots import plotsumionline
#
from GeoData.plotting import plotazelscale

vidnorm = LogNorm()

#%% joint isr optical plot
def dojointplot(ds,spec,freq,beamazel,optical,optazel,optlla,isrlla,heightkm,utopt,P):
    """
    ds: radar data

    f1,a1: radar   figure,axes
    f2,a2: optical figure,axes
    """
    assert isinstance(ds,DataArray)

#%% setup master figure
    fg = figure(figsize=(8,12))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])
#%% setup radar plot(s)
    a1 = fg.add_subplot(gs[1])
    plotsumionline(ds,a1,expfn(P['isrfn']),P['zlim'])

    h1 = a1.axvline(nan,color='k',linestyle='--')
    t1 = a1.text(0.05,0.95,'time=',transform=a1.transAxes,va='top',ha='left')
#%% setup top optical plot
    if optical is not None:
        a0 = fg.add_subplot(gs[0])
        clim = compclim(optical,lower=10,upper=99.99)
        h0 = a0.imshow(optical[0,...],origin='lower',interpolation='none',cmap='gray',
                       norm=vidnorm,vmin=clim[0],vmax=clim[1])
        a0.set_axis_off()
        t0 = a0.set_title('')

#%% plot magnetic zenith beam
        azimg = optazel[:,1].reshape(optical.shape[1:])
        elimg = optazel[:,2].reshape(optical.shape[1:])

        optisrazel = projectisrhist(isrlla,beamazel,optlla,optazel,heightkm)

        br,bc = findindex2Dsphere(azimg,elimg,optisrazel['az'],optisrazel['el'])

        #hollow beam circle
    #    a2.scatter(bc,br,s=500,marker='o',facecolors='none',edgecolor='red', alpha=0.5)

        #beam data, filled circle
        s0 = a0.scatter(bc,br,s=2700,alpha=0.6,linewidths=3,
                        edgecolors=jet(linspace(ds.min().item(), ds.max().item())))

        a0.autoscale(True,tight=True)
        fg.tight_layout()
#%% time sync
    tisr = ds.time.values
    Iisr,Iopt = timesync(tisr,utopt,P['tlim'])
#%% iterate
    first = True
    Writer = anim.writers['ffmpeg']
    writer = Writer(fps=5,
                    metadata=dict(artist='Michael Hirsch'),
                    codec='ffv1')

    ofn = Path(P['odir']).expanduser() / ('joint_' +
            pathvalidate.sanitize_filename(str(datetime.fromtimestamp(utopt[0]))[:-3]) + '.mkv')

    print('writing {}'.format(ofn))
    with writer.saving(fg, str(ofn),150):
      for iisr,iopt in zip(Iisr,Iopt):
        ctisr = tisr[iisr]
#%% update isr plot
        h1.set_xdata(ctisr)
        t1.set_text('isr: {}'.format(ctisr))
#%% update hist plot
        if iopt is not None:
            ctopt = datetime.fromtimestamp(utopt[iopt], tz=UTC)
            h0.set_data(optical[iopt,...])
            t0.set_text('optical: {}'.format(ctopt))
            s0.set_array(ds.loc[ctisr]) #FIXME circle not changing magnetic zenith beam color? NOTE this is isr time index
#%% anim
        if first and iopt is not None:
            plotazelscale(optical[iopt,...],azimg,elimg)
            show()
            first=False
        #
        draw(); pause(0.01)

        writer.grab_frame(facecolor='k')

        if ofn.suffix == '.png':
            try:
                writeplots(fg,ctopt,ofn,P['makeplot'],ctxt='joint')
            except UnboundLocalError:
                writeplots(fg,ctisr,ofn,P['makeplot'],ctxt='isr')

def compclim(imgs,lower=0.5,upper=99.9,Nsamples=50):
    """
    inputs:
    images: Nframe x ypix x xpix grayscale image stack (have not tried with 4-D color)
    lower,upper: percentage (0,100)% to clip
    Nsamples: number of frames to test across the image stack (don't use too many for memory reasons)
    """
    sampind = linspace(0,imgs.shape[0],Nsamples,endpoint=False,dtype=int)

    clim = percentile(imgs[sampind,...],[lower,upper])
    if upper == 100.:
        clim[1] = imgs.max() #consider all images
    return clim

#%% dt3
def sumionline(fn,P):
    snrsamp,azel,lla = readpower_samples(fn,P)

    if isinstance(snrsamp,DataArray):
        return snrsamp.sum(dim='srng'),azel,lla
    else:
        return None,azel,lla

#%% plasma line
def sumplasmaline(fn,P):
    spec,freq = readplasmaline(fn,P)
    assert isinstance(spec,DataArray) and spec.ndim==4
    assert isinstance(P['flim'][0],float)

    z = spec.srng
    specsum = DataArray(index=spec.items,columns=spec.labels)

    zind = (P['zlim'][0] <= z) & (z <= P['zlim'][1])

    for s in spec:
        find = (P['flim'][0] <= absolute(freq[s]/1.e6)) & (absolute(freq[s]/1.e6) < P['flim'][1])
        specsum.loc[:,s] = spec.loc[:,:,zind,find].sum(axis=3).sum(axis=2) #FIXME .sum(dim=)

    return specsum
