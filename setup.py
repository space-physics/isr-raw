#!/usr/bin/env python
from setuptools import setup

req = ['pathvalidate',
	  'sciencedates','pymap3d',
         'GeoData',
	   'nose','python-dateutil','pytz','numpy','xarray','matplotlib','seaborn','h5py']

setup(name='isrutils',
      packages=['isrutils'],
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scienceopen/isrutils',
      description='utilities for reading and plotting ISR raw data',
      version='0.5',
	  install_requires=req,
      dependency_links = [
            'https://github.com/jswoboda/GeoDataPython/tarball/master#egg=GeoData-999.0.0',],
	  )
