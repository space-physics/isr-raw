#!/usr/bin/env python
from pathlib import Path
from time import time
from xarray import concat
#
from . import readpower_samples,readsnr_int,snrvtime_fit
from .rawacf import readACF
from .plasmaline import readplasmaline
from .summed import sumionline
from .plots import plotsnr,plotsnr1d,plotplasmaline


def isrstacker(flist,P):

    for fn in flist:
        fn = Path(fn).expanduser()
        if not fn.is_file():
            continue

        specdown,specup,snrsamp,azel,isrlla,snrint,snr30int = isrselect(fn,P)
        if fn.samefile(flist[0]):
            specdowns=specdown; specups=specup
            snrsamps = snrsamp
            snrints = snrint
            snr30ints = snr30int
        else:
            if snrsamp is not None: snrsamps= concat((snrsamps,snrsamp), axis=1)
            if snrint is not None:  snrints = concat((snrints,snrint), axis=1)
            #TOOD other concat & update to xarray syntax


#%% plots
    plotplasmaline(specdowns,specups,flist,P)

    plotsnr(snrsamps,fn,P)
#%% ACF
    readACF(fn,P)

    plotsnr(snrints,fn,P)

    plotsnr1d(snr30ints,fn,P)

    plotsnr(snr30ints,fn,P)
    #plotsnrmesh(snr,fn,P)



def isrselect(fn:Path, P:dict):
    """
    this function is a switchyard to pick the right function to read and plot
    the desired data based on filename and user requests.
    """
#%% plasma line
    specdown,specup,azel = readplasmaline(fn, P)
#%% ~ 200 millisecond raw altcode and longpulse
    #tic = time()
    snrsamp,azel,isrlla = readpower_samples(fn, P)
    #if P['verbose']: print(f'sample read took {(time()-tic):.2f} sec.')
    #tic=time()
    ionsum = sumionline(snrsamp, P) # sum over altitude range (for detection)
    #if P['verbose']: print(f'sample sum took {(time()-tic):.2f} sec.')
#%% ACF
    if P['acf']:
        tic = time()
        readACF(fn,P)
        if P['verbose']:
            print(f'ACF/PSD read & plot took {time()-tic:.1f} sec.')
#%% multi-second integration (numerous integrated pulses)
    snrint = readsnr_int(fn, P['beamid'])
#%% 30 second integration plots
    if fn.stem.rsplit('_',1)[-1] == '30sec':
        snr30int = snrvtime_fit(fn,P['beamid'])
    else:
        snr30int=None

    return specdown,specup,snrsamp,azel,isrlla,snrint,snr30int,ionsum
