#!/usr/bin/env python
from . import Path
from pandas import concat
#
from .common import ftype
from .rawacf import readACF
from .plasmaline import readplasmaline
from .snrpower import readpower_samples,readsnr_int,snrvtime_fit
from .plots import plotsnr,plotsnr1d,plotplasmaline



def isrstacker(flist,odir,beamid,tlim,vlim,zlim,t0,acf,samples,makeplot):

    for fn in flist:
        fn = Path(fn).expanduser()
        if not fn.is_file():
            continue

        specdown,specup,snrsamp,azel,isrlla,snrint,snr30int = isrselect(fn,beamid,tlim,zlim,t0,acf,samples)
        if fn.samefile(flist[0]):
            specdowns=specdown; specups=specup
            snrsamps = snrsamp
            snrints = snrint
            snr30ints = snr30int
        else:
            if snrsamp is not None: snrsamps= concat((snrsamps,snrsamp),axis=1)
            if snrint is not None:  snrints = concat((snrints,snrint), axis=1)
            #TOOD other concat
#%% plots
    vlim = vlim if vlim else (30,70) #(70,100)
    plotplasmaline(specdowns,specups,flist,P,makeplot=makeplot,odir=odir)

    vlim = vlim if vlim else (30,60)
    plotsnr(snrsamps,fn,P)
#%% ACF
    vlim = vlim if vlim else (20,45)
    readACF(fn,P)

    vlim = vlim if vlim else (47,80)
    plotsnr(snrints,fn,P)

    vlim = vlim if vlim else (-20,None)
    if t0 is not None:
        plotsnr1d(snr30ints,fn,t0,zlim)
    plotsnr(snr30ints,fn,P)
    #plotsnrmesh(snr,fn,P)



def isrselect(fn,beamid,P):
    """
    this function is a switchyard to pick the right function to read and plot
    the desired data based on filename and user requests.
    """
    fn = Path(fn).expanduser() #need this here
#%% handle path, detect file type
    ft = ftype(fn)
#%% plasma line
    specdown=specup=None
    if ft in ('dt1','dt2'):
        specdown,specup = readplasmaline(fn,beamid,P['tlim'])
#%% ~ 200 millisecond raw altcode and longpulse
    snrsamp=azel=isrlla=None
    if ft in ('dt0','dt3') and P['samples']:
        snrsamp,azel,isrlla = readpower_samples(fn,beamid,P['zlim'],P['tlim'])
#%% ACF
    if ft in ('dt0','dt3') and P['acf']:
        readACF(fn,P)
#%% multi-second integration (numerous integrated pulses)
    snrint=None
    if ft in ('dt0','dt3') and P['int']:
        snrint = readsnr_int(fn,beamid)
#%% 30 second integration plots
    if fn.stem.rsplit('_',1)[-1] == '30sec':
        snr30int = snrvtime_fit(fn,beamid)
    else:
        snr30int=None

    return specdown,specup,snrsamp,azel,isrlla,snrint,snr30int
