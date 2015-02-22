from .mBase import stressModelBase, stressObj


class tidal(stressModelBase):

    """
    The 'tidal' model Reynold's stress model.

    Parameters
    ----------
    Ustar : float
            The friction velocity at the bottom boundary (aka :math:`U_*`).
    Zref : float
           The height of the 'no-stress' level in the water-column.

    Notes
    -----

    The v'w' and u'v' components are zero. The u'w' component is:

    .. math::
        \overline{u'w'} = -U_*^2 (1-z/Z_{\mathrm{ref}})

    for 0<z<Zref, and 0 elsewhere.

    """

    def __init__(self, Ustar, Zref):
        self.Zref = Zref
        self.Ustar = Ustar

    def _sumfile_string(self, tsrun, ):
        sumstring_format = """
        Stress model used                                =  {dat.model_desc}
        Friction velocity (UStar)                        =  {dat.Ustar:0.4g} [m/s]
        Reference height (ZRef)                          =  {dat.Zref:0.4g} [m]
        """
        return sumstring_format.format(dat=self, )

    def __call__(self, tsrun):
        """
        Create and calculate the stress object for a `tsrun`
        instance.

        Parameters
        ----------
        tsrun :         :class:`tsrun <pyts.main.tsrun>`
                        A TurbSim run object.

        Returns
        -------
        out :           :class:`stressObj <.mBase.specObj>`
                        A stress object for the grid in `tsrun`.

        """
        out = stressObj(tsrun)
        out.upwp_[out.z < self.Zref] = -self.Ustar ** 2 * \
            (1 - out.z[out.z < self.Zref][:, None] / self.Zref)
             #*out.upwp_max[-1:]
        # The other components default to zero.
        return out
