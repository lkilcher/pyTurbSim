"""
This module contains the power-law mean-velocity profiles:
 main   - The IEC mean wind speed profile.

"""
from .base import profObj
from .log import nwtc as logmain
from .power import nwtc as powmain
from numpy import tile, where

# !!!VERSION_INCONSISTENCY
# This model needs to account for the EWM50 and EWM1 turbulence models.


class main(powmain, logmain, ):

    """IEC wind profile model.

    This profile is a power-law across the rotor disk and logarithmic
    elsewhere.

    Parameters
    ----------
    grid :      :class:`tsGrid <pyts.base.tsGrid>`
                The TurbSim grid object for this simulation.

    URef :      float
                Reference velocity for the wind profile [m/s].

    RefHt :     float
                Reference height of the reference velocity [m].

    PLexp :     float,optional (0.2)
                The power-law exponent to be utilized for this
                simulation [non-dimensional], default=0.2 (per
                IEC specification).

    Z0 :        float
                Surface roughness length [m].

    Ri :        float
                The Richardon number [non-dimensional].

    turbmodel : str
                the name of the turbulence model in this simulationm, optional.

    See Also
    --------
    .power.nwtc : The iec model is this law over the rotor disk
    .log.nwtc   : The iec model is this law outside the rotor disk

    """

    def __init__(self, URef, RefHt, Z0, PLexp=0.2, turbmodel=None):
        self.Uref = URef
        self.Zref = RefHt
        self.PLexp = PLexp
        self.Z0 = Z0
        self.Ri = 0.0
        self.TurbModel = turbmodel

    def _sumfile_string(self, tsrun, ):
        sumstring_format = """
        Profile model used                               =  {dat.model_desc}
        Reference velocity (URef)                        =  {dat.Uref:0.4g} [m/s]
        Reference height (RefHt)                         =  {dat.Zref:0.4g} [m]
        Power-low exponent (PLexp)                       =  {dat.PLexp:0.4g}
        Surface roughness length (Z0)                    =  {dat.Z0:0.4g} [m]
        Turbulence Model                                 =  {dat.TurbModel}
        """
        return sumstring_format.format(dat=self)

    def __call__(self, tsrun):
        """
        Create and calculate the mean-profile object for a `tsrun`
        instance.

        Parameters
        ----------
        tsrun :         :class:`.tsrun`
                        A TurbSim run object.

        Returns
        -------
        out :           :class:`.profObj`
                        A iec wind-speed profile for the grid in `tsrun`.

        """
        out = profObj(tsrun)
        g = tsrun.grid  # A temporary, internal shortcut.
        zinds = (((-g.rotor_diam / 2 <= g.z - g.zhub)
                 & (g.z - g.zhub <= g.rotor_diam / 2))[:, None])
        yinds = ((-g.rotor_diam / 2 <= g.y)
                 & (g.y <= g.rotor_diam / 2))[None, :]
        out.array[0] = where(zinds & yinds,
                             tile(powmain.model(self, g.z)[:, None], len(yinds[0])),
                             tile(logmain.model(self, g.z)[:, None], len(yinds[0])), )
        return out
