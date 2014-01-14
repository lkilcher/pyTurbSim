# !!!ADDDOC
from mBase import profModelBase,np,prof
from ..misc import kappa,psiM

class nwtc(profModelBase,):
    """
    The logarithmic mean wind profile.
    """
    def __init__(self,URef,RefHt,Z0,Ri,turbmodel=None):
        """
        Create a logarathmic wind profile according to the NWTC standard.

        Parameters
        ----------
        grid     - The TurbSim grid object for this simulation.
        URef     - Reference velocity for the wind profile [m/s].
        RefHt    - Reference height of the reference velocity [m].
        Z0       - Surface roughness length [m].
        Ri       - The Richardon number [*non-dimensional].
        turbmodel- the name of the turbulence model in this simulationm, *optional*.

        Returns
        -------
        out      - A logarithmic wind profile object that matches the
                   specified input parameters.
        """
        self.Uref=URef
        self.Zref=RefHt
        self.Z0=Z0
        self.Ri=Ri
        self.TurbModel=turbmodel

    def __call__(self,tsrun):
        out=prof(tsrun)
        out[0]=self.model(out.grid.z)[:,None]
        return out
    
    def model(self,z):
        """
        The function that calculates the log profile.
        """
        # Note: this function is separated from the __init__ routine so that it can be utilized by other modules
        return (self.Uref*(np.log(z/self.Z0)+self.psiM)/(np.log(self.Zref/self.Z0)+self.psiM))
    
    @property
    def psiM(self,):
        return psiM(self.Ri,self.TurbModel)
        
class H2O(profModelBase,):
    """
    The logarithmic mean water profile.
    """
    def __init__(self,Uref,Zref,ustar):
        # !!!ADDDOC
        self.Uref=Uref
        self.Zref=Zref
        self.Ustar=ustar

    def __call__(self,tsrun):
        # # !!!FIXTHIS: this is not right for a log-layer.  Zref should be Z0 (or something), like above.
        out=prof(tsrun)
        out[0]=(self.Ustar/kappa*np.log(out.grid.z/self.Zref)+self.Uref)[:,None]
        return out

def cfg_nwtc(tsconfig):
    # !!!ADDDOC
    return nwtc(tsconfig['URef'],tsconfig['RefHt'],tsconfig['Z0'],tsconfig['RICH_NO'],tsconfig['TurbModel'])

def cfg_H2O(tsconfig):
    # !!!ADDDOC
    return H2O(tsconfig['URef'],tsconfig['RefHt'],tsconfig['UStar'])
