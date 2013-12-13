# !!!ADDDOC
from .mBase import turbModelBase,stressModelBase,np,cohModelNonIEC

class tidal(turbModelBase):
    # !!!ADDDOC
    s_coef=np.array([[1.21,4.3],[0.33,0.50],[0.23,0.26]])

    def __init__(self,profModel,Ustar,RefHt=None):
        self.Ustar=Ustar
        if RefHt is None and not hasattr(self.profModel,'Zref'):
            raise Exception("Required variable 'RefHt' not specified as input in the profile or turbulence model.")
        else:
            self.Zref=RefHt

#    def __call__(self,grid,profModel):
        
        dudz=np.abs(self.profModel.dudz[None,:,:,None])
        self.sigma2=self.Ustar**2*np.array([4.5,2.25,0.9])[:,None]*np.exp(-2*self.z[None,:]/self.Zref)
        self.Saa[:]=(self.sigma2[:,:,None,None]*self.s_coef[:,0][:,None,None,None]/dudz)/(1+self.s_coef[:,1][:,None,None,None]*(self.f[None,None,None,:]/dudz)**self.pow5_3)

class stressModelTidal(stressModelBase):
    # !!!ADDDOC
    def __init__(self,turbModel,RefHt=None):
        # !!!ADDDOC
        """
        The tidal model Reynold's stress model.  The u'w' component decreases linearly with z to zero at z=config['RefHt']
        """
        if RefHt is None:
            RefHt=self.Zref
        self.upwp_=-(1-self.z[:,None]/RefHt)*self.upwp_max[-1:][None,:]
        self.upwp_[self.z>RefHt]=0
        # The other components default to zero.

class river(tidal):
    # !!!ADDDOC
    # These fit positive velocity data in eastriver:
    s_coef=np.array([[1.057,3.432],[0.351,0.546],[0.265,0.341]])
    # These fit negative velocity data in eastriver:
    #s_coef=np.array([[0.784,2.085],[0.272,0.357],[0.240,0.290]])

def cfg_tidal(tsconfig,profModel):
    # !!!ADDDOC
    tmodel=tidal(profModel,tsconfig['UStar'],tsconfig['RefHt'])
    tmodel.set_cohereModel(cohModelNonIEC(tmodel,tsconfig['IncDec1'],tsconfig['IncDec2'],tsconfig['IncDec3'],tsconfig['CohExp']))
    tmodel.set_stressModel(stressModelTidal(tmodel,tsconfig['RefHt']))
    return tmodel

def cfg_river(tsconfig,profModel):
    # !!!ADDDOC
    tmodel=river(profModel,tsconfig['UStar'],tsconfig['RefHt'])
    tmodel.set_cohereModel(cohModelNonIEC(tmodel,tsconfig['IncDec1'],tsconfig['IncDec2'],tsconfig['IncDec3'],tsconfig['CohExp']))
    tmodel.set_stressModel(stressModelTidal(tmodel,tsconfig['RefHt']))
    return tmodel

