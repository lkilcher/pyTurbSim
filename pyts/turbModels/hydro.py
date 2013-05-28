from .mBase import *

class hydroGen(turbModelCohNonIEC):
    pow5_3=ts_float(5./3.)

class tidal(hydroGen):
    s_coef=np.array([[1.21,4.3],[0.33,0.50],[0.23,0.26]])

    def initModel(self,):
        """
        
        """
        dudz=np.abs(self.profModel.dudz[None,:,:,None])
        self.sigma2=self.UStar**2*np.array([4.5,2.25,0.9])[:,None]*np.exp(-2*self.grid.z[None,:]/self.RefHt)
        self._autoSpec[:]=(self.sigma2[:,:,None,None]*self.s_coef[:,0][:,None,None,None]/dudz)/(1+self.s_coef[:,1][:,None,None,None]*(self.f[None,None,None,:]/dudz)**self.pow5_3)

    def initStress(self,):
        """
        The tidal model Reynold's stress model.  The u'w' component decreases linearly with height to zero at z=config['RefHt']
        """

        self._rstrCoh[0]=0 # No u'v' stress.
        self._rstrCoh[1]=-(1-self.z[:,None,None]/self.config['RefHt'])/(self._std_u[0,:,:,None]*self._std_u[2,:,:,None])*(self._std_u[0,-1:,:,None]*self._std_u[2,-1:,:,None])
                                                                       
        self._rstrCoh[1][self.z>self.config['RefHt']]=0    # The u'w' component is zero above 'RefHt'

class river(tidal):
    # These fit positive velocity data in eastriver:
    s_coef=np.array([[1.057,3.432],[0.351,0.546],[0.265,0.341]])
    # These fit negative velocity data in eastriver:
    #s_coef=np.array([[0.784,2.085],[0.272,0.357],[0.240,0.290]])


