from mBase import *

class main(profModelBase,):
    """
    The logarithmic mean wind profile.
    """
    def initModel(self,):
        self._u[0]=self.model(self.grid.z)[:,None]

    def model(self,z):
        return (self.URef*(np.log(z/self.Z0)+self.psiM)/(np.log(self.RefHt/self.Z0)+self.psiM))
        
class H2O(profModelBase,):
    """
    The 'water' logarithmic mean velocity profile.
    """
    def initModel(self,):
        self._u[0]=(self.UStar/kappa*np.log(self.grid.z/self.RefHt)+self.URef)[:,None]

