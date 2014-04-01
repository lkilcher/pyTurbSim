"""
This is the velocity profile package's base module.

This module defines:
 profObj        - The mean-profile object class.
 profModelBase  - The base class for mean-profile models.

"""
from .. import base
np=base.np

class profObj(base.gridProps,base.calcObj):
    """
    Profile objects contain the array (self.array) of mean-velocity
    values for a specific PyTurbSim run. This class defines various
    shortcuts to the mean velocity data including:

    u     - The u-component mean-velocity array
    v     - The v-component mean-velocity array
    w     - The w-component mean-velocity array

    dudz  - The vertical shear of u-component.
    dvdz  - The vertical shear of v-component.
    dwdz  - The vertical shear of w-component.

    uhub  - The hub-height u-component mean-velocity.
    
    """

    def __init__(self,tsrun):
        """
        Create a profile object instance.

        Parameters
        ----------
        tsrun - The PyTurbSim run object in which the profile will be
                used.
        """
        self.grid=tsrun.grid
        self.array=np.zeros([3]+list(self.grid.shape),dtype=base.ts_float,order='F')

    @property
    def _dudz(self,):
        """
        This is a property for creating/returning the vertical shear.
        """
        if not hasattr(self,'_val_dudz'):
            self._val_dudz=np.concatenate(((self.array[:,1]-self.array[:,0])[:,None,:]/self.grid.dz,(self.array[:,2:]-self.array[:,:-2])/(2*self.grid.dz),(self.array[:,-1]-self.array[:,-2])[:,None,:]/self.grid.dz),axis=1)
        return self._val_dudz

    @property
    def uhub(self,):
        """
        Returns the u-component hub-height wind speed.
        """
        return self.u[self.grid.ihub]

    @property
    def u(self,):
        """
        Returns the w-component of the mean velocity field.
        """
        return self.array[0]
    @property
    def v(self,):
        """
        Returns the w-component of the mean velocity field.
        """
        return self.array[1]
    @property
    def w(self,):
        """
        Returns the w-component of the mean velocity field.
        """
        return self.array[2]

    @property
    def dudz(self,):
        """
        Returns the vertical derivative of the u-component of the mean velocity field.
        (Centered difference)
        """
        return self._dudz[0]
    @property
    def dvdz(self,):
        """
        Returns the vertical derivative of the v-component of the mean velocity field.
        (Centered difference)
        """
        return self._dudz[1]
    @property
    def dwdz(self,):
        """
        Returns the vertical derivative of the w-component of the mean velocity field.
        (Centered difference)
        """
        return self._dudz[2]

class profModelBase(base.modelBase):
    """
    A base class for TurbSim profile models.
    """
    pass
