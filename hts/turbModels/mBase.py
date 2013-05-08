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

    def __init__(self,profModel):
        self.grid=profModel.grid
        self.profModel=profModel
        self.config=profModel.config
        outtime=self.config['UsableTime']+profModel.grid.width/profModel.uhub
        atime=max(outtime,self.config['AnalysisTime'])
        self.df=1./atime
        self.dt=self.config['TimeStep']
        self.n_tower=0 # !!!VERSION_INCONSISTENCY
        self.n_t=np.ceil(atime/self.dt) # !!!CHECKTHIS
        self.n_t_out=np.int(np.ceil(outtime/self.dt))
        self.i0_out=np.random.randint(self.n_t-self.n_t_out+1)
        self.n_f=self.n_t/2
        self.n_p=self.grid.n_p
        self.n_pcomb=self.n_p*(self.n_p+1)/2
        self.f=np.arange(self.n_f,dtype=ts_float)*self.df  # !!!CHECKTHIS
        self._crossSpec_pack_name=None
        self._crossSpec_full_name=None
        self._autoSpec=np.empty((self.n_comp,self.n_p,self.n_f),dtype=ts_float,order='F')
        self._crossSpec_pack=np.empty((self.n_p*(self.n_p+1)/2,self.n_f),dtype=ts_float,order='F') # This is a working array, used 1-component at a time.
        self._work=np.empty(self.n_f,dtype=ts_float)
        self.rand=np.array(np.exp(1j*2*np.pi*np.random.rand(self.n_comp,self.n_p,self.n_f)),dtype=np.complex64,order='F') # The '3' is for each component.  These can be modified to produce correlations between components!
        # These are used for both stable and unstable spectra:
        self.ustar2=self.config['UStar']**2
        self.initModel()
        if hasattr(self,'initCohere'):
            self.initCohere()
        self.calcAutoSpec()

    def setCrossSpec_full(self,comp):
        """
        This function sets the variable self._crossSpec_full for the component *comp* (i.e. u,v,w).

        It first calls self.setCrossSpec_pack, then deals the data from that routine.
        """
        if self._crossSpec_full_name==comp:
            return
        if not hasattr(self,'_crossSpec_full'):
            self._crossSpec_full=np.empty((self.n_p,self.n_p,self.n_f),dtype=ts_float,order='F')
        self.setCrossSpec_pack(comp)
        indx=0
        # Deal the data from the packed-form matrix to make the full matrix:
        for jj in range(self.n_p):
            for ii in range(jj,self.n_p):
                if ii==jj:
                    self._crossSpec_full[ii,jj]=self._crossSpec_pack[indx]
                else:
                    self._crossSpec_full[ii,jj]=self._crossSpec_pack[indx]
                    self._crossSpec_full[jj,ii]=self._crossSpec_pack[indx]
                indx+=1
        self._crossSpec_full_name=comp
        
    def setCrossSpec_pack(self,comp):
        """
        This function sets the variable self._crossSpec_pack for the component *comp* (i.e. 0,1,2).
        
        This (default) function uses the coherence method (calcCoh) and auto-spectra data
        (_autoSpec) to compute the packed-form cross-spectral matrix.

        Override this function to provide alternate methods for computing the packed-form cross-spectral matrix.
        """
        if self._crossSpec_pack_name==comp:
            return
        indx=0
        for jj in range(self.n_p): # The _crossSpec_pack needs to be in column order for lapack's SPPTRF.
            for ii in range(jj,self.n_p):
                if ii==jj:
                    self._crossSpec_pack[indx]=self._autoSpec[comp][ii]
                else:
                    self._crossSpec_pack[indx]=self.calcCoh(comp,self.grid.ind2sub(ii),self.grid.ind2sub(jj))*np.sqrt(self._autoSpec[comp][ii]*self._autoSpec[comp][jj])
                indx+=1
        self._crossSpec_pack_name=comp

    @property
    def uhub(self,):
        return self.profModel.uhub

    @property
    def iter_full(self,):
        """
        Iterate over the u,v,w components of the spectrum.

        Yields the full (lower triangular) cross-spectral matrix, shape: (np,np,nf).
        """
        for comp in self.comp:
            self.setCrossSpec_full(comp)
            yield self._crossSpec_full
    
    def __iter__(self,):
        """
        Iterate over the u,v,w components of the spectrum.

        Yields the packed-form (lower triangular) cross-spectral matrix, shape: (np*(np+1)/2,nf).
        """
        for comp in self.comp:
            self.setCrossSpec_pack(comp)
            yield self._crossSpec_pack
    @property
    def Suu(self,):
        return np.reshape(self._autoSpec,[3]+list(self.grid.shape)+[-1])

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
        self._coh_coefs[0]=self.config['IncDec1'] or [self.profModel.uhub,0]
        self._coh_coefs[1]=self.config['IncDec2'] or 0.75*self._coh_coefs[0]
        self._coh_coefs[2]=self.config['IncDec3'] or 0.75*self._coh_coefs[0]

    def setCrossSpec_pack(self,comp):
        """
        This function sets the variable self._crossSpec_pack for the component *comp* (i.e. u,v,w).
        
        This function uses the TSlib.nonieccoh function to compute the cross-spectral matrix.
        If that library is not available, it computes the cross-spectral matrix in pure
        python using the calcCoh method.
        """
        if self._crossSpec_pack_name==comp:
            return
        if tslib is not None:
            self._crossSpec_pack=tslib.nonieccoh(self._autoSpec[comp],self.f,self.grid.y,self.grid.z,self.profModel.u.flatten(),self._coh_coefs[comp],self._CohExp,len(self.f),len(self.grid.y),len(self.grid.z))
        else:
            turbModelBase.setCrossSpec_pack(self,comp)
        
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

    def setCrossSpec_pack(self,comp):
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
            self._crossSpec_pack[np.cumsum(np.arange(self.n_p,0,-1)+1)-self.n_p-1]=self._autoSpec[comp] # Set the diagonal elements to be the spectra:
        elif tslib is not None:
            self._crossSpec_pack=tslib.ieccoh(self._autoSpec[comp],self.f,self.grid.y,self.grid.z,self.profModel.uhub,self.a,self.L,len(self.f),len(self.grid.y),len(self.grid.z))
        else:
            turbModelBase.setCrossSpec_pack(self,comp)

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
    
