from pathlib import Path

import isrraw as iu

rdir = Path(__file__).parents[1]
name = "test.dt3.h5"
path = rdir / "tests"
fn = path / name


P = {
    "beamid": 64157,
    "tlim": ("06 Apr 2013 00:01:17", "06 Apr 2013 00:02:30"),
    "zlim": (200, 300),
    "vlimacf": (None, None),
    "scan": False,
    "odir": None,
}  # km


def test_readpowersnr():
    iu.readpower_samples(fn, P)


def test_readacf():
    iu.readACF(fn, P)
