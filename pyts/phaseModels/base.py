"""
This is the base module for phase models.  Phase models produce the
initial phase information that is then correlated in the stress and
coherence models.

The basic phase model simply returns a 'random' array.

"""
from ..base import modelBase, np, ts_complex


class phaseModelBase(modelBase):
    pass
