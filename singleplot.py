#!/usr/bin/env python
"""
reading PFISR data down to IQ samples

See Examples/ for more updated specific code
"""
from isrraw.plots import simpleloop
from argparse import ArgumentParser


def main():

    p = ArgumentParser()
    p.add_argument("fn", help=".ini file to read")
    p = p.parse_args()

    simpleloop(p.fn)


if __name__ == "__main__":
    main()
