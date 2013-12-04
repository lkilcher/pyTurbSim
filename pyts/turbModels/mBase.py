try:
    from ..base import *
except ValueError:
    from base import *

class turbModelBase(modelBase):
    """
    A base class for TurbSim turbulence models.
    """
    pow5_3=5./3.
    pow2_3=2./3.

    def __getattr__(self,name):
        if hasattr(self.grid,name):
            return getattr(self.grid,name)
        elif hasattr(self.profModel,name):
            return getattr(self.profModel,name)
        else:
            raise AttributeError

    def __init__(self,profModel):
        self.grid=profModel.grid
        self.profModel=profModel
        self.config=profModel.config
        self._crossSpec_pack_name=None
        self._crossSpec_full_name=None
        self._autoSpec=np.empty((self.n_comp,self.n_z,self.n_y,self.n_f),dtype=ts_float)
        self._crossSpec_pack=np.empty((self.n_p*(self.n_p+1)/2,self.n_f),dtype=ts_float,order='F') # This is a working array, used 1-component at a time.
        self._rstrCoh=np.empty([self.n_comp-1]+list(self.grid.shape)+[self.n_f],dtype=ts_float) # This is the cross-coherence between velocity components (defines the Reynold's stress), it can be between 1 and -1.
        self._work=np.empty(self.n_f,dtype=ts_float)
        self.rand=np.array(np.exp(1j*2*np.pi*np.random.rand(self.n_comp,self.n_p,self.n_f)),dtype=np.complex64,order='F') # These are modified by self.calcStress to produce correlations (Reynold's stresses) between components!
        # These are used for both stable and unstable spectra:
        self.ustar2=self.config['UStar']**2
        self.initModel()
        self._autoSpec_flat=self.grid.flatten(self._autoSpec) # 'flatten' the _autoSpec matrix for use in the cross-spectral calculations
        # Note: defining the _autoSpec matrix as order='F' will not make _autoSpec_flat order='F' b/c of this flatten/reshape operation
        #       (which must be done in C-order).
        #       The order='F' operation is done when calling tslib (below).  This way, _autoSpec_flat and _autoSpec are the same data in memory
        #       (only duplicated in process of being passed to tslib).
        if hasattr(self,'initCohere'):
            self.initCohere()
        self._std_u=np.sqrt(np.trapz(self._autoSpec,x=self.f,axis=-1))
        self.initStress()
        self.calcStress()
        
    def _setCrossSpec_full(self,comp):
        """
        This function sets the variable self._crossSpec_full for the component *comp* (i.e. u,v,w).

        It first calls self._setCrossSpec_pack, then deals the data from that routine.
        """
        if self._crossSpec_full_name==comp:
            return
        if not hasattr(self,'_crossSpec_full'):
            self._crossSpec_full=np.empty((self.n_p,self.n_p,self.n_f),dtype=ts_float)
        self._setCrossSpec_pack(comp)
        # Deal the data from the packed-form matrix to make the full matrix:
        for (ii,jj),indx in self._iter_flat_inds:
            self._crossSpec_full[ii,jj]=self._crossSpec_pack[indx]
            if ii!=jj: # The matrix is symmetric, so we are just mirroring the data. 
                self._crossSpec_full[jj,ii]=self._crossSpec_pack[indx]
        self._crossSpec_full_name=comp

    def initStress(self,):
        """
        Initialize the stress matrix.  This defines the cross-coherence between components of velocity.
        """
        # In the future I may want to make these functions of the 
        if self.config['PC_UW'] is None:
            self._rstrCoh[1]=-0.3 # Setting the correlation for the u'w' component.
        else:
            val=self.config['PC_UW']/(self._std_u[0]*self._std_u[2]) # Definition of correlation.
            if (val>1.).any():
                print "Warning: Scaled Reynolds stress u'w' exceeds 1 (highest value is %0.2f)...\n Reducing it to 1." % (np.max(val),)
                val[val>1]=1.
            self._rstrCoh[1]=val[:,:,None]
        if self.config['PC_UV'] is None:
            self._rstrCoh[0]=1e-7 # This is the u'v' component.  This sets it to zero.
        else:
            val=self.config['PC_UV']/(self._std_u[0]*self._std_u[1])
            if (val>1.).any():
                print "Warning: Scaled Reynolds stress u'v' exceeds 1 (highest value is %0.2f)...\n Reducing it to 1." % (np.max(val),)
                val[val>1]=1.
            self._rstrCoh[0]=val[:,:,None]

    def calcStress(self,):
        """
        Here we control the Reynold's stress by setting the 'random' phases between components to be the same for a fraction of the frequencies.

        """
        # In the future it may be worthwhile to base the cross-coherence function _rstrCoh, on observed cross-component coherences (and phases).
        # Perhaps this is a gaussion distribution (with some width) of phase shifts vs. frequency.
        rstrmat=self.grid.flatten(self._rstrCoh[0])
        rnd=np.random.rand(self.n_p,self.n_f)*0.93 #!!!FIXTHIS: The 0.93 is a fudge factor to account for the likelihood that the other phases will be opposed to the ones specified (I think).  Need to do figure out how to specify this better.
        inds=rnd<rstrmat
        self.rand[1][inds]=self.rand[0][inds]
        inds=rnd<-rstrmat
        self.rand[1][inds]=-self.rand[0][inds]
        rstrmat=self.grid.flatten(self._rstrCoh[1])
        rnd=np.random.rand(self.n_p,self.n_f)*0.93 #!!!FIXTHIS: The 0.93 is a fudge factor to account for the likelihood that the other phases will be opposed to the ones specified (I think).  Need to do figure out how to specify this better.
        inds=rnd<rstrmat
        self.rand[2][inds]=self.rand[0][inds]
        inds=rnd<-rstrmat
        self.rand[2][inds]=-self.rand[0][inds]
        
    def _setCrossSpec_pack(self,comp):
        """
        This function sets the variable self._crossSpec_pack for the component *comp* (i.e. 0,1,2).
        
        This (default) function uses the coherence method (calcCoh) and auto-spectra data
        (_autoSpec) to compute the packed-form cross-spectral matrix.

        Override this function to provide alternate methods for computing the packed-form cross-spectral matrix.
        """
        if self._crossSpec_pack_name==comp:
            return
        for (ii,jj),indx in self._iter_flat_inds:
            if ii==jj:
                self._crossSpec_pack[indx]=self._autoSpec_flat[comp,ii]
            else:
                self._crossSpec_pack[indx]=self.calcCoh(comp,self.grid.ind2sub(ii),self.grid.ind2sub(jj))*np.sqrt(self._autoSpec_flat[comp,ii]*self._autoSpec_flat[comp,jj])
        self._crossSpec_pack_name=comp

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
            self._setCrossSpec_full(comp)
            yield self._crossSpec_full
    
    def __iter__(self,):
        """
        Iterate over the u,v,w components of the spectrum.

        Yields the packed-form (lower triangular) cross-spectral matrix, shape: (np*(np+1)/2,nf).
        """
        for comp in self.comp:
            self._setCrossSpec_pack(comp)
            yield self._crossSpec_pack
    @property
    def Suu(self,):
        return self._autoSpec

class turbModelCohNonIEC(turbModelBase):
    """
    The coherence model for the non-IEC spectral models.
    """

    def initCohere(self,):
        """
        Initialize the coherence parameters for the non-IEC spectral model.

        This function is called by __init__.
        """
        self._coh_coefs=np.empty((3,2),dtype=ts_float)
        self._CohExp=self.config['CohExp'] or 0.0
        if self.config['IncDec1'] is None:
            self._coh_coefs[0]=np.array([self.profModel.uhub,0])
        else:
            self._coh_coefs[0] = self.config['IncDec1']

        if self.config['IncDec2'] is None:
            self._coh_coefs[1] = 0.75*self._coh_coefs[0]
        else:
            self._coh_coefs[1]=self.config['IncDec2']

        if self.config['IncDec3'] is None:
            self._coh_coefs[1]=0.75*self._coh_coefs[0]
        else:
            self._coh_coefs[1]=self.config['IncDec3']

    def _setCrossSpec_pack(self,comp):
        """
        This function sets the variable self._crossSpec_pack for the component *comp* (i.e. u,v,w).
        
        This function uses the TSlib.nonieccoh function to compute the cross-spectral matrix.
        If that library is not available, it computes the cross-spectral matrix in pure
        python using the calcCoh method.
        """
        if self._crossSpec_pack_name==comp:
            return
        if tslib is not None:
            self._crossSpec_pack=tslib.nonieccoh(np.array(self._autoSpec_flat[comp],order='F'),self.f,self.grid.y,self.grid.z,self.profModel.u.flatten(),self._coh_coefs[comp],self._CohExp,len(self.f),len(self.grid.y),len(self.grid.z))
        else:
            turbModelBase._setCrossSpec_pack(self,comp)
        
    def calcCoh(self,comp,ii,jj):
        """
        The base function for calculating coherence for non-IEC spectral models.

        See the TurbSim documentation for further information.

        This function is only used if the TSlib fortran library is not available.
        """
        r=self.grid.dist(ii,jj)
        zm=(self.grid.z[ii[1]]+self.grid.z[jj[1]])/ts_float(2)
        um=(self.profModel.u[ii]+self.profModel.u[jj])/ts_float(2)
        self._work[:]=np.exp(-self._coh_coefs[comp][0]*(r/zm)**self._CohExp*np.sqrt((self.f*r/um)**ts_float(2)+(self._coh_coefs[comp][1])**ts_float(2)))
        return self._work
        
class turbModelCohIEC(turbModelBase):
    """
    The coherence model for the IEC spectral models.
    """
    def initCohere(self,):
        """
        Initialize the coherence parameters for the IEC spectral model.

        This function is called by __init__.
        """
        tmp=0.7*self.config['HubHt']
        if self.config['IECstandard'] is not None and self.config['IECedition']==2:
            self.a=8.8
            #self.L=2.45*np.min([30,self.config['HubHt']]) # This is in the documentation.
            if self.config['HubHt']>30: tmp=21. # These two lines are in the code.
            self.L=3.5*tmp
        else: # 3rd edition IEC standard:
            self.a=12.
            #self.L=5.67*np.min([60,self.config['HubHt']]) # This is in the documentation.
            if self.config['HubHt']>60: tmp=42.
            self.L=8.1*tmp

    def _setCrossSpec_pack(self,comp):
        """
        This function sets the variable self._crossSpec_pack for the component *comp* (i.e. 0,1,2).
        
        This function uses the TSlib.nonieccoh function to compute the cross-spectral matrix.
        If that library is not available, it computes the cross-spectral matrix in pure
        python using the calcCoh method.
        """
        if self._crossSpec_pack_name==comp:
            return
        if comp!=0:
            self._crossSpec_pack[:]=0 # Set all elements to zero.
            self._crossSpec_pack[np.cumsum(np.arange(self.n_p,0,-1)+1)-self.n_p-1]=self._autoSpec_flat[comp] # Set the diagonal elements to be the spectra:
        elif tslib is not None:
            self._crossSpec_pack=tslib.ieccoh(np.array(self._autoSpec_flat[comp],order='F'),self.f,self.grid.y,self.grid.z,self.profModel.uhub,self.a,self.L,len(self.f),len(self.grid.y),len(self.grid.z))
        else:
            turbModelBase._setCrossSpec_pack(self,comp)

    def calcCoh(self,comp,ii,jj):
        """
        The *comp*=('u', 'v' or 'w'), coherence between points *ii*=(iz,iy) and *jj*=(jz,jy).
        """
        if comp==0:
            r=self.grid.dist(ii,jj)
            self._work[:]=np.exp(-self.a*np.sqrt((self.f*r/self.uhub)**2+(0.12*r/self.L)**2))
        else:
            self._work[:]=0
        return self._work
    
