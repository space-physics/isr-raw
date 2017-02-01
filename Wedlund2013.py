#!/usr/bin/env python
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
from xarray import DataArray
from numpy import empty_like,column_stack
from matplotlib.pyplot import show,subplots
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
    Te = Fwd.loc[:,'Te']
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
    q = alpha * Fwd.loc[:,'Ne']**2
    return q

def phantom(Z0,H,zkm):
    Fwd = DataArray(data=column_stack(( 1e5 * chapman_profile(p.nez0,zkm,p.H), #[electrons cm^-3]
                                        maxwellian(zkm,220,2e9)[0])),# this is a repurposing of the maxwellian normally used for energy
                    dims=['altitude','type'],
                    coords={'altitude':zkm,'type':['Ne','Te']})
    #Fwd['Ne'] += 5e4 * chapman_profile(300,zkm,50) # < 500eV
    return Fwd

def doplot(Fwd,q,zlim):
    fg,axs = subplots(2,2,sharey=True)
#%% electron number density
    ax = axs[0,0]
    ax.plot(Fwd.loc[:,'Ne'], Fwd.altitude)
    ax.set_title('electron number density')
    ax.set_ylabel('altitude [km]')
    ax.set_xlabel('electron number density [e$^-$ cm$^{-3}$]')
#%% Electron temperature
    ax = axs[0,1]
    ax.plot(Fwd.loc[:,'Te'], Fwd.altitude)
    ax.set_title('Electron Temperature')
    ax.set_xlabel('Tempature [K]')
#%% production
    ax= axs[1,0]
    ax.plot(q, q.altitude)
    ax.set_title('Production')
    ax.set_ylabel('altitude [km]')
    ax.set_xlabel('ionization rate [cm$^{-3}$ s$^{-1}$]')

    [a.set_ylim(zlim) for a in axs.ravel()]

    fg.suptitle('Forward Model',fontsize='x-large')

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
