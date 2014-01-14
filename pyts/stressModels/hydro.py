from mBase import stressModelBase,stress

class tidal(stressModelBase):
    # !!!ADDDOC
    def __init__(self,RefHt):
        # !!!ADDDOC
        """
        The tidal model Reynold's stress model.  The u'w' component decreases linearly with z to zero at z=config['RefHt']
        """
        self.Zref=RefHt

    def __call__(self,tsrun):
        out=stress(tsrun)
        out.upwp_[out.z<self.Zref]=-(1-out.z[out.z<self.Zref][:,None]/self.Zref)*out.upwp_max[-1:]
        # The other components default to zero.
        return out

