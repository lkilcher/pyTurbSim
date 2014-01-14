from mBase import stressModelBase,stress

class uniform(stressModelBase):
    # !!!ADDDOC

    def __init__(self,upvp_=0.0,upwp_=0.0,vpwp_=0.0):
        """
        Set the Reynold's stresses to be uniform over the rotor disk.
        """
        self.vals=[upvp_,upwp_,vpwp_]

    def __call__(self,tsrun):
        out=stress(tsrun)
        out.upvp_[:]=self.vals[0]
        out.upwp_[:]=self.vals[1]
        out.vpwp_[:]=self.vals[2]
        return out
