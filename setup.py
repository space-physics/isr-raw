#!/usr/bin/env python
req = ['nose','python-dateutil','pytz', 'numpy','xarray','matplotlib', 'seaborn', 'h5py']
pipreq = ['pathvalidate', 'sciencedates','pymap3d',]
gitreq = ['GeoData',]

import pip
try:
    import conda.cli
    conda.cli.main('install',*req)
except Exception as e:
    pip.main(['install'] + req)
pip.main(['install'] + pipreq)
# %%
from setuptools import setup

setup(name='isrutils',
      packages=['isrutils'],
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/isrutils',
      description='utilities for reading and plotting ISR raw data',
      version='0.5',
	  install_requires= req+pipreq+gitreq,
      dependency_links = ['https://github.com/jswoboda/GeoDataPython/tarball/master#egg=GeoData-999.0.0',],
	  )
