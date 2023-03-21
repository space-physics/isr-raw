#!/usr/bin/env python
"""
plots integrated ISR power over altitude range on top of HiST image stream
"""
from matplotlib.pyplot import show

#
from isrraw.overlayISRopt import overlayisrhist
from isrraw.common import boilerplateapi


def main():
    overlayisrhist(boilerplateapi())

    show()


if __name__ == "__main__":
    main()
