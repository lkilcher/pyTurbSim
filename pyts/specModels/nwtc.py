"""
This module contains the nwtc spectral models.
"""
from .mBase import np, ts_float, specObj, specModelBase
from ..misc import zL
from .kelley_coefs import calc_nwtcup_coefs, p_coefs_unstable, f_coefs_unstable


class genNWTC(specModelBase):

    """
    An abstract base class for NWTC spectral models.

    """

    def __call__(self, tsrun):
        """
        Create and calculate the spectral object for a `tsrun`
        instance.

        Parameters
        ----------
        tsrun :         :class:`.tsrun`
                        A TurbSim run object.

        Returns
        -------
        out :           :class:`.specObj`
                        An NWTC spectral object for the grid in `tsrun`.

        """
        out = specObj(tsrun)
        # !!!FIXTHIS: The following lines bind calculation to the
        # !!!MODEL. This goes against the PyTurbSim philosophy of
        # !!!keeping calculations separated from models.
        self.f = out.f
        self._work = np.zeros(out.n_f, dtype=ts_float)
        self.zhub = tsrun.grid.zhub
        # Fixing this will require something like changing:
        #   out[comp][iz, iy] = model(z, u, comp)
        # to:
        #   self.model(out, u, icomp, iz, iy)
        # Note here that u must be supplied explicitly because it is
        # not known to 'out'.
        # This would also require:
        # 1) deleting the self._work variable
        # 2) changing ``def L(self,)`` from a property to ``def
        #    L(self, tsrun)`` and using tsrun.grid.zhub their.
        # 3) changing all calls to ``self.L`` accordingly.
        for iz in range(out.n_z):
            for iy in range(out.n_y):
                z = out.grid.z[iz]
                u = tsrun.prof.u[iz, iy]
                for comp in out.grid.comp:
                    self._work[:] = 0.0
                    out[comp][iz, iy] = self.model(z, u, comp)
        return out


class NWTC_stable(genNWTC):

    r"""The NWTC 'stable' spectral model.

    Parameters
    ----------
    Ustar :     float
                friction velocity [m/s].
    zL :        float
                The z/L stability parameter [non-dimensional]
    coef :      array_like((3,2),dtype=float)
                spectral coefficients for this model.

    Notes
    -----

    The specific form of this model is,

    .. math::

        S_k(f) = \frac{U_{*}^2 A_k
        \hat{f}^{-1}\gamma}{1+B_k(f/\hat{f})^{5/3}} \qquad k=0,1,2\
        (u,v,w)


    Where,

       :math:`\gamma=(\phi_E/\phi_M)^{2/3}`

       :math:`\hat{f}=\frac{\bar{u}\phi_M}{z}`

       :math:`\phi_E=(1+2.5 (z/L)^{0.6})^{1.5}`

       :math:`\phi_M=1+4.7*z/L`

       :math:`\bar{u}`, is the mean velocity at each grid-point, (taken from the profile model)

       :math:`A_k=\mathrm{scoef}[k,0] \mathrm{coef}[k,0]`

       :math:`B_k=\mathrm{scoef}[k,1] \mathrm{coef}[k,1]^{5/3}`

    See also
    --------
    :attr:`s_coef` : These are the hard-wired :math:`\mathrm{scoef}` coefficients.


    """
    s_coef = np.array([[79., 263.], [13., 32.], [3.5, 8.6]])

    def __init__(self, Ustar, zL, coef=None):
        self.Ustar = Ustar
        self.Ustar2 = self.Ustar ** 2
        self.zL = zL
        if coef is None:
            self.coefs = np.ones((3, 2), dtype=ts_float)
        else:
            self.coefs = coef

    def _sumfile_string(self, tsrun):
        sumstring_format = """
        Turbulence model used                            =  {dat.model_desc}
        Turbulence velocity (UStar)                      =  {dat.Ustar:0.2f} [m/s]
        Stability parameter (z/L)                        =  {dat.zL:0.2f}
        coefs  u                           =  [{p[0][0]:0.2f}, {p[0][1]:0.2f}]
               v                           =  [{p[1][0]:0.2f}, {p[1][1]:0.2f}]
               w                           =  [{p[2][0]:0.2f}, {p[2][1]:0.2f}]
        """
        return sumstring_format.format(dat=self,
                                       p=self.coefs,)

    @property
    def _phie(self):
        return (1. + 2.5 * self.zL ** 0.6) ** 1.5

    @property
    def _phim(self):
        return 1. + 4.7 * self.zL

    def model(self, z, u, comp):
        """
        Calculate the spectral model for height `z`, velocity `u`, and
        velocity component `comp`.
        """
        coef = self.coefs[comp]
        z_u = z / u
        denom = (self.f / self._phim)
        numer = (self._phie / self._phim) ** self.pow2_3 / self._phim * self.Ustar2
        if coef.ndim > 1:
            self._work[:] = 0
            for c in coef:
                self._work += self.model(z, u, comp)
            return self._work
        return (coef[0] * self.s_coef[comp, 0] * numer * z_u /
                (1. + self.s_coef[comp, 1] * (coef[1] * z_u * denom) ** self.pow5_3))


class NWTC_unstable(genNWTC):

    r"""The NWTC 'unstable' spectral model.

    .. math::
       S_k(f) = U_\mathrm{star}^2 G_k(f,\bar{u},z,ZI) \qquad k = u, v, w

    Where :math:`G_k` is a function that depends on the frequency,
    :math:`f`, the mean velocity :math:`\bar{u}`, the height
    :math:`z`, and the mixing layer depth :math:`ZI`. The exact form
    of :math:`G_k` can be found in this class's 'model' method.

    Parameters
    ----------
    Ustar : float
            The friction velocity (at the bottom boundary).
    zL    : float
            The ratio of the HubHt to the Monin-Obhukov length.
    ZI    : float
            The friction boundary layer height.
    p_coefs : array_like(3,2), optional
              Fit coefficients for this model.
    f_coefs : array_like(3,2), optional
              Fit coefficients for this model.

    """

    def __init__(self, Ustar, zL, ZI, p_coefs=None, f_coefs=None):
        self.Ustar = Ustar
        self.Ustar2 = self.Ustar ** 2
        self.zL = zL
        self.ZI = ZI
        if p_coefs is None:
            self.p_coefs = p_coefs_unstable
        if f_coefs is None:
            self.f_coefs = f_coefs_unstable

    def _sumfile_string(self, tsrun, ):
        sumstring_format = """
        Turbulence model used                            =  {dat.model_desc}
        Turbulence velocity (UStar)                      =  {dat.Ustar:0.4g} [m/s]
        Mixing layer depth (ZI)                          =  {dat.ZI:0.4g} [m]
        Stability parameter (z/L)                        =  {dat.zL:0.4g}
        Monin-Obhukov Length scale                       =  {Lmo:0.4g} [m]
        p_coefs   u                =  [{p[0][0]:0.4g}, {p[0][1]:0.4g}]
                  v                =  [{p[1][0]:0.4g}, {p[1][1]:0.4g}]
                  w                =  [{p[2][0]:0.4g}, {p[2][1]:0.4g}]
        f_coefs   u                =  [{f[0][0]:0.4g}, {f[0][1]:0.4g}]
                  v                =  [{f[1][0]:0.4g}, {f[1][1]:0.4g}]
                  w                =  [{f[2][0]:0.4g}, {f[2][1]:0.4g}]
        """
        return sumstring_format.format(dat=self,
                                       Lmo=self.L,
                                       p=self.p_coefs,
                                       f=self.f_coefs,)

    @property
    def L(self, ):
        if not hasattr(self, 'zhub'):
            raise Exception("The Monin-Obhukov is unknown until this "
                            "model has been '__call__'d.")
        return self.zhub / self.zL

    def model(self, z, u, comp):
        r"""
        Computes the spectrum for this 'unstable' spectral model.

        Parameters
        ----------
        z : array_like (nz)
            Height above the surface [m].
        u : array_like (nz,ny)
            Mean velocity [m/s].
        comp : int {0,1,2}
               Index (u,v,w) of the spectrum to compute.

        Returns
        -------
        spec : :class:`.mBase.specObj`
               The spectral object which contains the 'array'
               (property) of spectra at each point in the grid.

        Notes
        -----

        The form of the u-compenent spectrum is:

        .. math::
           S_u(f) = U_\mathrm{star}^2 \left( p_{u,1}\frac{\alpha}{1+( F_{u,1} \hat{f})^{5/3}} +
           p_{u,2}\frac{\beta}{( \delta_u + F_{u,2} f' )^{5/3} } \right )

        The form of the v-compenent spectrum is

        .. math::
           S_v(f) = U_\mathrm{star}^2 \left( p_{v,1}\frac{\alpha}{(1 + F_{v,1} \hat{f})^{5/3}} +
           p_{v,2}\frac{\beta}{( \delta_v + F_{v,2} f' )^{5/3} } \right )

        The form of the w-compenent spectrum is:

        .. math::
           S_w(f) = U_\mathrm{star}^2 \left( p_{w,1}\frac{\alpha}{(1 +
           F_{w,1} \hat{f})^{5/3}} \gamma + p_{w,2}\frac{\beta}{ 1 +
           F_{w,2} {f'} ^{5/3} } \right )

        Where,

           :math:`\hat{f} = f ZI/\bar{u}`

           :math:`f' = f z/ \bar{u}`

           :math:`\alpha = ZI^{5/3}/(-\bar{u}L^{2/3})`

           :math:`\beta = z(1-z/ZI)^2/\bar{u}`

           :math:`\delta_u = 1+15 z/ZI`

           :math:`\delta_v = 1+2.8 z/ZI`

           :math:`\gamma  = \frac{f'^2+0.09(z/ZI)^2}{f'^2+0.0225}`

        """
        p_coef = self.p_coefs[comp]
        f_coef = self.f_coefs[comp]
        pow5_3 = self.pow5_3
        z_ZI = z / self.ZI
        num0 = self.Ustar2 * self.ZI / u * (self.ZI / -self.L()) ** self.pow2_3
        fZI_u = self.f * self.ZI / u
        z_u = z / u
        num1 = self.Ustar2 * z_u * (1 - z_ZI) ** 2
        fz_u = self.f * z_u
        if comp == 0:
            tmp0 = 1 + 15 * z_ZI
            self._work = (p_coef[0] * num0 / (1 + (fZI_u * f_coef[0]) ** pow5_3)
                          + p_coef[1] * num1 / (tmp0 + f_coef[1] * fz_u) ** pow5_3)
        elif comp == 1:
            tmp0 = 1 + 2.8 * z_ZI
            self._work = (p_coef[0] * num0 / (1 + f_coef[0] * fZI_u) ** pow5_3
                          + p_coef[1] * num1 / (tmp0 + f_coef[1] * fz_u) ** pow5_3)
            ## # Handle extra (e.g. wake, for outf_turb) coefficients:
            ## if coef.shape[0]>2 and not np.isnan(coef[2,0]+coef[2,1]):
            # self._work+=coef[2,0]*17*num1/(tmp0+coef[2,1]*9.5*fz_u)**pow5_3
        else:
            self._work = (p_coef[0] * num0 / (1 + f_coef[0] * fZI_u) ** pow5_3
                          * np.sqrt((fz_u ** 2 + (0.3 * z_ZI) ** 2) / (fz_u ** 2 + 0.0225))
                          + p_coef[1] * num1 / (1 + f_coef[1] * fz_u ** pow5_3))
        return self._work


def smooth(Ustar, Ri, ZI=None):
    """
    Compute the 'smooth' spectral model.

    Parameters
    ----------
    Ustar :     float
                The bottom-boundary friction velocity [m/s].

    Ri :        float
                The Richardson number stability parameter.

    ZI :        float, optional
                mixing layer depth [m].  Only needed for Ri<0.

    Returns
    -------
    specModel : :class:`NWTC_stable` (Ri>0), or :class:`NWTC_unstable` (Ri<0)

    """
    zl_ = zL(Ri, 'smooth')
    if zl_ >= 0:
        out = NWTC_stable(Ustar, zl_)
    else:
        out = NWTC_unstable(Ustar, zl_, ZI)
    return out


def nwtcup(Ustar, Ri, ZI=None):
    """
    Compute the 'nwtcup' spectral model.

    Parameters
    ----------
    Ustar :     float
                The bottom-boundary friction velocity [m/s].

    Ri :        float
                The Richardson number stability parameter.

    ZI :        float, optional
                mixing layer depth [m].  Only needed for Ri<0.

    Returns
    -------
    specModel : :class:`NWTC_stable` (Ri>0), or :class:`NWTC_unstable` (Ri<0)

    """
    zl_ = zL(Ri, 'nwtcup')
    coefs = calc_nwtcup_coefs(zl_)
    if zl_ >= 0:
        out = NWTC_stable(Ustar, zl_, coefs)
    else:
        out = NWTC_unstable(Ustar, zl_, ZI, coefs)
    return out
