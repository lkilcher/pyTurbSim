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
        Phase model used                                 =  {dat.model_desc}
        """
        return sumstring_format.format(dat=self,)


class Rinker(phaseModelBase):
    """The temporal-coherence phase model

    This is based on the work of Jenni Rinker:
    http://dx.doi.org/10.1007/s10546-015-0121-x
    """

    def __init__(self, rho, mu=np.pi):
        self.rho = rho
        self.mu = mu

    def __call__(self, tsrun):
        phases = phaseObj(tsrun)

        # phases.array[:] = ...
        # This is where we need to define phases.array (equivalently,
        # phases[:]). Note that it is a n_comp=3, by n_p
        # (number of z,y points) by n_f (num frequencies) array.

        # Then return it...
        return phases

    def _sumfile_string(self, tsrun, ):
        sumstring_format = """
        Phase model used                                 =  {dat.model_desc}
        rho                                              =  {dat.rho:0.4g}
        mu                                               =  {dat.mu:0.4g}
        """
        return sumstring_format.format(dat=self,)
