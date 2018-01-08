"""
The main random phase models.
"""
from .base import phaseModelBase, phaseObj
import numpy as np


class Uniform(phaseModelBase):

    """The uniform random phase model

    This phase-model randomizes the phases uniformly between 0 and
    2*pi. It has no 'phase/temporal coherence' (correlation as a
    function of frequency).

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
        phases = phaseObj(tsrun)
        phases[:] = np.exp(1j * 2 * np.pi *
                           tsrun.randgen.rand(tsrun.grid.n_comp,
                                              tsrun.grid.n_p,
                                              tsrun.grid.n_f))
        return phases

    def _sumfile_string(self, tsrun, ):
        sumstring_format = """
        Profile model used                               =  {dat.model_desc}
        """
        return sumstring_format.format(dat=self,)
