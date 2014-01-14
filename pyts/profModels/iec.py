from mBase import profModelBase
from log import nwtc as logmain
from power import nwtc as powmain

class main(logmain,powmain):
    """
    The iec wind profile.
    """
    def __init__(self,URef,RefHt,Z0,Ri,PLexp=0.2,turbmodel=None):
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
        self.Uref=URef
        self.Zref=RefHt
        self.PLexp=PLexp
        self.Z0=Z0
        self.Ri=Ri
        self.TurbModel=turbmodel

    def __call__(self,tsrun):
        out=prof(tsrun)
        grid=tsrun.grid # A temporary, internal shortcut.
        out[0]=logmain.nwtc.model(self,grid.z)[:,None]
        zinds=-grid.rotor_diam/2<=grid.z-grid.zhub & grid.z-grid.zhub<=grid.rotor_diam/2
        out[0][zinds][:,(-grid.rotor_diam/2<=grid.y & grid.y<=grid.rotor_diam/2)]=powmain.nwtc.model(self,grid.z[zinds])
        return out

