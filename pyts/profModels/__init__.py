"""\namespace profModels
This is the PyTurbSim mean velocity 'profile models' package.  This
package contains pre-defined profile models that can be implemented in
a PyTurbSim run.

This package contains:
 api.py        - The API for this package.
 mBase.py      - The package's base module defines classes used by
                 models in the package.
 iec.py        - Contains International Electrotechnical Commission
                 (IEC) profile models.
 log.py        - Contains logarithmic mean velocity profile models.
 power.py      - Contains power-law mean velocity profile models.

For more information and to use this module import the profModels.api
package, e.g.:
import pyts.profModels.api as pm

"""
