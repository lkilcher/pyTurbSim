"""
The main random phase models.
"""
from .mBase import phaseModelBase, np, ts_complex


class randPhase(phaseModelBase):

    """
    This phase-model randomizes the phases uniformly and without any
    'phase coherence' (correlation as a function of frequency).

    Because it is so simple, it has no initialization parameters.

    """

    def __call__(self, tsrun):
        """
        Create and calculate the phases for the `tsrun` instance.

        Parameters
        ----------
        tsrun :         :class:`tsrun <pyts.main.tsrun>`
                        A TurbSim run object.

        Returns
        -------
        out :           array_like(3,n_p,n_f)
                        An array of random phases.

        """
        phases = np.empty((tsrun.grid.n_comp, tsrun.grid.n_p, tsrun.grid.n_f),
                          dtype=ts_complex, order='F')
        phases[:] = np.exp(1j * 2 * np.pi *
                           tsrun.randgen.rand(tsrun.grid.n_comp,
                                              tsrun.grid.n_p,
                                              tsrun.grid.n_f))
        return phases
