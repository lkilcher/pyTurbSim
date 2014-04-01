"""

"""
from mBase import phaseModelBase,np,ts_complex

class randPhase(phaseModelBase):

    def __call__(self,tsrun):
        phases=np.empty((tsrun.grid.n_comp,tsrun.grid.n_p,tsrun.grid.n_f),dtype=ts_complex,order='F')
        phases[:]=(np.exp(1j*2*np.pi*tsrun.randgen.rand(tsrun.grid.n_comp,tsrun.grid.n_p,tsrun.grid.n_f)))
        return phases

