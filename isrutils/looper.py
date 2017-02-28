"""
This isn't in __init__.py due to matplotlib & seaborn imports.
"""
from pathlib import Path
from configparser import ConfigParser
from numpy import array
from time import time
#
import matplotlib
matplotlib.use('agg') # NOTE comment out this line to enable visible plots
#from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.75)
sns.set_style('ticks')
#
from . import str2dt
from .switchyard import isrselect
from .rawacf import readACF
from .plots import plotsnr,plotplasmaline,plotsumionline

def simpleloop(inifn):
    ini = ConfigParser(allow_no_value=True, empty_lines_in_values=False,
                      inline_comment_prefixes=(';'), strict=True)
    ini.read(inifn)

    dpath = Path(ini.get('data','path')).expanduser()
    ftype = ini.get('data','ftype',fallback=None)
#%% parse user directory / file list input
    if dpath.is_dir() and not ftype:
        flist = dpath.glob('*dt*.h5')
    elif dpath.is_dir() and ftype: #glob pattern
            flist = dpath.glob(f'*.{ftype}.h5')
    elif dpath.is_file(): # a single file was specified
        flist = [flist]
    else:
        raise FileNotFoundError(f'unknown path/filetype {dpath} / {ftype}')

    flist=sorted(flist) #in case glob
    assert len(flist)>0, f'no files found in {dpath}'
    print(f'examining {len(flist)} files in {dpath}\n')
#%% api catchall
    P = {
    'odir': ini.get('plot','odir',fallback=None),
    'verbose': ini.getboolean('plot','verbose',fallback=False),
    'scan': ini.getboolean('data','scan',fallback=False),
     # N times the median is declared a detection
    'medthres': ini.getfloat('data','medthreas',fallback=2.),
    'tlim': ini.get('plot','tlim',fallback=None),
    'beamid': ini.getint('data','beamid'),
    'acf': ini.getboolean('plot','acf',fallback=False)
         }

    if P['tlim']:
        P['tlim'] = P['tlim'].split(',')
    P['tlim'] = str2dt(P['tlim'])

    for p in ('flim_pl','vlim','vlim_pl','vlim','vlimacf','vlimacfslice','vlimint',
              'zlim','zsum'):
        P[p] = array(ini.get('plot',p,fallback='nan').split(',')).astype(float)

#%% loop over files
    for f in flist:
        # read data
        specdown,specup,snrsamp,azel,isrlla,snrint,snr30int,ionsum = isrselect(dpath/f, P)
#%% plot
        # summed ion line over altitude range
#        tic = time()
        hit = plotsumionline(ionsum,None,f,P)
        assert isinstance(hit,bool), 'is summed data being properly read?'
        print(f.stem, hit)
#        if P['verbose']: print(f'sum plot took {(time()-tic):.1f} sec.')

        if hit and not P['acf']: # if P['acf'], it was already plotted. Otherwise, we plot only if hit
            readACF(f,P)

        if hit or not P['scan']:
            # 15 sec integration
            plotsnr(snrint,f,P,azel,ctxt='int_')
            # 200 ms integration
            plotsnr(snrsamp,f,P,azel)
            # plasma line spectrum
            plotplasmaline(specdown,specup,f,P,azel)
