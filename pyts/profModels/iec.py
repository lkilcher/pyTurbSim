from mBase import profModelBase
from log import main as logmain
from power import main as powmain

class main(profModelBase,logmain,powmain):
    """
    The iec wind profile.
    """
    def __init__(self,grid,URef,RefHt,Z0,Ri,PLexp=0.2,turbmodel=None):
        """
        Create an 'IEC' mean velocity profile, where the velocity is a power-law
        across the rotor disk and logarithmic elsewhere.
        Was this specified in an old IEC standard? Is it still valid?

        Parameters
        ----------
        grid     - The TurbSim grid object for this simulation.
        URef     - Reference velocity for the wind profile [m/s].
        RefHt    - Reference height of the reference velocity [m].
        PLexp    - The power-law exponent to be utilized for this
                   simulation [*non-dimensional], default=0.2 (per
                   IEC specification).
        Z0       - Surface roughness length [m].
        Ri       - The Richardon number [*non-dimensional].
        turbmodel- the name of the turbulence model in this simulationm, *optional*.

        Returns
        -------
        out      - An 'IEC' wind profile object that matches the
                   specified input parameters.
        """
        self.grid=grid # Every profile model must begin by adding the grid.
        self.Uref=URef
        self.Zref=RefHt
        self.PLexp=PLexp
        self.Z0=Z0
        self.Ri=Ri
        self.TurbModel=turbmodel
        self._u[0]=logmain.nwtc.model(self,self.z)[:,None]
        zinds=-self.rotor_diam/2<=self.z-self.zhub & self.z-self.zhub<=self.rotor_diam/2
        self._u[0][zinds][:,(-self.rotor_diam/2<=self.y & self.y<=self.rotor_diam/2)]=powmain.nwtc.model(self,self.z[zinds])

    
def cfg_iec(tsconfig,grid):
    return main(grid,tsconfig['URef'],tsconfig['RefHt'],tsconfig['Z0'],tsconfig['RICH_NO'],tsconfig['PLExp'],tsconfig['TurbModel'],
