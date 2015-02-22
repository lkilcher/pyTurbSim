"""
This module contains the turbulence models for the aquatic environment.

"""
from .mBase import specModelBase, np, specObj, ts_float


class tidal(specModelBase):

    r"""Tidal Channel spectral model.
    
    The tidal spectral model is based on measurements from Admiralty
    Inlet, in Puget Sound, WA.

    Parameters
    ----------
    Ustar :     float
                bottom boundary friction velocity [m/s].
    Zref :      float
                Reference height at which u'w' stress nears zero [m].

    Notes
    -----

    This model is similar to :class:`.NWTC_stable`, but uses
    different values for :attr:`coef`, and does not support new
    fit-coefficients. The form of this model is:

    .. math::
    
         S_k(f) = \frac{\sigma_k^2 \mathrm{coef}[k,0]}{1+\mathrm{coef}[k,1](f/\hat{f})^{5/3}}
         \qquad k=0,1,2\ (u,v,w)

    Where,

      :math:`\hat{f}=\frac{\partial \bar{u}}{\partial z}`

      :math:`\bar{u}` is the mean velocity from the :class:`.profObj`.

      :math:`\sigma_k^2 = U_{*}^2 \alpha_k exp(-2 z/Zref)`

      :math:`\alpha_k = (4.4,2.25,0.9)`

    See also
    --------
    :attr:`coef` : The 'fit coefficients'

    """
    coef = np.array([[1.21, 4.3], [0.33, 0.50], [0.23, 0.26]], dtype=ts_float)

    def __init__(self, Ustar, Zref):
        self.Ustar = Ustar
        self.Zref = Zref

    def _sumfile_string(self, tsrun, ):
        sumstring_format = """
        Turbulence model used                            =  {dat.model_desc}
        Turbulence velocity (UStar)                      =  {dat.Ustar:0.4g} [m/s]
        Log roughness scale (Zref)                       =  {dat.Zref:0.4g} [m]
        """
        return sumstring_format.format(dat=self)

    def __call__(self, tsrun):
        """Create the spectral object for :class:`.tsrun`.

        Parameters
        ----------
        tsrun :         :class:`.tsrun`
                        A TurbSim run object.

        Returns
        -------
        out :           :class:`.specObj`
                        An IEC spectral object for the grid in :class:`.tsrun`.

        """
        out = specObj(tsrun)
        dudz = np.abs(tsrun.prof.dudz[None, :, :, None])
        out.sigma2 = self.Ustar ** 2 * np.array([4.5, 2.25, 0.9])[:, None] \
            * np.exp(-2 * tsrun.grid.z[None, :] / self.Zref)
        out[:] = (out.sigma2[:, :, None, None]
                  * self.coef[:, 0][:, None, None, None] / dudz
                  ) / (1 + self.coef[:, 1][:, None, None, None]
                       * (tsrun.grid.f[None, None, None, :] / dudz) ** self.pow5_3)
        return out


class river(tidal):

    """River turbulence spectral model.

    This model is based on measurements from the East River, in New
    York City. It is identical to the :class:`tidal` model, but uses
    different values for :attr:`coef`.
    """

    # These fit positive velocity data in eastriver:
    coef = np.array([[1.057, 3.432],
                     [0.351, 0.546],
                     [0.265, 0.341]], dtype=ts_float)
    ## # These fit negative velocity data in eastriver:
    ## coef = np.array([[0.784, 2.085],
    ##                  [0.272, 0.357],
    ##                  [0.240, 0.290]], dtype=ts_float)
