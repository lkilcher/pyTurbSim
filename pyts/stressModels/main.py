from .mBase import stressModelBase, stressObj


class uniform(stressModelBase):

    """
    The 'uniform' Reynold's stress model. In this model each component
    of the Reynold's stress can be specified explicitly, but the
    values are uniform in space.

    Parameters
    ----------
    upvp_ : float
            The u'v' component of Reynold's stress.
    upwp_ : float
            The u'w' component of Reynold's stress.
    vpwp_ : float
            The v'w' component of Reynold's stress.

    """

    def __init__(self, upvp_=0.0, upwp_=0.0, vpwp_=0.0):
        """
        Set the Reynold's stresses to be uniform over the rotor disk.
        """
        self.vals = [upvp_, upwp_, vpwp_]

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
        out.upvp_[:] = self.vals[0]
        out.upwp_[:] = self.vals[1]
        out.vpwp_[:] = self.vals[2]
        return out
