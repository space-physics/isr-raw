========================
AMISR raw data utilities
========================
Utilities for working with Incoherent Scatter Radar data, especially from Poker Flat AMISR.

We work with the complex IQ voltage samples, the lowest level data available from the radar (after integration of several pulses, perhaps on the 0.1 milliscond time scale).

Coming soon, simultaneous plots with high speed multi-camera synchronized video.

Tested on Python 3.5

.. contents::

Install
=======
::

    git clone https://github.com/scienceopen/isrutils
    python setup.py develop

File Types
==========
Currently, these raw data files are *not* currently contained on `Madrigal <http://isr.sri.com/madrigal>`_, you will have to email SRI staff to get them manually.

===========   ==================
File ext.      Data Type
===========   ==================
dt0.h5        Ion Line: Alternating Code
dt1.h5        Downshifted Plasma line (negative Doppler shift)
dt2.h5        Upshifted Plasma line (positive Doppler shift)
dt3.h5        Ion Line: Long Pulse (small Doppler )
===========   ==================


Discussion
==========

The "ion line" measurement bandwidth is ~ +/- 100 kHz from the radar center frequency, and contains the data necessary for volume estimates of Electron Density, Ion Temperature, Electron Temperature, and Ion Velocity,
under certain assumptions for species composition vs. altitude. Some of the need to make assumptions about atmospheric composition can be mitigated with combined ion/plasma line inversion, among numerous other benefits.
The plasma line returns have several MHz of bandwidth, but most of the energy is contained in narrower bands upshifted and downshifted from the center frequency.

No one radar waveform is optimal for all conditions, particularly with regard to the spatio-temporal sampling dilemma.
Incoherent scattering from tiny particles gives exceedingly weak returns, and even with many billions of particles in the scattering volume, it takes well over ten thousand radar pulses to build a statistical basis for a usable autocorrelation function (ACF).
The shape of the ACF is fitted to estimate certain plasma parameters, given assumptions on the particle population that may be violated, causing in some limited
sets of cases either inaccurate fits or a failure to estimate the parameters.



References
==========
.. [1] H. Nilsson et al. `"Enhanced incoherent scatter plasma lines", Annales Geophysicae, 1997 <http://dx.doi.org/10.1007/s00585-996-1462-z>`_
.. [2] E. Kudeki and M. Milla "Incoherent Scatter Radar — Spectral Signal Model and Ionospheric Applications", 2012, in:  Doppler Radar Observations - Weather Radar, Wind Profiler, Ionospheric Radar, and Other Advanced Applications, Dr. Joan Bech (Ed.), ISBN: 978-953-51-0496-4, InTech, DOI: 10.5772/39010. <http://www.intechopen.com/books/doppler-radar-observations-weather-radar-wind-profiler-ionospheric-radar-and-other-advanced-applications/incoherent-scatter-radar-spectral-measurements-and-ionospheric-applications>`_
