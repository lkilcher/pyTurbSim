# !!!ADDDOC
from .mBase import turbModelBase,np,spec,ts_float

class tidal(turbModelBase):
    # !!!ADDDOC
    s_coef=np.array([[1.21,4.3],[0.33,0.50],[0.23,0.26]],dtype=ts_float)

    def __init__(self,Ustar,RefHt):
        self.Ustar=Ustar
        self.Zref=RefHt
        
    def __call__(self,tsrun):
        out=spec(tsrun)
        dudz=np.abs(tsrun.prof.dudz[None,:,:,None])
        out.sigma2=self.Ustar**2*np.array([4.5,2.25,0.9])[:,None]*np.exp(-2*tsrun.grid.z[None,:]/self.Zref)
        out[:]=(out.sigma2[:,:,None,None]*self.s_coef[:,0][:,None,None,None]/dudz)/(1+self.s_coef[:,1][:,None,None,None]*(tsrun.grid.f[None,None,None,:]/dudz)**self.pow5_3)
        return out

class river(tidal):
    # !!!ADDDOC
    # These fit positive velocity data in eastriver:
    s_coef=np.array([[1.057,3.432],[0.351,0.546],[0.265,0.341]],dtype=ts_float)
    # These fit negative velocity data in eastriver:
    #s_coef=np.array([[0.784,2.085],[0.272,0.357],[0.240,0.290]])

