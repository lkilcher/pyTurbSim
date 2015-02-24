"""
This is the stress package's base module.

produce estimates of Reynold's
stress

"""

from .. import base
np = base.np


class stressModelBase(base.modelBase):
    pass


class stressObj(base.calcObj, base.gridProps):

    def __init__(self, tsrun):
        self.grid = tsrun.grid
        self.randgen = tsrun.randgen
        self.array = np.zeros(
            [3] + self.grid.shape, dtype=base.ts_float, order='F')
        self.spec = tsrun.spec
        std_u = np.sqrt(self.spec.tke)
        self.stress_max = np.empty_like(self.array)
        self.stress_max[0] = std_u[0] * std_u[1]  # u'v'
        self.stress_max[1] = std_u[0] * std_u[2]  # u'w'
        self.stress_max[2] = std_u[1] * std_u[2]  # v'w'

    @property
    def upvp_max(self,):
        """
        The product of the standard deviations of u' and v' (i.e. the
        maximum stress for the given turbulence model).
        """
        return self.stress_max[0]

    @property
    def upwp_max(self,):
        """
        The product of the standard deviations of u' and w' (i.e. the
        maximum stress for the given turbulence model).
        """
        return self.stress_max[1]

    @property
    def vpwp_max(self,):
        """
        The product of the standard deviations of v' and w' (i.e. the
        maximum stress for the given turbulence model).
        """
        return self.stress_max[2]

    @property
    def upvp_(self,):
        """
        The u'v' Reynolds stress for this model.
        """
        return self.array[0]

    @upvp_.setter
    def upvp_(self, val):
        self.array[0] = val

    @property
    def upwp_(self,):
        """
        The u'w' Reynolds stress for this model.
        """
        return self.array[1]

    @upwp_.setter
    def upwp_(self, val):
        self.array[1] = val

    @property
    def vpwp_(self,):
        """
        The v'w' Reynolds stress for this model.
        """
        return self.array[2]

    @vpwp_.setter
    def vpwp_(self, val):
        self.array[2] = val

    @property
    def corr(self,):
        return self.array / self.stress_max

    @property
    def validity(self,):
        """
        Return a validity array for the stress magnitudes.

        Returns
        -------
        A 3 x n_z x n_y boolean array.

        There are three criteria for each point in the grid.  They are
        listed here by their index in the array:

          0) The magnitude criteria: no stress can exceed the maximum
             stress (correlation between components cannot exceed 1).
          1) The 'overlap' criteria: The sum of the magnitude of the
             correlations can exceed one if they overlap. However,
             their are limits to the overlap. This criteria indicates
             that limit has been exceeded.
          2) The 'sign' criteria. If only one component is negative
             than they can not overlap. In this case the sum of
             magnitude of the correlations must be less than 1.

        If any of the criteria are false at any point, than the
        stressModel is invalid at that point.
        """
        srt = np.sort(np.abs(self.corr))
        valid = np.empty(srt.shape, dtype=bool)

        # All individual stresses must be less than stress_max
        # (i.e. the correlation between components can not be
        # larger than the product of their standard devations).
        valid[0] = (srt < 1).all(0)

        # This is the 'overlap' criterion.
        valid[1] = (1 + srt[0] - srt[1] - srt[2] > 0)

        # This is the 'sign' criterion: if there is only one negative
        # stress, their can be no overlap (sum(srt) must be <1).
        valid[2] = ((self.array < 0).sum(0) != 1) | (srt.sum(0) <= 1)
        ############################
        # Now compute the 'overlap' (so that we don't have to redo or
        # store the sort for calc_phases).  average the product of the
        # smallest value with the two larger ones. Then take the
        # minimum value of that with the smallest value. This is the
        # 'overlap', i.e. the fraction of points that will have the
        # same phase for all three components.
        #
        # Note, this is specific choice of how the three components are
        # correlated.
        self._overlap = np.minimum((srt[0] * srt[1] + srt[0] * srt[2]) / 2, srt[0])
        # If there is only 1 negative stress than the overlap must be zero (if they are valid):
        self._overlap[(self.array < 0).sum(0) == 1] = 0
        #pdb.set_trace()
        return valid

    def check_validity(self,):
        """
        Check that the Reynold's stress magnitudes are valid.
        """
        # Currently, this raises an error if any of the points have invalid
        # stresses.  In the future it may make sense to adjust/modify the
        # stresses to make them valid?
        if ~(self.validity.all()):
            print self.validity.shape
            print self.validity
            raise Exception('The input reynolds stresses are inconsistent.')

    def calc_phases(self, phases):
        """
        Here we control the Reynold's stress by setting the phases
        between components to be the same for a fraction of the
        frequencies.
        """
        self.check_validity()
        rgen = self.randgen.rand
        if (self.array == 0).all():
            return phases  # No stress, so the phases are independently-random.
        # fudge_factor=0.93 #!!!FIXTHIS: The 0.93 is a fudge factor to account
        # for ... ???
        fudge_factor = 1
        rstrmat = self.grid.flatten(self.corr)[..., None]
        shp = (self.grid.n_p, self.grid.n_f)

        ####
        # First we set the 'overlap' stress. i.e. the phases that are the same
        # (or opposite) for all three components.
        # This is computed during check_validity:
        ovr = self.grid.flatten(self._overlap)[:, None]
        inds_used = (rgen(*shp) * fudge_factor) < ovr
        phases[2][inds_used] = (np.sign(rstrmat[1]) * phases[0])[inds_used]
        phases[1][inds_used] = (np.sign(rstrmat[0]) * phases[0])[inds_used]
        ####
        # Now set the u'v' non-overlap piece.
        inds = ((rgen(*shp) * fudge_factor) <
                np.abs(rstrmat[0]) - ovr) & (~inds_used)
        phases[1][inds] = (np.sign(rstrmat[0]) * phases[0])[inds]
        inds_used |= inds
        ####
        # Now set the u'w' non-overlap piece.
        inds = ((rgen(*shp) * fudge_factor) <
                np.abs(rstrmat[1]) - ovr) & (~inds_used)
        phases[2][inds] = (np.sign(rstrmat[1]) * phases[0])[inds]
        inds_used |= inds
        ####
        # Now set the v'w' non-overlap piece.
        inds = ((rgen(*shp) * fudge_factor) <
                np.abs(rstrmat[2]) - ovr) & (~inds_used)
        phases[2][inds] = (np.sign(rstrmat[2]) * phases[1])[inds]
        inds_used |= inds
        return phases
