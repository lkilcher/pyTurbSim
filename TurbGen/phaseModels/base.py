"""
This is the base module for phase models.  Phase models produce the
initial phase information that is then correlated in the stress and
coherence models.

The basic phase model simply returns a 'random' array.

"""
from ..base import modelBase, calcObj, ts_complex, gridProps
import numpy as np


class phaseModelBase(modelBase):
    pass


class phaseObj(gridProps, calcObj):

    """
    Profile objects contain the array (self.array) of mean-velocity
    values for a specific TurbGen run.

    Profile objects are created with/for a specific TurbGen run.

    Parameters
    ----------
    tgrun :     :class:`tgrun <TurbGen.main.tgrun>`
                The TurbGen run object in which the profile will be
                used.

    See also
    --------
    profModelBase : The abstract base class for classes that create this class.

    """

    def __init__(self, tgrun):
        self.grid = tgrun.grid
        self.array = np.zeros((tgrun.grid.n_comp,
                               tgrun.grid.n_p,
                               tgrun.grid.n_f),
                              dtype=ts_complex, order='F')
