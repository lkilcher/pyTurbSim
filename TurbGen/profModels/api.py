"""
TurbGen mean velocity 'profile models' package.

Available profile models
------------------------

:class:`log_models.nwtc <.log.nwtc>` (alias: log)
  The nwtc logarithmic mean wind-speed profile.

:class:`log_models.H2O <.log.H2O>` (alias: h2l)
  The hydro (water) logarithmic mean velocity profile.

:class:`power_models.nwtc <.power.nwtc>` (alias: pl)
  The nwtc 1/7 power-law mean wind-speed profile.

:class:`iec_models.main <.iec.main>` (alias: iec)
  The IEC mean wind-speed profile.

:class:`profModelBase <.profModelBase>`
  This is the base class for profile models. To create a new profile
  model, subclass this class or subclass and modify an existing
  profile model.

:class:`profObj <.profObj>`
  This is the 'profile object' class.  All profile model `__call__`
  methods must take a :class:`TGrun <TurbGen.main.TGrun>` as input and
  return this class.

Example usage
-------------

>>> import TurbGen.profModels.api as pm

Create a logarithmic mean wind-speed 'profile model' with 18m/s wind
at 80m, and surface roughness length of 1m:

>>> my_prof_model=pm.log(18,80,1)

# Now set 'tgrun' to use this profile model:

>>> tgrun.prof=my_prof_model(tgrun)


Creating a new profile model
----------------------------

Creating new profile models in TurbGen is simple. Simply subclass
:class:`.profModelBase`, then:

  1) write an `__init__` method that takes inputs that define the
  profile model *in general* (i.e. irrespective of the spatial grid or
  other statistics of the flow), and

  2) write a `__call__` method that takes :class:`.TGrun`
  as input and returns a :class:`.profObj`, which

For example::

  import TurbGen.profModels.api as pm # import the profModels api
  from numpy import polyval # Import helper functions.

  class my_new_model(pm.profModelBase):
      \"""
      A polynomial mean-velocity profile, where coefficients can be
      specified at initialization.
      \"""

      def __init__(self,Uref,Zref,poly_coefs=[1.,0.]):
          # All units should be in meters and seconds.
          self.Uref=Uref
          self.Zref=Zref
          self.poly_coefs=poly_coefs

      def __call__(self, tgrun):
          out=pm.profObj(tgrun)
          # Note here that tgrun contains the 'grid information', and
          # we can use that information to construct the profObj.
          out[0]=self.Uref*numpy.polyval(self.poly_coefs,tgrun.grid.z/Zref)
          # Here we have set the u-component (index 0) to follow the
          # polynomial, and we leave the other components to be zero.
          return out

That's all that is required to define a new profile model!  Now,
assuming you have already created a :class:`.TGrun`
instance (e.g. `tgr`) you set that :class:`.TGrun` to
use your new model by simply doing, for example:

>>> tgr.prof = my_new_model(3.,20,[.5,0])

Now your TurbGen run will utilize your newly defined model!

Notes
-----

For a description of the difference between 'profile models'
(e.g. 'my_prof_model' in example above) and the profile they output
(tgrun.prof), see the :doc:`../code-framework` section of the TurbGen
documentation.


"""
from . import log as log_models
from . import power as power_models
from . import iec as iec_models
#from jet import main as jet
from . import simple
from .base import profModelBase

# Alias the log models
h2l = log_models.H2O
log = log_models.nwtc

# Alias the power-law model
pl = power_models.nwtc

# Alias the iec model.
iec = iec_models.main

uniform = simple.uniform
linear = simple.linear
