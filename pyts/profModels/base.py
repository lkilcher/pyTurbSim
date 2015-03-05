"""
This is the velocity profile package's base module.

"""
from ..base import np, gridProps, calcObj, modelBase, ts_float


class profObj(gridProps, calcObj):

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
        self.array = np.zeros(
            [3] + list(self.grid.shape), dtype=ts_float, order='F')

    @property
    def _dudz(self,):
        """
        This is a property for creating/returning the vertical shear.
        """
        if not hasattr(self, '_val_dudz'):
            self._val_dudz = np.concatenate(
                ((self.array[:, 1] - self.array[:, 0])[:, None, :] / self.grid.dz,
                 (self.array[:, 2:] - self.array[:, :-2]) / (2 * self.grid.dz),
                 (self.array[:, -1] - self.array[:, -2])[:, None, :] / self.grid.dz),
                axis=1)
        return self._val_dudz

    @property
    def uhub(self,):
        """
        The u-component hub-height wind speed.
        """
        return self.u[self.grid.ihub]

    @property
    def u(self,):
        """
        The w-component of the mean velocity field.
        """
        return self.array[0]

    @property
    def v(self,):
        """
        The w-component of the mean velocity field.
        """
        return self.array[1]

    @property
    def w(self,):
        """
        The w-component of the mean velocity field.
        """
        return self.array[2]

    @property
    def dudz(self,):
        """
        The vertical derivative of the u-component of the mean velocity field.
        (Centered difference)
        """
        return self._dudz[0]

    @property
    def dvdz(self,):
        """
        The vertical derivative of the v-component of the mean velocity field.
        (Centered difference)
        """
        return self._dudz[1]

    @property
    def dwdz(self,):
        """
        The vertical derivative of the w-component of the mean velocity field.
        (Centered difference)
        """
        return self._dudz[2]


class profModelBase(modelBase):

    """
    A base class for TurbSim profile models.
    """
    pass
