# !!!ADDDOC
from mBase import profModelBase

def cfg_nwtc(tsconfig,grid):
    # !!!ADDDOC
    return nwtc(grid,tsconfig['URef'],tsconfig['RefHt'],tsconfig['PLExp'])

class nwtc(profModelBase):
    # !!!ADDDOC
    """
    The power-law mean wind profile.
    """
    def __init__(self,grid,Uref,RefHt,PLexp=1./7.):
        """
        Create a power-law wind profile.

        Parameters
        ----------
        grid     - The TurbSim grid object for this simulation.
        URef     - Reference velocity for the wind profile [m/s].
        RefHt    - Reference height of the reference velocity [m].
        PLexp    - The power-law exponent to be utilized for this
                   simulation [*non-dimensional], default=1/7.

        Returns
        -------
        out      - A power-law wind profile object that matches the
                   specified input parameters.
        """
        self.grid=grid # Every profile model must begin by adding the grid.
        self.Uref=Uref
        self.Zref=RefHt
        self.PLexp=PLexp
        self._u[0]=self.model(Uref,RefHt,PLexp,self.grid.z)[:,None]

    def model(self,uref,zref,plexp,z):
        """
        The function for calculating the mean velocity profile.
        """
        # Note: this function is separated from the __init__ routine so that it can be utilized by other modules
        return uref*(z/zref)**plexp
