#!/usr/bin/env python3
"""
reading PFISR data down to IQ samples

See README.rst for the data types this file handles.

Designed for Python 3.5+, may work with older versions.
"""
from __future__ import division,absolute_import
from pathlib2 import Path
from matplotlib.pyplot import show
#import seaborn as sns
#sns.color_palette(sns.color_palette("cubehelix"))
#sns.set(context='poster', style='ticks')
#sns.set(rc={'image.cmap': 'cubehelix_r'}) #for contour
#
from isrutils.snrpower import (readpower_samples,plotsnr,readsnr_int,snrvtime_fit,
                               plotsnr1d,plotsnrmesh)
from isrutils.rawacf import readACF
from isrutils.common import ftype
from isrutils.plasmaline import readplasmaline

def isrselect(fn,odir,beamid,tlim,vlim,zlim,t0,acf,samples,makeplot):
    """
    this function is a switchyard to pick the right function to read and plot
    the desired data based on filename and user requests.
    """
#%% handle path, detect file type
    fn = Path(fn).expanduser()
    odir = Path(odir).expanduser()

    ft = ftype(fn)
#%% plasma line
    if ft in ('dt1','dt2'):
        vlim = vlim if vlim else (70,100)
        readplasmaline(fn,beamid,makeplot,odir,vlim=vlim)
#%% raw altcode and longpulse
    elif ft in ('dt0','dt3') and samples:
        vlim = vlim if vlim else (32,60)
        snrsamp = readpower_samples(fn,beamid)
        plotsnr(snrsamp,fn,tlim=tlim,vlim=vlim,ctxt='Power [dB]')
    elif ft in ('dt0','dt3') and acf:
        vlim = vlim if vlim else (20,45)
        readACF(fn,beamid,makeplot,odir,tlim=tlim,vlim=vlim)
#%% 12 second (numerous integrated pulses)
    elif ft in ('dt0','dt3'):
        vlim = vlim if vlim else (47,70)
        snr12sec = readsnr_int(fn,beamid)
        plotsnr(snr12sec,fn,vlim=vlim,ctxt='SNR [dB]')
#%% 30 second integegration plots
    else:
        vlim = vlim if vlim else (-20,None)
        snr = snrvtime_fit(fn,beamid)

        if t0:
            plotsnr1d(snr,fn,t0,zlim)
        plotsnr(snr,fn,tlim,vlim)
        plotsnrmesh(snr,fn,t0,vlim,zlim)

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

    isrselect(p.fn,p.odir,p.beamid,p.tlim,p.vlim,p.zlim,p.t0,p.acf,p.samples,p.makeplot)

    show()
