"""
This is the TurbGen advanced programming interface
(API). This module provides a fully-customizable high-level
object-oriented interface to the TurbGen program.

The four components of this API are:

1) The :py:class:`~TurbGen.main.TGrun` class, which is the
controller/run object for TurbGen simulations.

2) The :func:`~.RectGrid` function, which is used to
define the TurbGen grid.

3) The 'model' classes, which include:

   a) :mod:`~TurbGen.profModels` (aliased here as 'pm'), contains the mean velocity
   profile models.

   b) :mod:`.specModels` (aliased here as 'sm'), contains the TKE spectral
   models.

   c) :mod:`.stressModels` (aliased here as 'rm'), contains the Reynold's
   stress profile models.

   d) :mod:`.cohereModels` (aliased here as 'cm'), contains the spatial
   coherence models.

   e) :mod:`.phaseModels`, contains the phase coherence (a.k.a.,
   temporal coherence) models.

4) The :mod:`io` module, which supports reading and writing of TurbSim
input (.inp) and output files (e.g. .bl, .wnd, etc.)

Example usage of this API can be found in the <tg_root>/Examples/api.py file.

.. literalinclude:: ../../../examples/api.py


"""
from main import TGrun
from base import RectGrid
import profModels.api as profModels
import specModels.api as specModels
import cohereModels.api as cohereModels
import stressModels.api as stressModels
import phaseModels.api as phaseModels
import io

# Set aliases to the model modules:
pm = profModels
sm = specModels
cm = cohereModels
rm = stressModels
