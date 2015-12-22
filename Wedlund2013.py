#!/usr/bin/env python3
"""
given energy deposition matrix A (based on MSIS/IRI/etc)
and measured electron number density Ne
estimate solution for q=A Phi
assuming quasi-stationary system such that production rate
q = alpha * Ne^2
where alpha is the dissociative recombination rate assuming Ni~Ne
"""
from pathlib import Path
import h5py
from pandas import DataFrame
from numpy import empty_like
from matplotlib.pyplot import figure,show,subplots
import seaborn as sns
sns.set_context('talk',font_scale=1.5)
#
from gridaurora.eFluxGen import maxwellian
from gridaurora.chapman import chapman_profile


def isrdep(depfn):
    depfn = Path(depfn).expanduser()

    with h5py.File(str(depfn),'r',libver='latest') as f:
        A = f['/eigenprofile'].value
        zkm = f['/altitude'].value
        Ek = f['/Ebins'].value
        Ekedges = f['/EbinEdges'].value

    return A,zkm,Ek

def isrNe2q(Fwd):
    """
    From Wedlund 2013 Par. 40, Sheedhan and St.-Maurice 2004
    """
    Te = Fwd['Te']
    hotind = Te.values>1200.
    alphaO2 = empty_like(hotind,dtype=float)
    alphaNO = empty_like(hotind,dtype=float)

    alphaO2[hotind] = 1.95e-7 * (300./Te[hotind])** 0.56  # Te>1200K
    alphaO2[~hotind]= 1.95e-7 * (300./Te[~hotind])**0.70

    alphaNO[hotind] = 3.02e-7 * (300./Te[hotind])** 0.56  # Te>1200K
    alphaNO[~hotind]= 3.50e-7 * (300./Te[~hotind])**0.69

    #NOTE: valid 100-250km altitude Wedlund 2013 Par. 42
    alpha = (0.478*alphaNO + 0.373*alphaO2) #[cm^3 s^-1]
#%% now invoke quasi-static q=alpha*Ne**2
    q = alpha * Fwd['Ne']**2
    return q

def phantom(Z0,H,zkm):
    Fwd = DataFrame(index=zkm,columns=['Ne','Te'])
    Fwd['Ne'] = 1e5 * chapman_profile(p.nez0,zkm,p.H) #[electrons cm^-3]
    # yes this is a repurposing of the maxwellian normally used for energy
    Fwd['Te'] = maxwellian(zkm,220,2e9)[0]
    return Fwd

def doplot(Fwd,q,zlim):
    fg,axs = subplots(2,2,sharey=True)
#%% electron number density
    ax = axs[0,0]
    ax.plot(Fwd['Ne'].values,Fwd.index)
    ax.set_title('electron number density')
    ax.set_ylabel('altitude [km]')
    ax.set_xlabel('electron number density [e$^-$ cm$^{-3}$]')
#%% Electron temperature
    ax = axs[0,1]
    ax.plot(Fwd['Te'].values,Fwd.index)
    ax.set_title('Electron Temperature')
    ax.set_xlabel('Tempature [K]')
#%% production
    ax= axs[1,0]
    ax.plot(q.values,q.index)
    ax.set_title('Production')
    ax.set_ylabel('altitude [km]')
    ax.set_xlabel('ionization rate [cm$^{-3}$ s$^{-1}$]')

    [a.set_ylim(zlim) for a in axs.ravel()]

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='simple demo of solving for flux given ISR Ne measurement')
    p.add_argument('--depfn',help='energy deposition data HDF5 file',default='precompute/transcareigen.h5')
    p.add_argument('--nez0',help='SIMULATION peak ionization altitude [km]',default=110.,type=float)
    p.add_argument('--H',help='SIMULATION scale height [km]',default=15.,type=float)
    p.add_argument('--zlim',help='plotting, altitude limits [km]',default=(90,300),type=float)
    p = p.parse_args()

    A,zkm,E = isrdep(p.depfn)

    Fwd = phantom(p.nez0,p.H,zkm)

    q = isrNe2q(Fwd)

#%% plot
    doplot(Fwd,q,p.zlim)
    show()


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

