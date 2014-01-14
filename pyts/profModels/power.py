# !!!ADDDOC
from mBase import profModelBase,prof

class nwtc(profModelBase):
    # !!!ADDDOC
    """
    The power-law mean wind profile.
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
        Calculate the profile array for this current profile model.
        
        Parameters
        ----------
        tsrun     - The 'TurbSim run' object for this simulation.

        Returns
        -------
        prof     - A TurbSim profile object, containing the array of mean
                   velocity for the simulation.
        """
        out=prof(tsrun)
        out[0]=self.model(out.grid.z)[:,None]
        return out
