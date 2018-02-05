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
    values for a specific PyTurbSim run.

    Profile objects are created with/for a specific PyTurbSim run.

    Parameters
    ----------
    tsrun :     :class:`tsrun <pyts.main.tsrun>`
                The PyTurbSim run object in which the profile will be
                used.

    See also
    --------
    profModelBase : The abstract base class for classes that create this class.

    """

    def __init__(self, tsrun):
        self.grid = tsrun.grid
        self.array = np.zeros((tsrun.grid.n_comp,
                               tsrun.grid.n_p,
                               tsrun.grid.n_f),
                              dtype=ts_complex, order='F')
