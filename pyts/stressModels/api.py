"""
PyTurbSim 'Reynold's stress models' package.

The Reynold's stress quantifies correlations betweens turbulent
velocity components. It has three components: <u'v'>, <u'w'> and
<v'w'> ('<x>' denotes an 'appropriate' time average of the quantity
'x').

Available stress models:
------------------------

:class:`.main.uniform` (alias: uniform)
  A uniform Reynold's stress over the spatial domain.

:class:`hydro.tidal <pyts.stressModels.hydro.tidal>` (alias: tidal)
  The 'tidal` Reynold's stress model (increases linearly toward the
  seafloor/ground).

:class:`.stressModelBase`
  This is the base class for stress models. To create a new one,
  subclass this class or subclass and modify an existing stress
  model.

:class:`.stressObj`
  This is the 'stress object' class.  All stress model `__call__`
  methods must take a :class:`tsrun <pyts.main.tsrun>` as input and
  return this class.


Example usage
-------------
import pyts.stressmodels.api as rm

Create a uniform Reynold's stress model where each component is
specified explicitly:

>>> my_stress_model=rm.uniform(upvp_=0.01,upwp_=0.1,vpwp_=0.0)

This stress model can then be applied to a tsrun (see
pyts.main.tsrun):

>>> tsrun.stress=my_stress_model(tsrun)

See also
--------
For a description of the difference between 'stress models'
(e.g. 'my_stress_model' in example above) and the stress they output
(tsrun.prof), see the 'models_and_stats_example.py' file.

"""
from .base import stressModelBase, stressObj
from .main import uniform
from .hydro import tidal
