"""
A central purpose of TurbSim is to produce time-series of velocity
that are correlated spatially and in a way that is consistent with
observations.  In particular, TurbSim produces time-series with
specific frequency-dependent correlations between all pairs of points;
this is the 'coherence'.

Loosely defined, coherence is the frequency dependence of the
correlation between velocity signals at different points in space.
Specically, for two signals u1 and u2 (e.g. velocity signals at points
'z1,y1' and 'z2,y2'), the coherence is defined as:

  Coh_(u1,u2) = C_(u1,u2)^2/(S_(u1)*S_(u2))
  
Where C_(u1,u2) is the cross-spectral density between signals u1 and
u2, and S_(u1) is the auto-spectral density of signal u1 (similar for
S_(u2)).

This module provides 'coherence models' which are specific spatial
coherence forms (functions of frequency) for each component of
velocity for all pairs of points in the grid.

"""
# !!!ADDDOC: Need more examples here.
import main

iec=main.iec
nwtc=main.nwtc
none=main.none
