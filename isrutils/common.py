from datetime import datetime
from numpy import array, unravel_index, datetime64, asarray, atleast_1d, nanmax, nanmin, nan, isfinite
from scipy.interpolate import interp1d
from argparse import ArgumentParser

#
from pymap3d.haversine import anglesep
from pymap3d import aer2ecef, ecef2aer

EPOCH = datetime(1970, 1, 1, 0, 0, 0)


def projectisrhist(isrlla, beamazel, optlla, optazel, heightkm):
    """
    intended to project ISR beam at a single height into optical data.

    output:
    az,el,slantrange in degrees,meters
    """
    isrlla = asarray(isrlla)
    optlla = asarray(optlla)
    assert isrlla.size == optlla.size == 3
    x, y, z = aer2ecef(beamazel[0], beamazel[1], heightkm * 1e3, isrlla[0], isrlla[1], isrlla[2])
    try:
        az, el, srng = ecef2aer(x, y, z, optlla[0], optlla[1], optlla[2])
    except IndexError:
        az, el, srng = ecef2aer(x, y, z, optlla["lat"], optlla["lon"], optlla["alt_km"])

    return {"az": az, "el": el, "srng": srng}


def timesync(tisr, topt, tlim=None):
    """
    TODO: for now, assume optical is always faster
    inputs
    tisr: vector of datetime for ISR
    topt: vector of datetime for camera
    tlim: start,stop UT1 Unix time request

    output
    iisr: indices (integers) of isr to playback at same time as camera
    iopt: indices (integers) of optical to playback at same time as isr
    """
    if isinstance(tisr[0], datetime):
        tisr = array([t.timestamp() for t in tisr])  # must be ndarray
    elif isinstance(tisr[0], datetime64):
        tisr = tisr.astype(float) / 1e9

    assert ((tisr > 1e9) & (tisr < 2e9)).all(), "date sanity check"

    if tlim is not None and isinstance(tlim[0], datetime):
        tlim = array([t.timestamp() for t in tlim])

    assert isinstance(tisr[0], float), "datetime64 is not wanted here, lets use ut1_unix float for minimum conversion effort"
    # separate comparison
    if topt is None:
        topt = (nan, nan)
    # %% interpolate isr indices to opt (assume opt is faster, a lot of duplicates iisr)
    if tlim is not None:
        tstart = nanmax([tlim[0], tisr[0], topt[0]])
        tend = nanmin([tlim[1], tisr[-1], topt[-1]])
    else:
        tstart = nanmax([tisr[0], topt[0]])
        tend = nanmin([tisr[-1], topt[-1]])

    if topt is not None and isfinite(topt[0]):
        f = interp1d(tisr, range(tisr.size), "nearest", assume_sorted=True)

        # optical:  typically treq = topt
        ioptreq = ((tstart <= topt) & (topt <= tend)).nonzero()[0]

        toptreq = topt[ioptreq]
        iisrreq = f(toptreq).astype(int)

        # tisrreq = tisr[(tstart<=tisr) & (tisr<=tend)]
    else:
        ioptreq = (None,) * tisr.size
        iisrreq = ((tstart <= tisr) & (tisr <= tend)).nonzero()[0]

    return iisrreq, ioptreq


def findindex2Dsphere(azimg, elimg, az, el):
    """
    finds nearest row,column index of projection on 2-D sphere.
    E.g. an astronomical or auroral camera image

    inputs:
    azimg: azimuth of image pixels (deg)
    elimg: elevation of image pixels (deg)
    az: azimuth of point you seek to find the index for (deg)
    el: elevation of point you seek to find the index for (deg)

    output:
    row, column of 2-D image closest to az,el


    brute force method of finding the row,col with the closest az,el using haversine method
    useful for:
    azimuth, elevation
    right ascension, declination
    latitude, longitude
    """
    az = atleast_1d(az)
    el = atleast_1d(el)
    assert azimg.ndim == 2 and elimg.ndim == 2
    assert isinstance(az[0], float) and isinstance(el[0], float)

    adist = anglesep(azimg, elimg, az, el)
    return unravel_index(adist.argmin(), azimg.shape)


def boilerplateapi(descr="loading, processing, plotting raw ISR data"):
    p = ArgumentParser(description=descr)
    p.add_argument("isrfn", help="HDF5 file (or path) to read")
    p.add_argument("-r", "--rtype", help="0: alt code. 1: plasma line. 3: long pulse", type=int, default=3)
    p.add_argument("-c", "--optfn", help="optical data HDF5 to read")  # ,nargs='+',default=('',)
    p.add_argument("-a", "--azelfn", help="plate scale file hdf5")  # ,nargs='+',default=('',)
    p.add_argument("--t0", help="time to extract 1-D vertical plot")
    p.add_argument("--acf", help="show autocorrelation function (ACF)", action="store_true")
    p.add_argument("--beamid", help="beam id 64157 is magnetic zenith beam", type=int, default=64157)
    p.add_argument("--vlim", help="min,max for SNR plot [dB]", type=float, nargs=2, default=(None, None))
    p.add_argument("--zlim", help="min,max for altitude [km]", type=float, nargs=2, default=(90.0, None))
    p.add_argument("--tlim", help="min,max time range yyyy-mm-ddTHH:MM:SSz", nargs=2, default=[None, None])
    p.add_argument("--flim", help="frequency limits to plots", type=float, nargs=2, default=(None, None))
    p.add_argument("-o", "--odir", help="directory to write files to", default=".")
    p = p.parse_args()

    return p
