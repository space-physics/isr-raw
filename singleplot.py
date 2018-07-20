#!/usr/bin/env python
"""
reading PFISR data down to IQ samples

See Examples/ for more updated specific code
"""
from isrutils import simpleloop
from argparse import ArgumentParser
import seaborn as sns
sns.set_context('talk', 1.75)
sns.set_style('ticks')


def main():

    p = ArgumentParser()
    p.add_argument('fn', help='.ini file to read')
    p = p.parse_args()

    simpleloop(p.fn)


if __name__ == '__main__':
    main()
