"""
This is the turbulence spectrum package's base module.

"""
from ..base import modelBase, ts_float, np, gridProps, calcObj
from numpy import trapz


class specObj(gridProps, calcObj):

    """
    Spectral objects contain the array (self.array) of turbulence
    spectra values for a specific PyTurbSim run. This class defines
    various shortcuts to the data.

    Parameters
    ----------
    tsrun : `tsrun` type
        The PyTurbSim run object in which the spectra will be used.

    """

    def __init__(self, tsrun):
        self.grid = tsrun.grid
        self.array = np.zeros((tsrun.grid.n_comp,
                               tsrun.grid.n_z,
                               tsrun.grid.n_y,
                               tsrun.grid.n_f),
                              dtype=ts_float, order='F')

    @property
    def Suu(self,):
        """
        This is the u-component of the TKE spectrum.
        """
        return self.array[0]

    @property
    def Svv(self,):
        """
        This is the v-component of the TKE spectrum.
        """
        return self.array[1]

    @property
    def Sww(self,):
        """
        This is the w-component of the TKE spectrum.
        """
        return self.array[2]

    @property
    def tke(self,):
        """
        This is the component-wise turbulent kinetic energy.
        """
        return trapz(self.array, x=self.f, axis=-1)

    @property
    def flat(self,):
        """
        Return the partially-flattened spectral array.  This flattens
        the spatial dimensions of the spectral array (component and
        frequency dimensions are retained).

        For example, for a 5 x 4 spatial grid (nz=5,ny=4) with 1000
        frequency values, the size of the array in this spectral
        object will be 3 x 5 x 4 x 1000.  Performing this flatten
        operation will return a 3 x 20 x 1000 shaped spectral
        array. The ordering (row-major or column-major) is defined in
        the spatial grid class.

        This is used for input into the functions that calculate the
        coherence.

        """
        return self.grid.flatten(self.array)


class specModelBase(modelBase):

    """
    A base class for TurbSim spectral models.
    """
    pow5_3 = ts_float(5. / 3.)
    pow2_3 = ts_float(2. / 3.)
