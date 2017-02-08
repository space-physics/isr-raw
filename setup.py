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
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scienceopen/isrutils',
	  install_requires=['pathvalidate',
	  'sciencedates','pymap3d',
                        'GeoData'],
      dependency_links = [
                          'https://github.com/jswoboda/GeoDataPython/tarball/master#egg=GeoData',],
      packages=['isrutils'],
	  )
