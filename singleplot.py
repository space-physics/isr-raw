#!/usr/bin/env python
"""
reading PFISR data down to IQ samples

See Examples/ for more updated specific code
"""
from isrutils.looper import simpleloop


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='.ini file to read')
    p = p.parse_args()

    simpleloop(p.fn)
