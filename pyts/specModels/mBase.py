# !!!ADDDOC
try:
    from ..base import modelBase,ts_float,np,gridProps,calcObj
except ValueError:
    from base import modelBase,ts_float,np,gridProps,calcObj

class spec(gridProps,calcObj):

    def __init__(self,tsrun):
        self.grid=tsrun.grid
        self.data=np.zeros((tsrun.grid.n_comp,tsrun.grid.n_z,tsrun.grid.n_y,tsrun.grid.n_f),dtype=ts_float,order='F')
        
    @property
    def Suu(self,):
        return self.data[0]
    @property
    def Svv(self,):
        return self.data[1]
    @property
    def Sww(self,):
        return self.data[2]

    @property
    def tke(self,):
        # !!!ADDDOC
        return np.trapz(self.data,x=self.f,axis=-1)

    @property
    def flat(self,):
        return self.grid.flatten(self.data)

class turbModelBase(modelBase):
    """
    A base class for TurbSim turbulence models.
    """
    pow5_3=5./3.
    pow2_3=2./3.
        

