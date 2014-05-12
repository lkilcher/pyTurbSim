"""
This is the base module for coherence models.

"""
from ..base import gridProps,modelBase,np,ts_float,ts_complex,tslib,dbg,calcObj

class cohereObj(gridProps,calcObj):
    """
    Some text.
    """

    @property
    def array(self,):
        """
        This property computes and returns the full coherence array.
        
        This array utilizes significant memory (3 x np x np x nf) and
        should be avoided unless needed.  By default PyTurbSim
        avoids holding the entire array in memory and instead computes
        small pieces of it as needed.
        """
        if not hasattr(self,'_array'):
            self._array=np.empty((self.n_comp,self.n_p,self.n_p,self.n_f),dtype=ts_complex,order='F')
            for icomp in range(3):
                for ff in range(self.n_f):
                    for ii,jj in self._iter_inds():
                        self._array[icomp,ii,jj]=self._array[icomp,jj,ii]=self.calcCoh(self.grid.f,icomp,ii,jj)
        return self._array
    @array.setter
    def array(self,val):
        self._array=val
    @array.deleter
    def array(self,):
        del self._array

    def __init__(self,tsrun):
        self.grid=tsrun.grid
        self.prof=tsrun.prof
        self.spec=tsrun.spec
        self.stress=tsrun.stress
        self.ncore=tsrun.ncore # This is used by tslib.

    def _iter_inds(self,):
        """
        An iterator for the lower-triangular indices (ii and jj) of
        the coherence matrix.
        """
        for jj in range(self.n_p):
            for ii in range(jj,self.n_p):
                yield ii,jj

    def calc_phases(self,phases):
        """
        Compute and set the full cross-spectral matrix for component
        *comp* for 'coherence calculator' instance *cohi*.

        This method should not be called explicitly.  It is called by
        a 'coherence calculator' instance's __call__ method.

        This routine utilizes a model's 'calcCoh' method, which must
        be defined explicitly for all sub-classes of cohereModelBase.

        See also
        --------
        calcCoh - computes the coherence for individual grid-point pairs.

        """
        out=np.zeros((self.n_comp,self.n_p,self.n_f),dtype=ts_complex,order='F')
        tmp=np.empty((self.n_p,self.n_p),dtype=ts_float,order='F')
        for icomp in range(3):
            for ff in np.range(self.n_f):
                for ii,jj in self._iter_inds():
                    if ii==jj:
                        tmp[ii,ii]=1
                    else:
                        tmp[ii,jj]=tmp[jj,ii]=self.calcCoh(self.grid.f[ff],icomp,ii,jj)
                tmp[:]=np.linalg.cholesky(tmp)
                for ii in range(self.n_p):
                    out[icomp,ii,ff]=sum(tmp.flatten('F')*phases[icomp,:,ff])
        return out
    
    def calcCoh(self,f,comp,ii,jj):
        """
        THIS IS A PLACEHOLDER METHOD WHICH SHOULD BE OVER-WRITTEN FOR ALL SUB-CLASSES
        OF cohereModelBase. THIS METHOD ONLY RAISES AN ERROR.
        
        A functioning version of this method (i.e. in a subclass of cohereModelBase)
        should return the a length-n_f vector that is the coherence between point
        *ii*=(iz,iy) and *jj*=(jz,jy) for velocity component *comp*.

        Parameters
        ----------
        *cohi*    - A 'coherence calculator' instance (for the given tsrun).
        *comp*    - an integer (0,1,2) indicating the velocity component for which to
                    compute the coherence.
        *ii*,*jj* - Two-integer elements indicating the grid-points between which to
                    calculate the coherence. For example: ii=(1,3),jj=(2,3)
        
        See also
        --------
        calc - iterates over grid-point pairs and calls calcCoh to compute the full
               cross-spectral matrix.
        
        """
        raise Exception('Subclasses of cohereObj must overwrite the calcCoh method or redfine the calc_phases method.')

class cohereUser(cohereObj):
    """
    Specify the coherence explicitly as an array.

    The array must have the dimensions 3 x np x np x nf, where np
    is the number of points in the grid, and nf is the number of
    frequencies for the inverse fft.  The dimensions of the array
    are:
        0) velocity component (u,v,w)
        1) first spatial point,
        2) second spatial point,
        3) frequency.
    The ordering of the spatial points (dims 1,2) must match the
    ordering of the TurbSim grid.  See the tsGrid classes
    'sub2ind', 'ind2sub', 'flatten' and 'reshape' methods for more
    details on this.

    """

    def __init__(self,array):
        self.array=array

    def calc_phases(self,phases):
        """
        Compute and set the full cross-spectral matrix for component
        *comp* for 'coherence calculator' instance *cohi*.

        This method should not be called explicitly.  It is called by
        a 'coherence calculator' instance's __call__ method.

        This routine utilizes a model's 'calcCoh' method, which must
        be defined explicitly for all sub-classes of cohereModelBase.

        """
        tmp=np.empty((self.n_p,self.n_p),dtype=ts_float,order='F')
        for ff in np.range(self.n_f):
            tmp[:]=np.linalg.cholesky(self.array[comp,:,:,ff])
            for ii in range(self.n_p):
                coh[ii,ff]=sum(tmp.flatten('F')*phases[:,ff])

class cohereModelBase(modelBase,gridProps):
    """
    Examples
    --------
    When a coherence model class is called, it returns a 'coherence
    model instance' (as expected) e.g.:
    cm = myCohereModel(inarg1,inarg2,...)

    A 'coherence model instance' is an instance of a specific
    coherence model that is independent of a turbsim run (i.e. the
    coherence model instance holds parameters that are specific the
    grid, mean profile model, or spectral model).
    
    When a 'coherence model instance' is called, it returns a
    'coherence object' instance,
    e.g.:
    coh=cm(tsr)

    Where tsr is a 'tsrun' object.
    
    """
    cohereObj=cohereObj # This needs to be set to the appropriate
                        # 'coherence object' for each model.

    def __call__(self,tsrun):
        """
        Calculate the coherence matrix for TurbSim run *tsrun* according to this
        coherence model. The grid, profile and spectrum (tsrun.grid, tsrun.prof,
        tsrun.spec) must already be defined for the tsrun.

        Parameters
        ----------
        tsrun : A 'TurbSim run' object that contains the grid, prof and spec
                attributes.

        Returns
        -------
        A coherence instance (array or 'calculator'), e.g.:
        cohi=thisCohereModel(tsrun)

        The coherence instance is either an array of the full
        cross-spectral matrix (3 x n_p x n_p x n_f), or a 'calculator' that returns
        the components of that array. Either way, the components of the cross-spectral
        matrix (csm) can be obtained from:
        
        csm_u=cohi[0]
        csm_v=cohi[1]
        csm_w=cohi[2]

        """
        out=self.cohereObj(tsrun)
        if hasattr(self,'set_coefs'):
            self.set_coefs(out)
        return out

        
    
