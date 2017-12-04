#!/usr/bin/env python
install_requires= ['python-dateutil','pytz', 'numpy','xarray','matplotlib', 'h5py','scipy',
'pathvalidate', 'sciencedates','pymap3d',
'GeoData',]
tests_require=['nose','coveralls']

# %%
from setuptools import setup,find_packages

setup(name='isrutils',
      packages=find_packages(),
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/isrutils',
      description='utilities for reading and plotting ISR raw data',
      version='0.5.1',
      python_requires='>=3.6',
	  install_requires=install_requires,
      dependency_links = ['https://github.com/jswoboda/GeoDataPython/tarball/master#egg=GeoData-999.0.0',],
      extras_require={'plot':['seaborn',],
                      'tests':tests_require},
      tests_require=tests_require,
	  )
