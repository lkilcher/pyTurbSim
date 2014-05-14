"""
This is the PyTurbSim package that provides tools for emulating
o-TurbSim functionality. In particular it contains functions for
taking a TurbSim 'config' object and performing a TurbSim run that
matches that config. Note that TurbSim 'config' objects can be created
from a TurbSim 'input' file using the io.config module.

This package contains the following files:

 base.py       - A base module that defines TurbSim config objects (tscfg)
 
 main.py       - The main module that has the primary wrapper routines.
 
 profModels.py - A module that contains wrapper functions for
                 implementing the tscfg's mean-profile model.
                 
 turbModels.py - A module that contains wrapper functions for
                 implementing the tscfg's turbulence models
                 (specModel, cohereModel, stressModel).

Example usage
-------------
See either:
 1) the :mod:`.pyTurbSim` executable script in the PyTurbSim root directory
 2) The :mod:`pyts.runConfig.main` docstring for example usage.

"""

