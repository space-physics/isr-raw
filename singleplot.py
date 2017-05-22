#!/usr/bin/env python
"""
reading PFISR data down to IQ samples

See Examples/ for more updated specific code
"""
import matplotlib
matplotlib.use('agg') # NOTE comment out this line to enable visible plots
#from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',1.75)
sns.set_style('ticks')
#
from isrutils.looper import simpleloop


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn', help='.ini file to read')
    p = p.parse_args()

    simpleloop(p.fn)
