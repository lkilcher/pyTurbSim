"""
This module contains the following spectral models:
  smooth - The 'smooth' spectral model.
  nwtcup - The NWTC 'upwind' model.
"""
from .mBase import np,ts_float,specObj,specModelBase
from ..misc import zL,fix2range
from kelley_coefs import calc_nwtcup_coefs

class genNWTC(specModelBase):
    """
    Some text.
    """
    def __call__(self,tsrun):
        """
        Some more text.
        """
        out=specObj(tsrun)
        # !!!FIXTHIS: The following lines bind output to the specModel object. It would be better to make this explicit, or something.
        self.f=out.f
        self._work=np.zeros(out.n_f,dtype=ts_float)
        for iz in range(out.n_z):
            for iy in range(out.n_y):
                z=out.grid.z[iz]
                u=tsrun.prof.u[iz,iy]
                for comp in out.grid.comp:
                    self._work[:]=0.0
                    out[comp][iz,iy]=self.model(z,u,comp)
        return out

class NWTC_stable(genNWTC):
    """
    Some text.
    """
    s_coef=np.array([[79.,263.],[13.,32.],[3.5,8.6]])

    def __init__(self,Ustar,zL,coefs=None):
        # !!!ADDDOC
        self.Ustar=Ustar
        self.Ustar2=self.Ustar**2
        self.zL=zL
        if coefs is None:
            self.coefs=np.ones((3,2),dtype=ts_float)
        else:
            self.coefs=coefs
    
    @property
    def _phie(self):
        return (1.+2.5*self.zL**0.6)**1.5
    @property
    def _phim(self):
        return 1.+4.7*self.zL
    
    def model(self,z,u,comp):
        # !!!ADDDOC
        coef=self.coefs[comp]
        z_u=z/u
        denom=(self.f/self._phim)
        numer=(self._phie/self._phim)**self.pow2_3/self._phim*self.Ustar2
        if coef.ndim>1:
            self._work[:]=0
            for c in coef:
                self._work+=self.model(z,u,comp)
            return self._work
        return coef[0]*self.s_coef[comp,0]*numer*z_u/(1.+self.s_coef[comp,1]*(coef[1]*z_u*denom)**self.pow5_3)


class NWTC_unstable(genNWTC):
    r"""
    The NWTC 'unstable' spectral model.

    .. math::
       S_i(f) = U_\mathrm{star}^2 G_i(f,\bar{u},z,ZI) \qquad i = u, v, w

    Where :math:`G_i` is a function that depends on the frequency,
    :math:`f`, the mean velocity :math:`\bar{u}`, the height
    :math:`z`, and the mixing layer depth :math:`ZI`. The exact form
    of :math:`G_i` can be found in this class's 'model' method.
    
    """

    def __init__(self,Ustar,zL,ZI,p_coefs=None,f_coefs=None):
        """
        Some more text.
        """
        # !!!ADDDOC
        self.Ustar=Ustar
        self.Ustar2=self.Ustar**2
        self.zL=zL
        self.ZI=ZI
        if p_coefs is None:
            self.p_coefs=p_coefs_unstable
        if f_coefs is None:
            self.f_coefs=f_coefs_unstable

    @property
    def L(self,):
        return self.grid.zhub/self.zL

    def model(self,z,u,comp):
        r"""
        Computes the spectrum for this 'unstable' spectral model.

        Args
        ----
        
        z (array: nz)  - Height above the surface [m].
        
        u (array: nz,ny)  - Mean velocity [m/s].

        comp (int) - Index (0,1,2)=(u,v,w) of the spectrum to compute.

        Returns
        -------

        spec (array: nz,ny,nf) - The spectrum at each point.

        The form of the u-compenent spectrum is:
        
        .. math::
           S_u(f) = U_\mathrm{star}^2 \left( p_{u,1}\frac{\alpha}{1+( F_{u,1} \hat{f})^{5/3}} +
           p_{u,2}\frac{\beta}{( \delta_u + F_{u,2} f' )^{5/3} } \right )

        The form of the v-compenent spectrum is:

        .. math::
           S_v(f) = U_\mathrm{star}^2 \left( p_{v,1}\frac{\alpha}{(1 + F_{v,1} \hat{f})^{5/3}} +
           p_{v,2}\frac{\beta}{( \delta_v + F_{v,2} f' )^{5/3} } \right )

        The form of the w-compenent spectrum is:

        .. math::
           S_w(f) = U_\mathrm{star}^2 \left( p_{w,1}\frac{\alpha}{(1 + F_{w,1} \hat{f})^{5/3}} \gamma +
           p_{w,2}\frac{\beta}{ 1 + F_{w,2} {f'} ^{5/3} } \right )

        Where:
        
           :math:`\hat{f} = f ZI/\bar{u}`
           
           :math:`f' = f z/ \bar{u}`

           :math:`\alpha = ZI^{5/3}/(-\bar{u}L^{2/3})`

           :math:`\beta = z(1-z/ZI)^2/\bar{u}`

           :math:`\delta_u = 1+15 z/ZI`

           :math:`\delta_v = 1+2.8 z/ZI`

           :math:`\gamma  = \frac{f'^2+0.09(z/ZI)^2}{f'^2+0.0225}`
        
        """
        p_coef=self.p_coefs[comp]
        f_coef=self.f_coefs[comp]
        pow5_3=self.pow5_3
        z_ZI=z/self.ZI
        num0=self.Ustar2*self.ZI/u*(self.ZI/-self.L)**self.pow2_3
        fZI_u=self.f*self.ZI/u
        num1=self.Ustar2*z_u*(1-z_ZI)**2
        fz_u=self.f*z_u
        if comp==0:
            tmp0=1+15*z_ZI
            self._work=p_coef[0]*num0/(1+(fZI_u*f_coef[0])**pow5_3) + p_coef[1]*num1/(tmp0+f_coef[1]*fz_u)**pow5_3
        elif comp==1:
            tmp0=1+2.8*z_ZI
            self._work=p_coef[0]*num0/(1+f_coef[0]*fZI_u)**pow5_3 + p_coef[1]*num1/(tmp0+f_coef[1]*fz_u)**pow5_3
            ## # Handle extra (e.g. wake, for outf_turb) coefficients:
            ## if coef.shape[0]>2 and not np.isnan(coef[2,0]+coef[2,1]):
            ##     self._work+=coef[2,0]*17*num1/(tmp0+coef[2,1]*9.5*fz_u)**pow5_3
        else:
            self._work=p_coef[0]*num0/(1+f_coef[0]*fZI_u)**pow5_3*np.sqrt((fz_u**2+(0.3*z_ZI)**2)/(fz_u**2+0.0225)) + p_coef[1]*num1/(1+f_coef[1]*fz_u**pow5_3)
        return self._work

def smooth(Ustar,Ri,ZI=None):
    """
    Compute the 'smooth' spectral model.

    Args
    ----
    Ustar         - The bottom-boundary friction velocity [m/s].
    Ri            - The Richardson number stability parameter.
    ZI (optional) - mixing layer depth [m].  Only needed for Ri<0.
    
    Returns
    -------
    A specModel object, either the NWTC_stable spectral object (for
    Ri>=0), or a NWTC_unstable spectral object.

    See Also
    --------
    NWTC_stable - spectral model.
    NWTC_unstable - spectral model.
    
    """
    zl_=zL(Ri,'smooth')
    if zl_>=0:
        out=NWTC_stable(Ustar,zl_)
    else:
        out=NWTC_unstable(Ustar,zl_,ZI)
    return out

def nwtcup(Ustar,Ri,ZI=None):
    """
    Compute the 'nwtcup' spectral model.

    Args
    ----
    Ustar         - The bottom-boundary friction velocity [m/s].
    Ri            - The Richardson number stability parameter.
    ZI (optional) - mixing layer depth [m].  Only needed for Ri<0.

    Returns
    -------
    A specModel object, either the NWTC_stable spectral object (for
    Ri>=0), or a NWTC_unstable spectral object.

    See Also
    --------
    NWTC_stable - spectral model.
    NWTC_unstable - spectral model.

    """
    zl_=zL(Ri,'nwtcup')
    coefs=calc_nwtcup_coefs(zl_)
    if zl_>=0:
        out=NWTC_stable(Ustar,zl_,coefs)
    else:
        out=NWTC_unstable(Ustar,zl_,ZI,coefs)
    return out
