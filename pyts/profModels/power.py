"""
The NWTC power-law profile model.
"""
from .mBase import profModelBase, profObj


class nwtc(profModelBase):

    r"""
    The power-law mean wind profile model.

    .. math::

           \bar{U}(z) = U_{ref} * ( z / Z_{ref} )^{PLexp}

    Parameters
    ----------
    URef :      float
                Reference velocity for the wind profile [m/s].
    Zref  :     float
                Reference height of the reference velocity [m].
    PLexp :     float
                The power-law exponent to be utilized for this
                simulation [non-dimensional], default=1/7.

    """

    def __init__(self, Uref, Zref, PLexp=1. / 7.):
        self.Uref = Uref
        self.Zref = Zref
        self.PLexp = PLexp

    def model(self, z):
        """
        The function for calculating the mean velocity profile.
        """
        # Note: this function is separated from the __init__ routine so that it
        # can be utilized by other modules
        return self.Uref * (z / self.Zref) ** self.PLexp

    def __call__(self, tsrun):
        """
        Create and calculate the mean-profile object for a `tsrun`
        instance.

        Parameters
        ----------
        tsrun :         :class:`tsrun <pyts.main.tsrun>`
                        A TurbSim run object.

        Returns
        -------
        out :           :class:`profObj <.mBase.profObj>`
                        A power-law wind-speed profile for the grid in `tsrun`.

        """
        out = profObj(tsrun)
        out[0] = self.model(out.grid.z)[:, None]
        return out
