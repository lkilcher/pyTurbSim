Code Framework
==============

|pyts| is a Python 'package' organized into 'modules' and
'sub-packages' that provide a logical and functional framework for the
code and its use.  The primary components of this framework are:

1) The modules in the :mod:`.pyts` root folder, especially:

   a) :mod:`pyts.main`, which contains the high-level classes and
      functions that control the flow of |pyts| simulations.  Most
      importantly, this module defines:

      - :class:`pyts.main.tsrun`, this is the primary 'run' class of
        PyTurbSim, which controls and directs.
      - :class:`pyts.main.tsdata`, this is the |pyts| output-data
        class returned by :class:`pyts.main.tsrun` after execution.

   b) :mod:`pyts.base`, which contains abstract base classes for other
      components of the code (this is the foundation of the code
      structure).

2) The model packages, which contain predefined models of the statistics |pyts| is capable of simulating.

   a) :mod:`pyts.profModels`, contains the mean velocity profile
      models.
   b) :mod:`pyts.specModels`, contains the TKE spectral
      models.
   c) :mod:`pyts.stressModels`, contains the Reynold's
      stress profile models.
   d) :mod:`pyts.cohereModels`, contains the spatial
      coherence models.
   More details on model packages can be found in the :ref:`model-info` section.

3) The :mod:`pyts.io` package supports reading and writing of TurbSim
   input (.inp) and output files (e.g. .bl, .wnd, etc.).

4) Wrapper packages that implement different user interfaces of
   |pyts|:

   a) :mod:`pyts.runConfig` contains all the software for running
      |pyts| using :term:`input file`\ s (to mimic |ots|).
   b) :mod:`pyts.gui` contains the graphical user interface.

   For further information on how to use these interface see
   :doc:`usage`.

5) The 'tslib' folder and library.  This folder contains the Fortran
   code that implements the processor-intensive pieces of
   |pyts|. Having this library compiled for your system significantly
   speeds up |pyts|.  For information on properly installing this
   library, consult the :doc:`install` page.


.. _model-info:

Models vs. run-specific 'statistics'
------------------------------------
PyTurbSim makes a distinction between 'models' (PyTurbSim objects that
partially define a statistic) and run-specific 'stat-objects' which are the output
of these model objects (these are numpy array wrappers). Models are
independent of the spatial grid and other models in a PyTurbSim
run. The statistics are the values of the statistic that will be
reproduced in the PyTurbSim output.

PyTurbSim is primarily designed to produce output that matches four
statistics for each component of velocity (u,v,w):

1) The mean velocity profile (prof),
2) The turbulence energy spectrum (spec),
3) The spatial coherence (cohere), and
4) The Reynold's stresses (stress).

Within PyTurbSim each of these statistics may be defined in two
distinct ways. They may be defined using 'models' or using
'stat-objects' (essentially array wrappers). Models define a statistic
in terms of input parameters to a model and other variables of other
models.  For more information on specifying a statistic, see the four
statistic properties (prof, spec, cohere, and stress) of a tsrun
object.

Models
^^^^^^

Models define the functional form of a statistic and can depend on the
spatial grid or other stat-objects defined before it. When models are
used to compute statistics they are computed the order above
(1-4). This means that a turbulence energy spectrum model can depend
on the mean velocity profile, but not the coherence or
stress. Likewise the coherence can depend on the mean velocity and
turbulence spectrum, but not the stress, and so on.  (Even though
models cannot depend on the values of an array defined later, they can
depend on 'parameters' of that model.)



Stat-objects/arrays
^^^^^^^^^^^^^^^^^^^
Stat-objects, on the other hand, contain the values of the statistic
(an array) that will be reproduced in the PyTurbSim output. However,
because stat-objects are essentially wrappers for an array of the
values of the statistic, they do not have the flexibility to depend on
the values of other statistics.

Customizing PyTurbSim
---------------------
Need to add some examples here...
