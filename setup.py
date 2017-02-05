#!/usr/bin/env python
from setuptools import setup

try:
    import conda.cli
    conda.cli.main('install','--file','requirements.txt')
except Exception as e:
    print(e)
    import pip
    pip.main(['install','-r','requirements.txt'])

setup(name='isrutils',
	  install_requires=['pathvalidate',
                         'histutils','pymap3d','GeoData'],
      dependency_links = ['https://github.com/scienceopen/histutils/tarball/master#egg=histutils',
                          'https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',
                          'https://github.com/jswoboda/GeoDataPython/tarball/master#egg=GeoData',],
      packages=['isrutils'],
	  )
