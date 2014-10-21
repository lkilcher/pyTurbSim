"""
PyTurbSim turbulence 'spectra models' API.

Available spectral models
-------------------------

:func:`.nwtc.smooth` (alias: smooth)
  The nwtc 'smooth' spectral model.

:func:`.nwtc.nwtcup` (alias: nwtcup)
  The nwtc 'upwind' spectral model.

:class:`hydro.tidal <pyts.specModels.hydro.tidal>` (alias: tidal)
  The hydro 'tidal' spectral model.

:class:`.hydro.river` (alias: river)
  The hydro 'river' spectral model.

:class:`.iec.ieckai`  (alias: ieckai)
  The IEC 'Kaimal' spectral model.

:class:`.iec.iecvkm`  (alias: iecvkm)
  The IEC 'Von-Karman' spectral model.

:class:`specModelBase <.mBase.specModelBase>`
  This is the base class for spectral models. To create a new spectral
  model, subclass this class or subclass and modify an existing
  spectal model.

:class:`specObj <.mBase.specObj>`
  This is the 'spectral object' class.  All spectral model `__call__`
  methods must take a :class:`tsrun <pyts.main.tsrun>` as input and
  return this class.

Example usage
-------------

>>> import pyts.specModels.api as sm

Create a `smooth` spectral model with friction velocity Ustar=1m/s and Richardson number Ri=0.6:

>>> my_spec_model=sm.smooth(1.0,0.6)

Now set a :class:`pyts.main.tsrun` instance to use this spectral model:

>>> tsrun.spec=my_spec_model(tsrun)

Notes
-----

For a description of the difference between 'spectral models'
(e.g. 'my_spec_model' in example above) and the spectral array they
output (tsrun.spec), see the :doc:`../code-framework` section of the PyTurbSim
documentation.

"""
import hydro
import nwtc
import iec
from .mBase import specModelBase, specObj

# Shortcut the hydro models
tidal = hydro.tidal
river = hydro.river

# Shortcut the nwtc models
nwtcup = nwtc.nwtcup
smooth = nwtc.smooth

# Shortcut the iec models
ieckai = iec.IECKai
iecvkm = iec.IECVKm
