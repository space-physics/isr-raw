#!/usr/bin/env python
"""
plots integrated ISR power over altitude range on top of HiST image stream
"""
from isrutils.overlayISRopt import overlayisrhist

P = {
    "isrfn": "~/data/2013-04-14/isr/d0346832.dt0.h5",
    "zsum": (120, 220),
    "zlim": (90, None),
    "tlim": ["2013-04-14T08:28:00", "2013-04-14T08:29:10"],
    "azelfn": "~/code/histfeas/precompute/hst0cal.h5",
    "optfn": "~/data/2013-04-14/HST/2013-04-14T0827-0830_hst0.h5",
    "beamid": 64157,
}
P["odir"] = "out/" + str(P["tlim"][0]) + ".mkv"

overlayisrhist(P)
