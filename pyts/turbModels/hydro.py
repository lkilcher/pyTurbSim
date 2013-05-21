from .mBase import *

class hydroGen(turbModelCohNonIEC):
    pow5_3=ts_float(5./3.)
    
    def calcAutoSpec(self,):
        dudz=np.abs(self.profModel.dudz.flatten(order='C')[None,:,None])
        self._autoSpec[:]=(self.sigma2[:,:,None]*self.s_coef[:,0][:,None,None]/dudz)/(1+self.s_coef[:,1][:,None,None]*(self.f[None,None,:]/dudz)**self.pow5_3)

class tidal(hydroGen):
    s_coef=np.array([[1.21,4.3],[0.33,0.50],[0.23,0.26]])

    def initModel(self,):
        self.sigma2=((self.UStar**2*np.array([4.5,2.25,0.9])[:,None]*np.exp(-2*self.grid.z[None,:]/self.RefHt))[:,:,None]*np.ones((1,1,self.grid.n_y))).reshape((3,self.grid.n_z*self.grid.n_y))


class river(tidal):
    # These fit positive velocity data in eastriver:
    s_coef=np.array([[1.057,3.432],[0.351,0.546],[0.265,0.341]])
    # These fit negative velocity data in eastriver:
    #s_coef=np.array([[0.784,2.085],[0.272,0.357],[0.240,0.290]])


