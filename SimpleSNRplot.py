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

#%%
    fn = Path(p.fn).expanduser()
    odir = Path(p.odir).expanduser()

#%% raw (lowest common level)
    if ftype(fn) in ('dt0','dt3') and p.samples:
        vlim = p.vlim if p.vlim else (32,60)
        snrsamp = readpower_samples(fn,p.beamid)
        plotsnr(snrsamp,fn,tlim=p.tlim,vlim=vlim,ctxt='Power [dB]')
    elif ftype(fn) in ('dt0','dt3') and p.acf:
        vlim = p.vlim if p.vlim else (20,45)
        readACF(fn,p.beamid,p.makeplot,odir,tlim=p.tlim,vlim=vlim)
#%% 12 second (numerous integrated pulses)
    elif ftype(fn) in ('dt0','dt3'):
        vlim = p.vlim if p.vlim else (47,70)
        snr12sec = readsnr_int(fn,p.beamid)
        plotsnr(snr12sec,fn,vlim=vlim,ctxt='SNR [dB]')
#%% 30 second integegration plots
    else:
        vlim = p.vlim if p.vlim else (-20,None)
        snr = snrvtime_fit(fn,p.beamid)

        if p.t0:
            plotsnr1d(snr,fn,p.t0,p.zlim)
        plotsnr(snr,fn,p.tlim,vlim)
        plotsnrmesh(snr,fn,p.t0,vlim,p.zlim)

    show()
