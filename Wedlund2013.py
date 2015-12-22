#!/usr/bin/env python3
"""
given energy deposition matrix A (based on MSIS/IRI/etc)
and measured electron number density Ne
estimate solution for q=A Phi
assuming quasi-stationary system such that
q = alpha * Ne^2
"""
from pathlib import Path
import h5py
from pandas import DataFrame
from numpy import atleast_1d,empty_like
from matplotlib.pyplot import figure,show
#
from gridaurora.chapman import chapman_profile


def isrdep(depfn):
    depfn = Path(depfn).expanduser()

    with h5py.File(str(depfn),'r',libver='latest') as f:
        A = f['/eigenprofile'].value
        zkm = f['/altitude'].value
        Ek = f['/Ebins'].value
        Ekedges = f['/EbinEdges'].value

    return A,zkm,Ek

def isrNeSim(NeFwd,Te):
    """
    From Wedlund 2013 Par. 40, Sheedhan and St.-Maurice 2004
    """
    hotind = Te>1200.
    alphaO2 = empty_like(Te,dtype=float)
    alphaNO = empty_like(Te,dtype=float)

    alphaO2[hotind] = 1.95e-7 * (300./Te[hotind])** 0.56  # Te>1200K
    alphaO2[~hotind]= 1.95e-7 * (300./Te[~hotind])**0.70

    alphaNO[hotind] = 3.02e-7 * (300./Te[hotind])** 0.56  # Te>1200K
    alphaNO[~hotind]= 3.50e-7 * (300./Te[~hotind])**0.69

    #NOTE: valid 100-250km altitude Wedlund 2013 Par. 42
    alpha = (0.478*alphaNO + 0.373*alphaO2)



if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(descripton='simple demo of solving for flux given ISR Ne measurement')
    p.add_argument('--depfn',help='energy deposition data HDF5 file',default='precompute/transcareigen.h5')
    p.add_argument('--nez0',help='SIMULATION peak ionization altitude [km]',default=110.,type=float)
    p.add_argument('--H',help='SIMULATION scale height [km]',default=20.,type=float)
    p = p.parse_args()

    A,zkm,Ek = isrdep(p.depfn)

    NeFWD = DataFrame(data=chapman_profile(p.nez0,zkm,p.H),
                      index=zkm)

    Te = atleast_1d(2000.) #TODO this should be per altitude in real measurements and sims

    isrNe2q(NeFWD,Te)





















#%% notes
"""
Wedlund et al 2013 'Estimating energy spectra of electron precipitation above auroral arcs
from ground-based observations with radar and optics'

A key result of the paper is their finding a better initial guess for the inversion.

The Introduction notes that we often desire to obtain an ionization profile to invert to get the
precipitation characteristics at the "top" of the ionosphere, which is often taken to
be ~1000km altitude, below which no significant particle acceleration takes place.

Par. 6 notes that ISR Ne observations have been used to estimate ionization profiles and
then E0, Q precipitation estimates along the Up-B beam only.

Par. 7 notes that optical inversions gave 10-15km B_\perp resolution, but only for angles near
magnetic zenith, and that increasing zenith angle increasingly washes out the horizontal resolution.

Par. 8-9 note that the ill-posed nature of the problem is manageable when multiple sensors are used
as in Tanaka 2011.

Par. 10 wraps up the Introduction by noting that 427.8nm N2+ emission and ISR Ne will be used
together for 3-D estimates of precipitation flux characteristics (lat/lon/energy)
* Question: at what resolution and error?

Section 2: ALIS/ISR experiment description
Five cameras, 256x256 pixels, 70-90 deg. FOV, 50km baseline separation. 5 sec. imaging cadence
four filters N2+1NG 4278 Å, O I(1S – 1D) 5577 Å, O I(1D – 3P) 6300 Å, OI(3p3P – 3s3S ) 8446 Å

IN THIS EXPERIMENT of March 5 2008, the 4278Å cadence was 10-20 sec.

Their assertition, since arc remained stable in intensity and morphology for 2-3 min. and this
is the transit time of Alfven wave from plasma sheet to ionosphere, the system can be treated
as quasi-static.

The ISR raw data was processed at 10 sec. cadence for Ne,Te,Ti in the magnetic zenith beam ONLY
Ion heating: no significant ion heating observed, so assuming convection E-fields are absent. (no Joule heating)

electron heating: rise from 1000K to as much as 3000K, before Ne increase by factor of 5-10.

Section 3: They use Rees-Sergienko-Ivanov energy deposition model
Production rate q is related to energy deposition matrix A and flux Phi
q = A * Phi
where Phi is the unknown flux to estimate,
A is modeled by Transcar, GLOW, Rees, etc.,
and
q = alpha * Ne^2  <=> Ne = sqrt(q/alpha)

Par 87: time evolution of event, noting E0, Q changes over 3 time steps. I would like to see more
time steps in between the 50,70 sec. time steps shown.
"""

