"""
This module contains the power-law mean-velocity profiles:
 nwtc   - The NWTC logarithmic mean wind speed profile.
 H2O    - The hydro-logarithmic mean velocity profile.

"""
from mBase import profModelBase,np,profObj
from ..misc import kappa,psiM

class nwtc(profModelBase,):
    """
    The NWTC logarithmic mean wind-speed profile.
        
                               ln( z / Z0 ) - psi_M
           Ubar(z) = URef *  ------------------------
                              ln( ZRef / Z0) - psi_M

                              
    Where psi_M is a function of the Ri, the Richardson number (psi_M=0 for Ri=0),
    and the turbulence model.

    """
    def __init__(self,URef,ZRef,Z0,Ri=0,turbmodel=None):
        """
        Create a NWTC logarithmic mean wind-speed profile model instance.
        
        Parameters
        ----------
        URef     - Reference velocity for the wind profile [m/s].
        ZRef     - Reference height of the reference velocity [m].
        Z0       - Surface roughness length [m].
        Ri       - The Richardon number [*non-dimensional].
        turbmodel- the name of the turbulence model in this simulationm, *optional*.

        """
        self.Uref=URef
        self.Zref=ZRef
        self.Z0=Z0
        self.Ri=Ri
        self.TurbModel=turbmodel

    def __call__(self,tsrun):
        """
        Call the mean wind speed profile with a *tsrun* object to return the
        run-specific mean velocity profile object.

        Parameters
        ----------
        tsrun    - A TurbSim run object.
        
        Returns
        -------
        out      - A logarithmic wind-speed profile for the grid in tsrun.
        """
        out=profObj(tsrun)
        out[0]=self.model(out.grid.z)[:,None]
        return out
    
    def model(self,z):
        """
        Calculate the log profile for input variable *z*.

        Parameters
        ----------
        z       - Height above the ground (nz x ny array).

        Returns
        -------
        mean velocity (nz x ny array).
        """
        # Note: this function is separated from the __init__ routine so that it can be utilized by other modules
        return (self.Uref*(np.log(z/self.Z0)+self.psiM)/(np.log(self.Zref/self.Z0)+self.psiM))
    
    @property
    def psiM(self,):
        """
        The psi_M parameter for this profile model.

        See the pyts.misc.psiM function for details.
        """
        return psiM(self.Ri,self.TurbModel)
        
class H2O(profModelBase,):
    """
    The logarithmic mean water velocity profile.

           Ubar(z) = Ustar/kappa * ln( z / Zref) + Uref
           
    """
    def __init__(self,Uref,Zref,ustar):
        """
        Create a hydro-logarathmic mean velocity profile model instance.
        
        Parameters
        ----------
        URef     - Reference velocity for the wind profile [m/s].
        ZRef     - Reference height of the reference velocity [m].
        ustar    - Surface friction veclocity [m/s].
        
        """
        self.Uref=Uref
        self.Zref=Zref
        self.Ustar=ustar

    def __call__(self,tsrun):
        """
        Call the mean wind speed profile with a *tsrun* object to return the
        run-specific mean velocity profile object.

        Parameters
        ----------
        tsrun    - A TurbSim run object.

        Returns
        -------
        out - A logarithmic mean-velocity profile object for the
              spatial grid in tsrun.
        """
        out=profObj(tsrun)
        out[0]=(self.Ustar/kappa*np.log(out.grid.z/self.Zref)+self.Uref)[:,None]
        return out
