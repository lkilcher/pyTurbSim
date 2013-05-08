from .mBase import *

class main(turbModelCohNonIEC):
    """
    The von-Karmon spectral model.

    This can be used to specify spectra based on von Karmon length and standard deviations.

    This model is not currently documented in the Manual.
    
    """
    pow5_6=5./6.
    pow11_6=11./6.

    def initModel(self,):
        self.L_in=self.config['UserProf_L']
        self.z_in=self.config['UserProf_H']
        self.sigma_in=self.config['UserProf_Std']
        self.stdscale=self.config['StdScale']
        
    def calcAutoSpec(self,):
        sigma=self.ustar2**1.075
        for ii in range(self.n_p):
            z=self.grid.z[ii[0]]
            u=self.profModel.u[ii]
            if self.L is not None:
                lvk=np.interp(z,self.z_in,self.L_in)
            else:
                if z<150:
                    lvk=0.7*z*3.5
                else:
                    lvk=105*3.5
            if self.sigma_in is not None:
                sigma=np.interp(z,self.z_in,self.sigma_in)
            l1_u=lvk/u
            sigmal1_u=2*sigma**2*l1_u
            flu2=(self.f*l1_u)**2
            tmp=1+71*flu2
            self._autoSpec[0][ii]=2*sigmal1_u/tmp**self.pow5_6
            self._autoSpec[1][ii]=sigmal1_u*(1.0+189.0*flu2)/tmp**self.pow11_6
            self._autoSpec[2][ii]=self._autoSpec[1][ii]
        self._autoSpec*=self.stdscale[:,None,None]**2
        
                
