# !!!ADDDOC
try:
    from .. import base
    #from ..base import modelBase,np,ts_float,ts_complex
except ValueError:
    import base
    #from base import modelBase,np,ts_float,ts_complex
np=base.np

class spec(base.tsarray):

    @property
    def Suu(self,):
        return self[0]
    @property
    def Svv(self,):
        return self[0]
    @property
    def Sww(self,):
        return self[0]
    

class turbModelBase(base.modelBase):
    """
    A base class for TurbSim turbulence models.
    """
    pow5_3=5./3.
    pow2_3=2./3.

    def init(self,grid,profModel):
        if not hasattr(self,'profModel') or self.profModel is not profModel:
            self.profModel=profModel
        ## if not hasattr(self,'grid') or self.grid is not grid:
        ##     self.spec=base.tsarray(
        

    def __new__(cls,profModel,*args,**kwargs):
        self=super(turbModelBase,cls).__new__(cls,profModel,*args,**kwargs)
        self.profModel=profModel
        self.grid=profModel.grid
        self.rand=np.array(np.exp(1j*2*np.pi*self.grid.randgen.rand(self.n_comp,self.n_p,self.n_f)),dtype=base.ts_complex,order='F')
        self.Saa=np.empty((self.n_comp,self.n_z,self.n_y,self.n_f),dtype=base.ts_float)
        return self

    @property
    def Suu(self,):
        """
        The u-component spectral array (n_z x n_y x n_f).
        """
        return self.Saa[0]
    @property
    def Svv(self,):
        """
        The u-component spectral array (n_z x n_y x n_f).
        """
        return self.Saa[1]
    @property
    def Sww(self,):
        """
        The u-component spectral array (n_z x n_y x n_f).
        """
        return self.Saa[2]

    def set_cohereModel(self,cohModel):
        # !!!ADDDOC
        self.cohModel=cohModel

    def set_stressModel(self,stressModel):
        # !!!ADDDOC
        self.stressModel=stressModel

    @property
    def tke(self,):
        # !!!ADDDOC
        return np.trapz(self.Saa,x=self.f,axis=-1)
    
    @property
    def Saa_flat(self,):
        # !!!ADDDOC
        # 'flatten' the _autoSpec matrix for use in the cross-spectral calculations
        return self.grid.flatten(self.Saa)
        # Note: defining the _autoSpec matrix as order='F' will not make Saa_flat order='F' b/c of this flatten/reshape operation
        #       (which must be done in C-order).
        #       The order='F' operation is done when calling tslib (below).  This way, Saa_flat and Saa are the same data in memory
        #       (only duplicated in process of being passed to tslib).

class cohModelBase(base.modelBase):
    # !!!ADDDOC
    _crossSpec_pack_name=None
    _crossSpec_full_name=None

    def __new__(cls,turbModel,*args,**kwargs):
        self=super(cohModelBase,cls).__new__(cls,turbModel,*args,**kwargs)
        self.turbModel=turbModel
        self.profModel=turbModel.profModel
        self.grid=turbModel.profModel.grid
        self._work=np.empty(self.n_f,dtype=base.ts_float)
        self._crossSpec_pack=np.empty((self.n_p*(self.n_p+1)/2,self.n_f),dtype=base.ts_float,order='F') # This is a working array, used 1-component at a time.
        return self
    
    def get_crossSpec_full(self,comp):
        """
        Calculate the cross-spectral matrix, Sij for velocity component *comp* (0,1,2).
        
        This function sets and returns the variable self._crossSpec_full for the component *comp* (i.e. u,v,w).

        It first calls self.get_crossSpec_pack, then deals the data from the self._crossSpec_pack variable.
        """
        if self._crossSpec_full_name==comp:
            return self._crossSpec_full
        if not hasattr(self,'_crossSpec_full'): # This is not initialized in __new__ to save memory (it is not necessarily used).
            self._crossSpec_full=np.empty((self.n_p,self.n_p,self.n_f),dtype=base.ts_float)
        if self._crossSpec_pack_name!=comp:
            self._setCrossSpec_pack(comp)
        # Deal the data from the packed-form matrix to make the full matrix:
        for (ii,jj),indx in self._iter_flat_inds:
            self._crossSpec_full[ii,jj]=self._crossSpec_pack[indx]
            if ii!=jj: # The matrix is symmetric, so we are just mirroring the data. 
                self._crossSpec_full[jj,ii]=self._crossSpec_pack[indx]
        self._crossSpec_full_name=comp
        return self._crossSpec_full

    def get_crossSpec_pack(self,comp):
        # !!!ADDDOC
        if self._crossSpec_pack_name==comp:
            return self._crossSpec_pack
        for (ii,jj),indx in self._iter_flat_inds:
            if ii==jj:
                self._crossSpec_pack[indx]=self.Saa_flat[comp,ii]
            else:
                self._crossSpec_pack[indx]=self.calcCoh(comp,self.grid.ind2sub(ii),self.grid.ind2sub(jj))*np.sqrt(self.Saa_flat[comp,ii]*self.Saa_flat[comp,jj])
        self._crossSpec_pack_name=comp
        return self._crossSpec_pack

    @property
    def _iter_flat_inds(self,):
        indx=0
         # The _crossSpec_pack needs to be in column order for lapack's SPPTRF.
        for jj in range(self.n_p):
            for ii in range(jj,self.n_p):
                yield (ii,jj),indx
                indx+=1

    @property
    def iter_full(self,):
        """
        Iterate over the u,v,w components of the spectrum.

        Yields the full (lower triangular) cross-spectral matrix, shape: (np,np,nf).
        """
        for comp in self.comp:
            yield self.get_crossSpec_full(comp)
    
    def __iter__(self,):
        """
        Iterate over the u,v,w components of the spectrum.

        Yields the packed-form (lower triangular) cross-spectral matrix, shape: (np*(np+1)/2,nf).
        """
        for comp in self.comp:
            yield self.get_crossSpec_pack(comp)

    @property
    def Saa(self,):
        return self.turbModel.Saa
    @property
    def Saa_flat(self,):
        return self.turbModel.Saa_flat

class cohModelNonIEC(cohModelBase):
    # !!!ADDDOC
    """
    The coherence model for the non-IEC spectral models.
    """

    def __init__(self,turbModel,IncDec1=None,IncDec2=None,IncDec3=None,CohExp=0.0):
        # !!!ADDDOC
        """
        Initialize the coherence parameters for the non-IEC spectral model.
        """
        self._coh_coefs=np.empty((3,2),dtype=base.ts_float)
        if CohExp is None:
            self._CohExp=0.0
        else:
            self._CohExp=CohExp
        if IncDec1 is None:
            self._coh_coefs[0]=np.array([self.profModel.uhub,0])
        else:
            self._coh_coefs[0] = IncDec1
        if IncDec2 is None:
            self._coh_coefs[1] = 0.75*self._coh_coefs[0]
        else:
            self._coh_coefs[1]=IncDec2
        if IncDec3 is None:
            self._coh_coefs[2]=0.75*self._coh_coefs[0]
        else:
            self._coh_coefs[2]=IncDec3

    def get_crossSpec_pack(self,comp):
        # !!!ADDDOC
        """
        This function sets the variable self._crossSpec_pack for the component *comp* (i.e. 0,1,2=u,v,w).
        
        This function uses the TSlib.nonieccoh function to compute the cross-spectral matrix.
        If that library is not available, it computes the cross-spectral matrix in pure
        python using the calcCoh method.
        """
        if self._crossSpec_pack_name==comp:
            return self._crossSpec_pack
        if base.tslib is not None:
            self._crossSpec_pack=base.tslib.nonieccoh(np.array(self.Saa_flat[comp],order='F'),self.f,self.grid.y,self.grid.z,self.grid.flatten(self.profModel.u),self._coh_coefs[comp],self._CohExp,len(self.f),len(self.grid.y),len(self.grid.z))
            self._crossSpec_pack_name=comp
            return self._crossSpec_pack
        else:
            return cohModelBase.get_crossSpec_pack(self,comp)
        
    def calcCoh(self,comp,ii,jj):
        # !!!ADDDOC
        """
        The base function for calculating coherence for non-IEC spectral models.

        See the TurbSim documentation for further information.

        This function is only used if the TSlib fortran library is not available.
        """
        r=self.grid.dist(ii,jj)
        zm=(self.grid.z[ii[1]]+self.grid.z[jj[1]])/base.ts_float(2)
        um=(self.profModel.u[ii]+self.profModel.u[jj])/base.ts_float(2)
        self._work[:]=np.exp(-self._coh_coefs[comp][0]*(r/zm)**self._CohExp*np.sqrt((self.f*r/um)**base.ts_float(2)+(self._coh_coefs[comp][1])**base.ts_float(2)))
        return self._work
        
class cohModelIEC(cohModelBase):
    # !!!ADDDOC
    """
    The coherence model for the IEC spectral models.
    """
    def __init__(self,turbModel):
        # !!!ADDDOC
        """
        Initialize the coherence parameters for the IEC spectral model.
        """
        if turbModel.IECedition==2:
            self.a=8.8
            self.L=3.5*turbModel.Lambda
        else: # 3rd edition IEC standard:
            self.a=12.
            self.L=8.1*turbModel.Lambda

    def get_crossSpec_pack(self,comp):
        """
        This function sets the variable self._crossSpec_pack for the component *comp* (i.e. 0,1,2).
        
        This function uses the TSlib.ieccoh function to compute the cross-spectral matrix.
        If that library is not available, it computes the cross-spectral matrix in pure
        python using the calcCoh method.
        """
        if self._crossSpec_pack_name==comp:
            return self._crossSpec_pack
        if comp!=0:
            self._crossSpec_pack[:]=0 # Set all elements to zero.
            self._crossSpec_pack[np.cumsum(np.arange(self.n_p,0,-1)+1)-self.n_p-1]=self.Saa_flat[comp] # Set the diagonal elements to be the spectra:
            self._crossSpec_pack_name=comp
            return self._crossSpec_pack
        elif base.tslib is not None:
            self._crossSpec_pack=base.tslib.ieccoh(np.array(self.Saa_flat[comp],order='F'),self.f,self.grid.y,self.grid.z,self.profModel.uhub,self.a,self.L,len(self.f),len(self.grid.y),len(self.grid.z))
            self._crossSpec_pack_name=comp
            return self._crossSpec_pack
        else:
            return cohModelBase.get_crossSpec_pack(self,comp)

    def calcCoh(self,comp,ii,jj):
        """
        The *comp*=(0,1,2=u,v,w), coherence between points *ii*=(iz,iy) and *jj*=(jz,jy).
        """
        if comp==0:
            r=self.grid.dist(ii,jj)
            self._work[:]=np.exp(-self.a*np.sqrt((self.f*r/self.uhub)**2+(0.12*r/self.L)**2))
        else:
            self._work[:]=0
        return self._work
    

class stressModelBase(base.modelBase):

    def __new__(cls,turbModel,*args,**kwargs):
        # !!!ADDDOC
        """
        Initialize the 
        """
        self=super(stressModelBase,cls).__new__(cls,turbModel,*args,**kwargs)
        self.turbModel=turbModel
        self.profModel=turbModel.profModel
        self.grid=turbModel.profModel.grid
        self.stress=np.zeros_like(turbModel.profModel._u)
        self.rand=turbModel.rand
        self._dat_stress_max=np.empty_like(turbModel.profModel._u)
        return self

    @property
    def stress_max(self,):
        """
        Returns
        -------
        A 3 x n_z x n_y float array of maximum Reynolds stress values.

        Components:
        -----------
          0 - u'v'_max
          1 - u'w'_max
          2 - v'w'_max
        The product of the standard devations of the components (i.e. the
        maximum stress for the given turbulence model).
        """
        std_u=np.sqrt(self.turbModel.tke)
        self._dat_stress_max[0]=std_u[0]*std_u[1] # u'v'
        self._dat_stress_max[1]=std_u[0]*std_u[2] # u'w'
        self._dat_stress_max[2]=std_u[1]*std_u[2] # v'w'
        return self._dat_stress_max

    @property
    def upvp_max(self,):
        """
        The product of the standard devations of u' and v' (i.e. the maximum stress
        for the given turbulence model).
        """
        return self.stress_max[0]
    @property
    def upwp_max(self,):
        """
        The product of the standard devations of u' and w' (i.e. the maximum stress
        for the given turbulence model).
        """
        return self.stress_max[1]
    @property
    def vpwp_max(self,):
        """
        The product of the standard devations of v' and w' (i.e. the maximum stress
        for the given turbulence model).
        """
        return self.stress_max[2]

    @property
    def upvp_(self,):
        """
        The u'v' Reynolds stress for this model.
        """
        return self.stress[0]
    @upvp_.setter
    def upvp_(self,val):
        self.stress[0]=val

    @property
    def upwp_(self,):
        """
        The u'w' Reynolds stress for this model.
        """
        return self.stress[1]
    @upwp_.setter
    def upwp_(self,val):
        self.stress[1]=val

    @property
    def vpwp_(self,):
        """
        The v'w' Reynolds stress for this model.
        """
        return self.stress[2]
    @vpwp_.setter
    def vpwp_(self,val):
        self.stress[2]=val

    @property
    def corr(self,):
        return self.stress/self.stress_max

    @property
    def validity(self,):
        """
        Return a validity array for the stress magnitudes.

        Returns
        -------
        A 3 x n_z x n_y boolean array.  

        There are three criteria for each point in the grid.  They are listed here by their index in the array:
          0) The magnitude criteria: no stress can exceed the maximum stress (correlation between components cannot exceed 1).
          1) The 'overlap' criteria: The sum of the magnitude of the correlations can exceed one if they overlap. However, their
             are limits to the overlap. This criteria indicates that limit has been exceeded.
          2) The 'sign' criteria. If only one component is negative than they can not overlap. In this case the sum of magnitude
             of the correlations must be less than 1.

        If any of the criteria are false at any point, than the stressModel is invalid at that point.
        """
        srt=np.sort(np.abs(self.corr))
        valid=np.empty(srt.shape,dtype=bool)
        valid[0]=np.all(srt<1,0) # All individual stresses must be less than stress_max (i.e. the correlation between components can not be larger than the product of their standard devations).
        valid[1]=(1+srt[0]-srt[1]-srt[2]>0) # This is the 'overlap' criterion.
        valid[2]=((self.stress<0).sum(0)!=1) | (srt.sum(0)<=1) # This is the 'sign' criterion: if there is only one negative stress, their can be no overlap (sum(srt) must be <1).
        ############################
        # Now compute the 'overlap' (so that we don't have to redo or store the sort for _setPhases).
        # average the product of the smallest value with the two larger ones. Then take the minimum value of that with the smallest value. This is the 'overlap', i.e. the fraction of points that will have the same phase for all three components.
        # Note, this is specific choice of how the three components are correlated.
        self._overlap=np.minimum((srt[0]*srt[1]+srt[0]*srt[2])/2,srt[0])
        self._overlap[(self.stress<0).sum(0)==1]=0 # If there is only 1 negative stress than the overlap must be zero (if they are valid).
        return valid

    def check_validity(self,):
        """
        Check that the Reynold's stress magnitudes are valid.
        """
        # Currently, this raises an error if any of the points have invalid stresses.  In the future it may make sense to adjust/modify the stresses to make them valid?
        if ~(self.validity.all()):
            raise Exception('The input reynolds stresses are inconsistent.')

        
    def _setPhases(self,):
        """
        Here we control the Reynold's stress by setting the phases between components to be the same for fraction of the frequencies.
        """
        self.check_validity()
        #fudge_factor=0.93 #!!!FIXTHIS: The 0.93 is a fudge factor to account for ... ???
        fudge_factor=1
        rstrmat=self.grid.flatten(self.stress/self.stress_max)[...,None]
        rgen=self.grid.randgen.rand
        shp=(self.grid.n_p,self.grid.n_f)
        
        ####
        # First we set the 'overlap' stress. i.e. the phases that are the same (or opposite) for all three components.
        ovr=self.grid.flatten(self._overlap)[:,None] # This is computed during check_validity.
        inds_used=(rgen(*shp)*fudge_factor)<ovr
        self.rand[2][inds_used]=(np.sign(rstrmat[1])*self.rand[0])[inds_used]
        self.rand[1][inds_used]=(np.sign(rstrmat[0])*self.rand[0])[inds_used]
        ####
        # Now set the u'v' non-overlap piece.
        inds=((rgen(*shp)*fudge_factor)<np.abs(rstrmat[0])-ovr) & (~inds_used)
        self.rand[1][inds]=(np.sign(rstrmat[0])*self.rand[0])[inds]
        inds_used|=inds
        ####
        # Now set the u'w' non-overlap piece.
        inds=((rgen(*shp)*fudge_factor)<np.abs(rstrmat[1])-ovr) & (~inds_used)
        self.rand[2][inds]=(np.sign(rstrmat[1])*self.rand[0])[inds]
        inds_used|=inds
        ####
        # Now set the v'w' non-overlap piece.
        inds=((rgen(*shp)*fudge_factor)<np.abs(rstrmat[2])-ovr) & (~inds_used)
        self.rand[2][inds]=(np.sign(rstrmat[2])*self.rand[1])[inds]
        inds_used|=inds

class stressModelUniform(stressModelBase):
    # !!!ADDDOC

    def __init__(self,turbModel,upvp_=0.0,upwp_=0.0,vpwp_=0.0):
        """
        Set the Reynold's stresses to be uniform over the rotor disk.
        """
        self.upvp_[:]=upvp_
        self.upwp_[:]=upwp_
        self.vpwp_[:]=vpwp_
        
