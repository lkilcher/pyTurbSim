from .mBase import stressModelBase, np


class stressModelBase_f(stressModelBase):

    """
    A stress-model base-class that supports setting the stress by controlling the frequency-dependent coherence between velocity components.
    """

    def __new__(cls, turbModel, *args, **kwargs):
        self = super(stressModelBase_f, cls).__new__(
            cls, turbModel, *args, **kwargs)
        self._rstrCoh = np.zeros(
            [self.n_comp] + list(self.grid.shape) + [self.n_f], dtype=ts_float)

    # In the future I need to overwrite the _setPhases routine to allow for more control of the _rstrCoh array.  For example:
    #           It may be worthwhile to base the cross-coherence function _rstrCoh, on observed cross-component coherences (and phases). Perhaps this is a gaussion distribution (with some width) of phase shifts vs. frequency. For now we simply set a fraction of the phase shifts to be the same between the components to control the Reynold's stress.
    # For now, I have simply copied the code that was here before I simplified
    # the stressModelBase class.
    def _setPhases(self,):
        """
        Here we control the Reynold's stress by setting the 'random' phases between components to be the same for a fraction of the frequencies.

        """

        # fudge_factor=0.93 #!!!FIXTHIS: The 0.93 is a fudge factor to account
        # for ... ???
        fudge_factor = 1
        self._rstrCoh = self.stress[..., None] / self.stress_max[..., None]
        rstrmat = self.grid.flatten(
            self._rstrCoh)  # This doesn't currently work
        srt = np.sort(np.abs(rstrmat), axis=0)
        #rem=1+srt[0]-srt[1]-srt[2]
        if (1 + srt[0] - srt[1] - srt[2] < 0).any() or (((rstrmat < 0).sum(0) == 1) & (srt.sum(0) > 1)).any():
             # We can't have rem<0, or only one negative correlation if the
             # total correlation is greater than 1.
            raise Exception('The input reynolds stresses are inconsistent.')
        ovr = np.minimum((srt[0] * srt[1] + srt[0] * srt[2]) / 2, srt[0])
                         # average the product of the smallest value with the
                         # two larger ones. Then take the minimum value of that
                         # with the smallest value. This is the 'overlap', i.e.
                         # the fraction of points that will have the same phase
                         # for all three components.
        ovr[(rstrmat < 0).sum(0)
            == 1] = 0  # If there is only 1 negative stress than the overlap must be zero.
        rgen = self.grid.randgen.rand
        shp = (self.grid.n_p, self.grid.n_f)

        ####
        # First we set the 'overlap' stress. i.e. the phases that are the same
        # (or opposite) for all three components.
        inds_used = (rgen(*shp) * fudge_factor) < ovr
        self.rand[2][inds_used] = np.sign(
            rstrmat[1][inds_used]) * self.rand[0][inds_used]
        self.rand[1][inds_used] = np.sign(
            rstrmat[0][inds_used]) * self.rand[0][inds_used]
        ####
        # Now set the u'v' non-overlap piece.
        inds = ((rgen(*shp) * fudge_factor) <
                np.abs(rstrmat[0]) - ovr) & (~inds_used)
        self.rand[1][inds] = np.sign(rstrmat[0][inds]) * self.rand[0][inds]
        inds_used |= inds
        ####
        # Now set the u'w' non-overlap piece.
        inds = ((rgen(*shp) * fudge_factor) <
                np.abs(rstrmat[1]) - ovr) & (~inds_used)
        self.rand[2][inds] = np.sign(rstrmat[1][inds]) * self.rand[0][inds]
        inds_used |= inds
        ####
        # Now set the v'w' non-overlap piece.
        inds = ((rgen(*shp) * fudge_factor) <
                np.abs(rstrmat[2]) - ovr) & (~inds_used)
        self.rand[2][inds] = np.sign(rstrmat[2][inds]) * self.rand[1][inds]
        inds_used |= inds
