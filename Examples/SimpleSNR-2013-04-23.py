#!/usr/bin/env python3
"""
2013-05-01
"""

from __future__ import annotations
import typing as T
from pathlib import Path
from datetime import datetime


# %% users param
vlim = (22, 55)
# zlim=(90, 400)
zlim = (None, None)
tlim = (datetime(2013, 5, 1), datetime(2013, 5, 1))
tlim = (None, None)


P: dict[str, T.Any] = {
    "path": "~/data/2013-04-23/isr",
    "beamid": 64157,
    "showacf": False,
    "showsamples": True,
}
# %% iterate over list. Files are ID'd by file extension (See README.rst)

flist = [x for x in Path(P["path"]).expanduser().iterdir() if x.suffix == ".h5"]
