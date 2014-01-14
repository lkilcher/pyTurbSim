# !!!ADDDOC
try:
    from .. import base
except ValueError:
    import base
np=base.np

class prof(base.gridProps,base.calcObj):

    def __init__(self,tsrun):
        self.grid=tsrun.grid
        self.data=np.zeros([3]+list(self.grid.shape),dtype=base.ts_float,order='F')

    @property
    def _dudz(self,):
        if not hasattr(self,'_val_dudz'):
            self._val_dudz=np.concatenate(((self.data[:,1]-self.data[:,0])[:,None,:]/self.grid.dz,(self.data[:,2:]-self.data[:,:-2])/(2*self.grid.dz),(self.data[:,-1]-self.data[:,-2])[:,None,:]/self.grid.dz),axis=1)
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
        return self.data[0]
    @property
    def v(self,):
        """
        Returns the w-component of the mean velocity field.
        """
        return self.data[1]
    @property
    def w(self,):
        """
        Returns the w-component of the mean velocity field.
        """
        return self.data[2]

    @property
    def dudz(self,):
        """
        Returns the vertical derivative of the u-component of the mean velocity field.
        """
        return self._dudz[0]
    @property
    def dvdz(self,):
        """
        Returns the vertical derivative of the v-component of the mean velocity field.
        """
        return self._dudz[1]
    @property
    def dwdz(self,):
        """
        Returns the vertical derivative of the w-component of the mean velocity field.
        """
        return self._dudz[2]

class profModelBase(base.modelBase):
    """
    A base class for TurbSim profile models.
    """
    pass
