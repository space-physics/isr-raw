from pathlib import Path
#
from isrutils.common import ftype
from isrutils.rawacf import readACF
from isrutils.plasmaline import readplasmaline,plotplasmaline
from isrutils.snrpower import (readpower_samples,plotsnr,readsnr_int,snrvtime_fit,
                               plotsnr1d,plotsnrmesh)

def isrselect(fn,odir,beamid,tlim,vlim,zlim,t0,acf,samples,makeplot):
    """
    this function is a switchyard to pick the right function to read and plot
    the desired data based on filename and user requests.
    """
    fn = Path(fn).expanduser()
#%% handle path, detect file type
    ft = ftype(fn)
#%% plasma line
    if ft in ('dt1','dt2'):
        vlim = vlim if vlim else (70,100)
        spec,freq = readplasmaline(fn,beamid,tlim)
        plotplasmaline(spec,freq,fn,vlim=vlim,zlim=zlim,makeplot=makeplot,odir=odir)
#%% raw altcode and longpulse
    if ft in ('dt0','dt3') and samples:
        vlim = vlim if vlim else (30,60)
        snrsamp,azel,isrlla = readpower_samples(fn,beamid,tlim,zlim)
        plotsnr(snrsamp,fn,tlim=tlim,vlim=vlim,ctxt='Power [dB]')
    if ft in ('dt0','dt3') and acf:
        vlim = vlim if vlim else (20,45)
        readACF(fn,beamid,makeplot,odir,tlim=tlim,vlim=vlim)
#%% 12 second (numerous integrated pulses)
    if ft in ('dt0','dt3'):
        vlim = vlim if vlim else (47,70)
        snr12sec = readsnr_int(fn,beamid)
        plotsnr(snr12sec,fn,vlim=vlim,ctxt='SNR [dB]')
#%% 30 second integration plots
    if fn.stem.rsplit('_',1)[-1] == '30sec':
        vlim = vlim if vlim else (-20,None)
        snr = snrvtime_fit(fn,beamid)

        if t0 is not None:
            plotsnr1d(snr,fn,t0,zlim)
        plotsnr(snr,fn,tlim,vlim)
        #plotsnrmesh(snr,fn,t0,vlim,zlim)
