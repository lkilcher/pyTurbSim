try:
    from ..base import *
except ValueError:
    from base import *

class profModelBase(modelBase):
    """
    A base class for TurbSim profile models.
    """
    
    def __init__(self,tsConfig,grid):
        """
        Initialize the profModelBase, then calls the user-customizable `initModel' routine.
        """
        self.grid=grid
        self.config=tsConfig
        self._u=np.zeros([3]+list(self.grid.shape),dtype=np.float32,order='F')
        if hasattr(self,'initModel'):
            self.initModel()

    @property
    def _dudz(self,):
        if not hasattr(self,'_val_dudz'):
            self._val_dudz=np.concatenate(((self._u[:,1]-self._u[:,0])[:,None,:]/self.grid.dz,(self._u[:,2:]-self._u[:,:-2])/(2*self.grid.dz),(self._u[:,-1]-self._u[:,-2])[:,None,:]/self.grid.dz),axis=1)
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
        return self._u[0]
    @property
    def v(self,):
        """
        Returns the w-component of the mean velocity field.
        """
        return self._u[1]
    @property
    def w(self,):
        """
        Returns the w-component of the mean velocity field.
        """
        return self._u[2]

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
