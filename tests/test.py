#!/usr/bin/env python
import matplotlib
matplotlib.use('agg')
print(matplotlib.get_backend())

from isrutils import Path
from numpy.testing import run_module_suite
#
from isrutils.snrpower import (readpower_samples,readsnr_int,snrvtime_fit)
from isrutils.plots import plotsnr,plotsnr1d,plotsnrmesh
from isrutils.rawacf import readACF
from isrutils.plasmaline import readplasmaline

rdir = Path(__file__).parents[1]
name = 'test.dt3.h5'
path = rdir/'tests'
fn = path/name


P={'beamid':64157,
   'tlim':[None,None],
    'zlim':(200,300)} #km

def test_readpowersnr():
    readpower_samples(fn,P)

def test_readacf():
    readACF(fn,P)


if __name__ == '__main__':
    run_module_suite()
