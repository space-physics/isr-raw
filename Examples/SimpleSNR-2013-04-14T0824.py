#!/usr/bin/env python

# %% users param
P = {
    "path": "~/data/2013-04-14/isr",
    "beamid": 64157,
    "acf": False,
    "vlimacf": (18, 45),
    "zlim_pl": [None, None],
    "vlim_pl": [72, 90],
    "flim_pl": [3.5, 5.5],
    "odir": "out/2013-04-14T0824",
    "vlim": [25, 55],
    "zlim": (90, None),
    "tlim": ("2013-04-14T08:25Z", "2013-04-14T08:27Z"),
    "verbose": True,
}
# %%

flist = (
    "d0346832.dt3.h5",
    # 'd0346832.dt1.h5'
    # 'd0346832.dt0.h5'
)
