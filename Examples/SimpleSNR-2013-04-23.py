#!/usr/bin/env python
"""
2013-05-01
"""
from pathlib import Path
from datetime import datetime
from matplotlib.pyplot import show
from isrutils.looper import simpleloop
import seaborn as sns
sns.set_context('talk', 1.5)

# %% users param
vlim = (22, 55)
# zlim=(90, 400)
zlim = (None, None)
tlim = (datetime(2013, 5, 1),
        datetime(2013, 5, 1))
tlim = (None, None)


P = {'path': '~/data/2013-04-23/isr',
     'beamid': 64157,
     'showacf': False,
     'showsamples': True,
     }
# %% iterate over list. Files are ID'd by file extension (See README.rst)

flist = [x for x in Path(P['path']).expanduser().iterdir() if x.suffix == '.h5']

simpleloop(flist, tlim, zlim, vlim, P)

show()
