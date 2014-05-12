"""
PyTurbSim is a program for producing simulations of turbulent velocity
time-series for input to device simulation tools (e.g. the NWTC's
FAST) that estimate wind- and water-turbine performance and loads.
PyTurbSim outputs 2-D planes (i.e. y-z) of 3-component velocity
(u,v,w) time-series [1]. In other words, PyTurbSim provides the
inflow information that 'drives' device simulations.

PyTurbSim is the official water-turbulence simulation tool for
marine hydrokinetic (MHK) turbine device simulation
(a.k.a. HydroTurbSim), and is also designed to be a valuable
development and testing platform for NREL's 'TurbSim' tool [2].


.. _intro-background:

Background
----------

TurbSim is a statistical rather than a physical or dynamic tool.  That
is, rather than solving fluid-flow equations (e.g. large eddy
simulations) it produces time-series that match specific statistics of
real flows.  PyTurbSim is capable of matching the following statistics
of any velocity dataset:

1) the mean velocity profile,
2) the turbulent kinetic energy spectrum (and therefore the turbulence intensity),
3) the Reynold's stress profile, and
4) the spatial coherence.

These statistics have been found to be critical predictors of
wind-turbine fatigue loading.  Therefore, though this tool does not
produce time-series that obey fluid-flow equations (i.e. the
Navier-Stokes equations, compressibility), it does provide time-series
that drive realistic wind and MHK turbine device simulation and it
does so using significantly lower computational resources than
fluid-flow simulations.  That is, TurbSim and PyTurbSim efficiently
produce time-series that drive realistic loads estimates that agree
reasonably with measurements of loads on real wind turbines [3].

A primary difference between o-TurbSim and PyTurbSim is that PyTurbSim
is designed to facilitate explicit user-control of the four statistics
listed above. O-TurbSim, on the other hand, is designed so that a user
selects from a pre-defined subset of these statistics.

History
^^^^^^^
pyTurbSim is a python-implementation of the National Wind Technology
Center's (NWTC) 'TurbSim' program. Throughout the documentation, the
term 'TurbSim' is used to refer to both PyTurbSim and the original
TurbSim tool (hereafter 'o-TurbSim').  O-TurbSim can be downloaded
here:
https://wind.nrel.gov/designcodes/preprocessors/turbsim/

PyTurbSim was originally written as a script for developing and
testing new profile and turbulence models that would later be
incorporated into o-TurbSim. The idea was that the script could be
quickly modified and executed to produce new output that could be
compared to measured datasets (for validating new models) or o-TurbSim
output (for validating the script). Once a new model had been
developed it could then be incorporated into o-TurbSim and released as
part of o-TurbSim.  As the 'PyTurbSim script' was developed to
simplify its use it became a full-fledged program of its own with some
capabilities that exceed o-TurbSim. O-TurbSim has capabilities that
are not included in PyTurbSim as well; see the capabilities.txt file for
a comparison of capabilities of these two tools.

The PyTurbSim documentation is largely based on O-TurbSim's documentation. For
additional information consider looking at that document:
https://wind.nrel.gov/designcodes/preprocessors/turbsim/TurbSim.pdf

Usage
-----

PyTurbSim has three primary operational modes/interfaces.
  1) input files,
  2) direct python interface, and
  3) a graphical user interface.

  -- Input Files (runConfig package)
  This mode is designed to mimic the o-TurbSim interface. It is
  designed for use by device developers and other users familiar with
  the o-TurbSim program who want output that is consistent with
  predifined models built into TurbSim. In this mode pyTurbSim reads
  o-TurbSim input files and writes out binary data in the same format
  as o-TurbSim. This mode can be run from a standard (i.e. DOS, UNIX)
  command line and is well suited for interfacing with FAST and other
  device simulation tools in the same way that o-TurbSim does.  For
  more information on this mode, see the docstring in the
  runConfig/__init__.py file.

  -- Python Interface (api.py file)
  This is the core interface of PyTurbSim (the other two are
  wrappers). As such, this mode provides more control over output
  (access to lower-level functions). This interface was designed for
  controlling the four statistics above (\ :ref:`intro-background` section)
  explicitly without modifying the program itself.  It is likely to be
  particularly useful to users familiar with python who are developing
  and testing new turbulence models that will be incorporated into the
  tool.  As a starting point for using this interface see the api.py
  docstring.

  -- Graphical User Interface (gui package, aka gTurbSim)
  A graphical user interface (gui) was developed for reading and
  writing TurbSim input files.  The gui was designed to help new users
  of TurbSim in understanding and writing input files. The gui can
  be used to run O-TurbSim.  The python script gTurbSim.py will run the
  gui.  For more information see the gui/__init__.py docstring.
  

Dependencies
------------

PyTurbSim depends on Python and numpy. The gui (gTurbSim) also
requires wxPython.


Notes and Citations
-------------------

 [1] At the most basic level PyTurbSim output is a four-dimensional
     array.  The dimensions are:
       1) velocity component (size 3, corresponding to u,v,w),
       2) z spatial dimension (size n_z = number of z-points)
       3) y spatial dimension (size n_y = number of y-points)
       4) time dimension (size n_t = number of timesteps)
     TurbSim implicitly makes the 'frozen flow hypothesis' and so the
     time-dimension can also, roughly, be considered the x spatial
     dimension.  

 [2] The NWTC is a center at the Department of Energy's (DOE) National
 Renewable Energy Lab (NREL).  The DOE provided funding for development
 of these tools.

 [3] Moriarty, P. J.; Holley, W. E. & Butterfield, S. Effect of
 turbulence variation on extreme loads prediction for wind turbines
 Transactions of the American Society of Mechanical Engineers Journal
 of Solar Energy Engineering, AMERICAN SOCIETY MECHANICAL ENGINEERS,
 2002, 124, 387-395
"""
from api import *

