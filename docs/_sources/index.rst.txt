.. PyTurbSim documentation master file, created by
   sphinx-quickstart on Tue Apr  1 12:34:10 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyTurbSim's home page
==================================
|pyts| is a program for producing simulations of turbulent velocity
time-series for input to device simulation tools that estimate water-
and wind-turbine performance and loads.  |pyts| outputs spatial
time-series (a sequence of 2-D, y-z, planes) of 3-component velocity
(u,v,w) that match statistics of real oceanic, riverine and wind
turbulence [#]_.  In other words, |pyts|  provides the inflow
information that 'drives' device simulations.  See the :ref:`about`
page for more information.

|pyts| is the official water-turbulence simulation tool for
hydrokinetic turbine device simulation (a.k.a. HydroTurbSim), and is
also a valuable development and testing platform for NREL's 'TurbSim'
tool (see :ref:`about.history`\ ).  New mean-profile, spectral and
coherence models can be implemented easily in a pythonic,
object-oriented manner, and plotting routines for comparing output
to targets and/or data are included.

Table of Contents
=================

.. toctree::
   :maxdepth: 3
   
   about
   install
   usage
   plotting-tools
   code-framework
   api/pyts
   glossary
   

Indices, tables and notes
=========================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :doc:`glossary`

.. [#] At the most basic level |pyts| output is a four-dimensional
       array.  The dimensions are:
    
       1) velocity component (size 3, corresponding to u,v,w),
       2) z spatial dimension (size n_z = number of z-points)
       3) y spatial dimension (size n_y = number of y-points)
       4) time dimension (size n_t = number of timesteps)

       TurbSim implicitly makes the 'frozen flow hypothesis' and so the
       time-dimension can also, roughly, be considered the x spatial
       dimension.  
