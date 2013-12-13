"""
This module contains the following spectral models:
  smooth - The 'smooth' spectral model.
  nwtcup - The NWTC 'upwind' model.
"""
from .mBase import turbModelBase,np,base,cohModelNonIEC,stressModelUniform
from ..nwtc_funcs import zL as zL_func
from ..misc import fix2range


def cfg_nwtcup(tsconfig,profModel):
    tmodel=nwtcup(profModel,tsconfig['UStar'],tsconfig['RICH_NO'],tsconfig['ZI'])
    tmodel.set_cohereModel(cohModelNonIEC(tmodel,tsconfig['IncDec1'],tsconfig['IncDec2'],tsconfig['IncDec3'],tsconfig['CohExp']))
    tmodel.set_stressModel(stressModelUniform(tmodel,upvp_=tsconfig['PC_UV'],upwp_=tsconfig['PC_UW'],vpwp_=tsconfig['PC_VW']))
    return tmodel

def cfg_smooth(tsconfig,profModel):
    tmodel=smooth(profModel,tsconfig['UStar'],tsconfig['RICH_NO'],tsconfig['ZI'])
    tmodel.set_cohereModel(cohModelNonIEC(tmodel,tsconfig['IncDec1'],tsconfig['IncDec2'],tsconfig['IncDec3'],tsconfig['CohExp']))
    tmodel.set_stressModel(stressModelUniform(tmodel,upvp_=tsconfig['PC_UV'],upwp_=tsconfig['PC_UW'],vpwp_=tsconfig['PC_VW']))
    return tmodel


class NWTCgenModel(turbModelBase):
    """
    Base class for the nwtc models.
    """
    
    s_coef=np.array([[79.,263.],[13.,32.],[3.5,8.6]])

    @property
    def zL(self,):
        return zL_func(self.Ri,self.turbmodel)

    @property
    def phie(self):
        return (1.+2.5*self.zL**0.6)**1.5
    @property
    def phim(self):
        return 1.+4.7*self.zL

    @property
    def L(self,):
        return self.grid.zhub/self.zL

    @property
    def numer(self,):
        if not hasattr(self,'_val_numer'):
            self._val_numer=(self.phie/self.phim)**self.pow2_3/self.phim*self.Ustar2
        return self._val_numer
    @property
    def denom(self,):
        if not hasattr(self,'_val_denom'):
            self._val_denom=(self.f/self.phim)
        return self._val_denom

    @property
    def stable(self,):
        return self.zL>0
    
    def _stableModel(self,z,u,comp,coef=np.array([1.,1.])):
        # !!!ADDDOC
        z_u=z/u
        if coef.ndim>1:
            self._work[:]=0
            for c in coef:
                self._work+=self._stableModel(z,u,comp,c)
            return self._work
        return coef[0]*self.s_coef[comp,0]*self.numer*z_u/(1.+self.s_coef[comp,1]*(coef[1]*z_u*self.denom)**self.pow5_3)

    def _unstableModel(self,z,u,comp,coef=np.array([[1.,1.],[1.,1.]])):
        # !!!ADDDOC
        pow5_3=self.pow5_3
        z_ZI=z/self.ZI
        num0=self.Ustar2*self.ZI/u*(self.ZI/-self.L)**self.pow2_3
        fZI_u=self.f*self.ZI/u
        num1=self.Ustar2*z_u*(1-z_ZI)**2
        fz_u=self.f*z_u
        if comp==0:
            tmp0=1+15*z_ZI
            self._work=0.5*coef[0,0]*num0/(1+2.2*(fZI_u*coef[0,1])**pow5_3) + coef[1,0]*105*num1/(tmp0+coef[1,1]*33*fz_u)**pow5_3
        elif comp==1:
            tmp0=1+2.8*z_ZI
            self._work=0.95*coef[0,0]*num0/(1+2*coef[0,1]*fZI_u)**pow5_3 + coef[1,0]*17*num1/(tmp0+coef[1,1]*9.5*fz_u)**pow5_3
            # Handle extra (e.g. wake, for outf_turb) coefficients:
            if coef.shape[0]>2 and not np.isnan(coef[2,0]+coef[2,1]):
                self._work+=coef[2,0]*17*num1/(tmp0+coef[2,1]*9.5*fz_u)**pow5_3
        else:
            self._work=0.95*coef[0,0]*num0/(1+2*coef[0,1]*fZI_u)**pow5_3*np.sqrt((fz_u**2+(0.3*z_ZI)**2)/(fz_u**2+0.0225)) + coef[1,0]*2*num1/(1+coef[1,1]*5.3*fz_u**pow5_3)
        return self._work

    def calcModel(self,):
        for iz in range(self.n_z):
            for iy in range(self.n_y):
                z=self.grid.z[iz]
                u=self.profModel.u[iz,iy]
                for comp in self.comp:
                    if self.stable:
                        self.Saa[comp,iz,iy]=self._stableModel(z,u,comp,self.coefs[comp])
                    else:
                        self.Saa[comp,iz,iy]=self._unstableModel(z,u,comp,self.coefs[comp])
    
    def __init__(self,profModel,Ustar,Ri,ZI):
        """
        Important note: you cannot modify values of this model before
        calling the routine. All work is done at time of initilization.
        """
        # !!!ADDDOC
        self.Ustar=Ustar
        self.Ustar2=self.Ustar**2
        self.Ri=Ri
        self.ZI=ZI
        self._work=np.empty(self.n_f,dtype=base.ts_float)
        self.initCoefs()
        self.calcModel()

class smooth(NWTCgenModel):
    # !!!ADDDOC
    turbmodel='smooth'

    def initCoefs(self,):
        # The coefficients are all 1 for the simple 'smooth' model.
        if self.stable:
            self.coefs=np.ones((3,2),dtype=base.ts_float)
        else:
            self.coefs=np.ones((3,2,2),dtype=base.ts_float)
        
class nwtcup(NWTCgenModel):
    # !!!ADDDOC
    turbmodel='nwtcup'
    _coefs={'stable':{},'unstable':{}}
    # These coefficients are copied from TSsubs.f90.
    # They were calculated by Neil Kelley based on data from the NWTC.
    _coefs['stable']['terms']={'fr_il':np.array([[0.0964,-0.316,0,-0.386,0],
                                                 [0.0323,-0.388,0,-0.389,0],
                                                 [0.0972,-0.0964,0,-0.616,0],],dtype=base.ts_float),
                               'fr_ih':np.array([[1.69,-.340,0,-.133,0],
                                                 [0.473,-0.441,0,0.291,0],
                                                 [0.470,-0.218,0,-0.158,0],],dtype=base.ts_float),
                               'Pr_il':np.array([[1.21,0.0523,0,0.189,0],
                                                 [1.29,0.00664,0,0.354,0],
                                                 [0.368,0.0938,0,0.109,0],],dtype=base.ts_float),
                               'Pr_ih':np.array([[0.224,0.170,0,0.223,0],
                                                 [0.991,0.344,0,-0.605,0],
                                                 [0.639,0.0354,0,-0.0319,0],],dtype=base.ts_float)
                               }
    _coefs['stable']['min']={'fr_il':(0.015,0.003,0.006),
                             'fr_ih':(0.35,0.25,0.2),
                             'Pr_il':(0.8,0.95,0.2),
                             'Pr_ih':(0.05,0.2,0.25),
                             }
    _coefs['stable']['max']={'fr_il':(0.4,0.23,0.175),
                             'fr_ih':(10.,3.,1.25),
                             'Pr_il':(2.25,2.25,0.75),
                             'Pr_ih':(0.8,1.0,1.0),
                             }
    _coefs['unstable']['terms']={
        'fr_il':np.array([
            [  0.08825035, -0.08806865, -0.26295052,  1.74135233, 1.86785832 ],
            [  0.58374913, -0.53220033,  1.49509302,  3.61867635, -0.98540722 ],
            [  0.81092087, -0.03483105,  0.58332966, -0.10731274, -0.16463702 ],],dtype=base.ts_float),
        'fr_ih':np.array([
            [  1.34307411, -0.55126969, -0.07034031,  0.40185202, -0.55083463 ],
            [  4.30596626,  0.31302745, -0.26457011, -1.41513284, 0.91503248 ],
            [  1.05515450, -0.25002535,  0.14528047,  1.00641958, -0.67569359 ],],dtype=base.ts_float),
        'Pr_il':np.array([
            [ 57.51578485, -1.89080610,  4.03260796,  6.09158000, -7.47414385 ],
            [ 32.06436225, -1.43676866,  3.57797045,  5.31617813, -5.76800891 ],
            [  6.60003543, -0.45005503,  1.35937877,  2.45632937, -1.98267575 ],],dtype=base.ts_float),
        'Pr_ih':np.array([
            [  4.52702491,  0.72447070, -0.10602646, -3.73265876, -0.49429015 ],
            [  3.93109762,  0.57974534, -0.20510478, -4.85367443, -0.61610914 ],
            [ 16.56290180,  0.40464339,  0.82276250, -3.92300971, -1.82957067 ],],dtype=base.ts_float),
        }
    _coefs['unstable']['min']={'fr_il':(0.2,0.12,0.2),
                               'fr_ih':(0.1,1.8,.95),
                               'Pr_il':(1.0,0.2,1.0),
                               'Pr_ih':(0.1,0.2,0.3),
                               }
    _coefs['unstable']['max']={'fr_il':(1.5,2.3,1.4),
                               'fr_ih':(8.0,7.5,1.75),
                               'Pr_il':(8.,8.,7.),
                               'Pr_ih':(1.2,0.9,1.0),
                               }

    def initCoefs(self,):
        if self.stable:
            self._loc_zL=fix2range(self.zL,0.005,3.5)
            self.ustar_tmp=0.
        else:
            self._loc_zL=np.abs(fix2range(self.zL,-0.5,-0.025))
            self.ustar_tmp=fix2range(self.UStar,0.2,1.4)
        out=np.empty((3,2,2),dtype=base.ts_float)
        if self.stable:
            dat=self._coefs['stable']
        else:
            dat=self._coefs['unstable']
        for i0,sfx in enumerate(['il','ih']):
            for i1,pfx in enumerate(['Pr','fr']):
                nm=pfx+'_'+sfx
                arr=dat['terms'][nm]
                out[:,i0,i1]=fix2range(arr[:,0]*(self._loc_zL**arr[:,1])*self.ustar_tmp**arr[:,2]*np.exp(arr[:,3]*self._loc_zL+arr[:,4]*self.ustar_tmp),dat['min'][nm],dat['max'][nm])
        out[:,:,1]**=-1 # Invert the second (fr) coefficient.
        out[:,:,0]*=out[:,:,1] # All of the first coefficients are the product of the first and the second (inverse included).
        self.coefs=out
