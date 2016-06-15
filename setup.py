#!/usr/bin/env python
from setuptools import setup
import subprocess

try:
    subprocess.call(['conda','install','--yes','--file','requirements.txt'])
except Exception:
    pass

#%%
with open('README.rst','r') as f:
	long_description = f.read()

setup(name='isrutils',
	  description='Utilities for working with Incoherent Scatter Radar raw data (initially targeted for PFISR)',
	  long_description=long_description,
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/isrutils',
	  install_requires=['pathlib2','pymap3d','GeoData'],
      dependency_links = ['https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',
                          'https://github.com/jswoboda/GeoDataPython/tarball/master#egg=GeoData',],
      packages=['isrutils'],
	  )
