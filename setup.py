#!/usr/bin/env python3

from setuptools import setup
import subprocess
#%%
with open('README.rst','r') as f:
	long_description = f.read()

setup(name='isrutils',
      version='0.1',
	  description='Utilities for working with Incoherent Scatter Radar raw data (initially targeted for PFISR)',
	  long_description=long_description,
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/isrutils',
	  install_requires=['pymap3d'],
      dependency_links = ['https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',],
      packages=['isrutils'],
	  )
#%%
try:
    subprocess.run(['conda','install','--yes','--quiet','--file','requirements.txt'])
except Exception as e:
    print('you will need to install packages in requirements.txt  {}'.format(e))
    with open('requirements.txt','r') as f:
        print(f.read())
