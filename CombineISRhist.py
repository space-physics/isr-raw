#!/usr/bin/env python
"""
plots integrated ISR power over altitude range on top of HiST image stream
"""
from matplotlib.pyplot import show

#
from isrutils.overlayISRopt import overlayisrhist
from isrutils.common import boilerplateapi


def main():
    overlayisrhist(boilerplateapi())

    show()


if __name__ == "__main__":
    main()
