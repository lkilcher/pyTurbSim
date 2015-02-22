"""
This module contains the log-law mean-velocity profiles:
 linear   - A linear wind speed profile
 uniform  - A uniform mean wind speed.

"""
from .mBase import profModelBase, np, profObj


class uniform(profModelBase,):

    r"""Uniform wind-speed 'profile' model.

    Parameters
    ----------
    URef :    The mean velocity you wish to produce.

    Notes
    -----

    This wind-speed 'profile' actually just sets the mean u-component
    wind-speed to be spatially uniform. The v- and w-components are
    zero.

    """

    def __init__(self, URef):
        self.Uref = URef

    def _sumfile_string(self, tsrun, ):
        sumstring_format = """
        Profile model used                               =  {dat.model_desc}
        Reference velocity (URef)                        =  {dat.Uref:0.2f} [m/s]
        """
        return sumstring_format.format(dat=self, )

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
                        A uniform wind-speed profile for the grid in `tsrun`.

        """
        out = profObj(tsrun)
        out[0][:] = self.Uref  # Set the velocity.
        return out


class linear(profModelBase,):

    r"""
    A 'linear' mean wind-speed 'profile'.

    Parameters
    ----------
    URef  :  float
        The mean velocity you wish to produce [m/s].
    ZRef  :  float
        Reference height of URef [m].
    URef2 :  float (default = 0)
        Second velocity point [m/s].
    ZRef2 :  float (default = 0)
        Reference height of second velocity point [m]

    Notes
    -----

    The u-component is set to a linear profile through the points
    (URef,Zref) and (URef2,ZRef2). v- and w-components are zero.

    """

    def __init__(self, URef, ZRef, URef2=0.0, ZRef2=0.0):
        self.Uref = URef
        self.Zref = ZRef
        self.Uref2 = URef2
        self.Zref2 = ZRef2

    def _sumfile_string(self, tsrun, ):
        sumstring_format = """
        Profile model used                               =  {dat.model_desc}
        Reference velocity (URef)                        =  {dat.Uref:0.2f} [m/s]
        Reference height (ZRef)                          =  {dat.Zref:0.2f} [m]
        Reference velocity 2 (URef)                      =  {dat.Uref2:0.2f} [m/s]
        Reference height 2 (ZRef)                        =  {dat.Zref2:0.2f} [m]
        """
        return sumstring_format.format(dat=self,)

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
                        A uniform wind-speed profile for the grid in `tsrun`.

        """
        out = profObj(tsrun)
        out[0][:] = out.grid.z * \
            (self.Uref - self.Uref2) / (self.Zref - self.Zref2)
        return out
