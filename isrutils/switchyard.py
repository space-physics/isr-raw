#!/usr/bin/env python
from . import Path
from pandas import concat
#
from .common import ftype
from .rawacf import readACF
from .plasmaline import readplasmaline,plotplasmaline
from .snrpower import readpower_samples,readsnr_int,snrvtime_fit
from .plots import plotsnr,plotsnr1d,plotsnrmesh



def isrstacker(flist,odir,beamid,tlim,vlim,zlim,t0,acf,samples,makeplot):

    for fn in flist:
        fn = Path(fn).expanduser()

        spec,freq,snrsamp,azel,isrlla,snrint,snr30int = isrselect(fn,beamid,tlim,zlim,t0,acf,samples)
        if fn.samefile(flist[0]):
            specs=spec; freqs=freq
            snrsamps = snrsamp
            snrints = snrint
            snr30ints = snr30int
        else:
            if snrsamp is not None: snrsamps= concat((snrsamps,snrsamp),axis=1)
            if snrint is not None:  snrints = concat((snrints,snrint), axis=1)
            #TOOD other concat
#%% plots
    vlim = vlim if vlim else (30,70) #(70,100)
    plotplasmaline(specs,freqs,flist,vlim=vlim,zlim=zlim,makeplot=makeplot,odir=odir)

    vlim = vlim if vlim else (30,60)
    plotsnr(snrsamps,fn,tlim=tlim,vlim=vlim,ctxt='Power [dB]')
#%% ACF
    vlim = vlim if vlim else (20,45)
    readACF(fn,beamid,makeplot,odir,tlim=tlim,vlim=vlim)

    vlim = vlim if vlim else (47,80)
    plotsnr(snrints,fn,vlim=vlim,ctxt='SNR [dB]')

    vlim = vlim if vlim else (-20,None)
    if t0 is not None:
        plotsnr1d(snr30ints,fn,t0,zlim)
    plotsnr(snr30ints,fn,tlim,vlim)
    #plotsnrmesh(snr,fn,t0,vlim,zlim)



def isrselect(fn,beamid,tlim,zlim,t0,acf,samples):
    """
    this function is a switchyard to pick the right function to read and plot
    the desired data based on filename and user requests.
    """
    fn = Path(fn).expanduser() #need this here
#%% handle path, detect file type
    ft = ftype(fn)
#%% plasma line
    spec=freq=None
    if ft in ('dt1','dt2'):
        spec,freq = readplasmaline(fn,beamid,tlim)
#%% 0.234 second raw altcode and longpulse
    snrsamp=azel=isrlla=None
    if ft in ('dt0','dt3') and samples:
        try:
            snrsamp,azel,isrlla = readpower_samples(fn,beamid,zlim,tlim)
        except KeyError as e:
            print('raw pulse data not found {}  {}'.format(fn,e))
#%% multi-second integration (numerous integrated pulses)
    snrint=None
    if ft in ('dt0','dt3'):
        try:
            snrint = readsnr_int(fn,beamid)
        except KeyError as e:
            print('integrated pulse data not found {}  {}'.format(fn,e))
#%% 30 second integration plots
    if fn.stem.rsplit('_',1)[-1] == '30sec':
        snr30int = snrvtime_fit(fn,beamid)
    else:
        snr30int=None

    return spec,freq,snrsamp,azel,isrlla,snrint,snr30int
