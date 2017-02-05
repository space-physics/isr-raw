#!/usr/bin/env python
from setuptools import setup

setup(name='isrutils',
	  install_requires=['nose','python-dateutil','pytz','numpy','xarray','matplotlib','seaborn','h5py',
                        'pathvalidate',
                         'histutils','pymap3d','GeoData'],
      dependency_links = ['https://github.com/scienceopen/histutils/tarball/master#egg=histutils',
                          'https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',
                          'https://github.com/jswoboda/GeoDataPython/tarball/master#egg=GeoData',],
      packages=['isrutils'],
	  )
