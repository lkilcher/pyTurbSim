from mBase import cohModelBase,cohereCalc,cohereCalc_pack

class cohModelIEC(cohModelBase):
    # !!!ADDDOC
    """
    The coherence model for the IEC spectral models.
    """

    def L(self,zhub):
        return self._Lfactor*Lambda(zhub,self.IECedition)
    
    def __init__(self,IECedition):
        # !!!ADDDOC
        """
        Initialize the coherence parameters for the IEC spectral model.
        """
        self.IECedition=IECedition
        
        if IECedition==2:
            self._Lfactor=3.5
            self.a=8.8
        else: # 3rd edition IEC standard:
            self._Lfactor=3.5
            self.a=12.

    def tslib_func(self,calcinst):
        

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
            self._crossSpec_pack=base.tslib.ieccoh(self.Saa_flat[comp],self.f,self.grid.y,self.grid.z,self.profModel.uhub,self.a,self.L(calcinst.grid.zhub),len(self.f),len(self.grid.y),len(self.grid.z))
            self._crossSpec_pack_name=comp
            return self._crossSpec_pack
        else:
            return cohModelBase.get_crossSpec_pack(self,comp)

    def calcCoh(self,calcinst,comp,ii,jj):
        """
        The *comp*=(0,1,2=u,v,w), coherence between points *ii*=(iz,iy) and *jj*=(jz,jy).
        """
        if comp==0:
            r=calcinst.grid.dist(ii,jj)
            calcinst._work[:]=np.exp(-self.a*np.sqrt((calcinst.f*r/calcinst.uhub)**2+(0.12*r/self.L(calcinst.grid.zhub))**2))
        else:
            calcinst._work[:]=0
        return calcinst._work
