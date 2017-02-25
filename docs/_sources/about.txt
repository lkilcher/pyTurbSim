.. _about:

About
-----

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
reasonably with measurements of loads on real wind turbines [#]_.

.. _about.history:

History
^^^^^^^
pyTurbSim is a python-implementation of the National Wind Technology
Center's (NWTC) 'TurbSim' program [#]_. Throughout the documentation,
the term 'TurbSim' is used to refer to both PyTurbSim and the original
TurbSim tool (hereafter '|ots|').  |ots| is still actively
maintained and available from the `NWTC design codes site
<https://wind.nrel.gov/designcodes/preprocessors/turbsim/>`_.

PyTurbSim was originally written as a script for developing and
testing new profile and turbulence models that would later be
incorporated into |ots|. The idea was that the script could be
quickly modified and executed to produce new output that could be
compared to measured datasets (for validating new models) or |ots|
output (for validating the script). Once a new model had been
developed it could then be incorporated into |ots| and released as
part of |ots|.  As the 'PyTurbSim script' was developed to
simplify its use it became a full-fledged program of its own with some
capabilities that exceed |ots|. |ots| has capabilities that
are not included in PyTurbSim as well; see the capabilities.txt file for
a comparison of capabilities of these two tools.

PyTurbSim does supports some, but not all spectral models of the
original (atmospheric) TurbSim program.  Furthermore, PyTurbSim does
not support the 'coherent structures' functionality that Neil Kelley
developed.  For producing simulations of atmospheric turbulence, I
highly recommend using the original TurbSim program, developed by
Bonnie Jonkman and Neil Kelley (based on the original SNLWIND tool
developed by Paul Veers).  That having been said, I believe the
'SMOOTH' and 'IEC' spectral models are accurately represented by this
tool.  All other spectral models have not been verified or are not
included in this tool.  PyTurbSim would not be possible without the
work of Niel Kelley, Paul Veers and especially Bonnie Jonkman.  Thank
you to all of these people for their excellent work and support in
creating this tool.

The PyTurbSim documentation is based on `O-TurbSim's documentation
<https://wind.nrel.gov/designcodes/preprocessors/turbsim/TurbSim.pdf>`_. For
additional information, especially regarding the 'config'/'input' file
operational mode, take a look at that document.

License
^^^^^^^
PyTurbSim is released publically by the National Renewable Energy Lab
under the FreeBSD license (see the COPYRIGHT file in the
`repository <http://github.com/lkilcher/pyTurbSim>`_).


===============

.. [#] Moriarty, P. J.; Holley, W. E. & Butterfield, S. Effect of
       turbulence variation on extreme loads prediction for wind turbines
       Transactions of the American Society of Mechanical Engineers Journal
       of Solar Energy Engineering, AMERICAN SOCIETY MECHANICAL ENGINEERS,
       2002, 124, 387-395

.. [#] The NWTC is a center at the Department of Energy's (DOE) National
       Renewable Energy Lab (:term:`NREL`).  The DOE provided funding for development
       of these tools.
