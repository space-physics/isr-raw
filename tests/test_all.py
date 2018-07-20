#!/usr/bin/env python
import matplotlib
matplotlib.use('agg')
print(matplotlib.get_backend())

from pathlib import Path
import pytest
#
from isrutils import readpower_samples,readsnr_int,snrvtime_fit, readplasmaline, readACF


rdir = Path(__file__).parents[1]
name = 'test.dt3.h5'
path = rdir/'tests'
fn = path/name


P={'beamid':64157,
   'tlim':('06 Apr 2013 00:01:17','06 Apr 2013 00:02:30'),
    'zlim':(200,300),
    'vlimacf':(None,None),
    'scan':False,
    'odir': None} #km

def test_readpowersnr():
    readpower_samples(fn,P)

def test_readacf():
    readACF(fn,P)


if __name__ == '__main__':
    pytest.main()
