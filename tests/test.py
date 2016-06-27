#!/usr/bin/env python
import tarfile
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
if not fn.is_file():
    with tarfile.open(str(fn) + '.xz','r') as f:
        f.extract(name,str(path))


bid=64157 #magnetic zenith beam id for PFISR for experiments I know of  ~ 2011-2016

zlim=(200,300) #km

def test_readpowersnr():
    readpower_samples(fn,bid,zlim)

def test_readacf():
    readACF(fn,bid)


if __name__ == '__main__':
    run_module_suite()
