#!/usr/bin/env python
"""
summed measurements and plots
"""
from pathlib import Path
import xarray
from xarray import DataArray
import isrutils


# %% dt3
def sumionline(snrsamp: DataArray, P: dict):

    if "zsum" in P and isinstance(snrsamp, DataArray):

        srng = snrsamp.srng
        i = (srng > P["zsum"][0]) & (srng < P["zsum"][1])

        return snrsamp.isel(srng=i).sum(dim="srng")


# %% plasma line


def sumplasmaline(fn: Path, P: dict):
    spec, freq = isrutils.readplasmaline(fn, P)
    assert isinstance(spec, xarray.DataArray) and spec.ndim == 4
    assert isinstance(P["flim"][0], float)

    z = spec.srng
    specsum = DataArray(index=spec.items, columns=spec.labels)

    zind = (P["zlim"][0] <= z) & (z <= P["zlim"][1])

    for s in spec:
        find = (P["flim"][0] <= abs(freq[s] / 1.0e6)) & (abs(freq[s] / 1.0e6) < P["flim"][1])
        specsum.loc[:, s] = spec.loc[:, :, zind, find].sum(axis=3).sum(axis=2)  # FIXME .sum(dim=)

    return specsum
