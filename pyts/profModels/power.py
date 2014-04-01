"""
This module contains the power-law mean-velocity profiles:
 nwtc   - The NWTC power-law mean wind speed profile.

"""
from mBase import profModelBase,profObj

class nwtc(profModelBase):
    """
    The power-law mean wind profile.

           Ubar(z) = URef * ( z / RefHt )^PLexp
    
    """
    def __init__(self,Uref,RefHt,PLexp=1./7.):
        """
        Create a power-law wind profile.

        Parameters
        ----------
        URef     - Reference velocity for the wind profile [m/s].
        RefHt    - Reference height of the reference velocity [m].
        PLexp    - The power-law exponent to be utilized for this
                   simulation [*non-dimensional], default=1/7.

        Returns
        -------
        out      - A power-law wind profile object that matches the
                   specified input parameters.
        """
        self.Uref=Uref
        self.Zref=RefHt
        self.PLexp=PLexp

    def model(self,z):
        """
        The function for calculating the mean velocity profile.
        """
        # Note: this function is separated from the __init__ routine so that it can be utilized by other modules
        return self.Uref*(z/self.Zref)**self.PLexp

    def __call__(self,tsrun):
        """
        Calculate the profile object for this profile model.
        
        Parameters
        ----------
        tsrun    - A TurbSim run object.

        Returns
        -------
        out      - A TurbSim profile object, containing the array of mean
                   velocity for the simulation.
        """
        out=profObj(tsrun)
        out[0]=self.model(out.grid.z)[:,None]
        return out
