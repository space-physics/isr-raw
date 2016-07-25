#!/usr/bin/env python
from setuptools import setup
import subprocess

try:
    subprocess.call(['conda','install','--file','requirements.txt'])
except Exception:
    pass

setup(name='isrutils',
	  description='Utilities for Incoherent Scatter Radar raw data (initially targeted for PFISR)',
	  url='https://github.com/scienceopen/isrutils',
	  install_requires=['pathlib2','pathvalidate',
                         'histutils','pymap3d','GeoData'],
      dependency_links = ['https://github.com/scienceopen/histutils/tarball/master#egg=histutils',
                          'https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',
                          'https://github.com/jswoboda/GeoDataPython/tarball/master#egg=GeoData',],
      packages=['isrutils'],
	  )
