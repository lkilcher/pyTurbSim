"""
This module contains the IEC turbulence models.

See the
`Original-TurbSim user manual
<http://wind.nrel.gov/designcodes/preprocessors/turbsim/TurbSim.pdf>`_
for more info on IEC spectral models.

"""
from .mBase import specModelBase, np, ts_float, specObj
from ..misc import InvalidConfig, Lambda
import warnings


class iecbase(specModelBase):

    r"""
    This is a base class for the IEC spectral models (IECKAI and IECVKM).

    Parameters
    ----------
    IECwindtype : str {'NTM'=normal,
                       'xETM'=extreme turbulence,
                       'xEWM1'=extreme 1-year wind,
                       'xEWM50'=extreme 50-year wind,
                       where x=wind turbine class 1, 2, or 3}
    IECstandard : int {1}
                  Currently this only supports IECstandard==1.
                  IECstandard == 2 and 3 correspond to small and
                  offshore wind, respectively, and have not yet been
                  implemented here.
    IECedition : int {2,3}
                 This is the 'edition' number of the -1 standard.
    IECturbc : str | float {'A','B','C'}
               The string form correspodes to the IEC turbulence
               'categories'. If a float is provided, it specifies a
               specific value of Turbulence Intensity.
    ETMc : float, optional (2.0)
           ETMc specifies the value of the 'c' parameter in the
           equation for :math:`\sigma_u`. It is only used when
           `IECwindtype`=`xETM`.

    Notes
    -----

    For further details on the IEC spectral models see the
    `Original-TurbSim user manual
    <http://wind.nrel.gov/designcodes/preprocessors/turbsim/TurbSim.pdf>`_.
    """

    def __init__(self, IECwindtype, IECstandard,
                 IECedition, IECturbc, ETMc=None):
        self.IECwindtype = IECwindtype
        self.IECstandard = IECstandard
        self.IECedition = IECedition
        self.IECturbc = IECturbc
        self.ETMc = ETMc

    def _sumfile_string(self, tsrun):
        windtype_desc = {'NTM': 'Normal Turbulence Model',
                         'ETM': 'Extreme Turbulence Model',
                         '1EWM1': 'Extreme 1-Year Wind Speed Model (Class 1)',
                         '2EWM1': 'Extreme 1-Year Wind Speed Model (Class 2)',
                         '3EWM1': 'Extreme 1-Year Wind Speed Model (Class 3)',
                         '1EWM50': 'Extreme 50-Year Wind Speed Model (Class 1)',
                         '2EWM50': 'Extreme 50-Year Wind Speed Model (Class 2)',
                         '3EWM50': 'Extreme 50-Year Wind Speed Model (Class 3)',
                         }
        edition_desc = {(1, 1): 'IEC 61400-1 Ed. 1: 1993',
                        (1, 2): 'IEC 61400-1 Ed. 2: 1999',
                        (1, 3): 'IEC 61400-1 Ed. 3: 2005',
                        (2, 2): 'IEC 61400-2 Ed. 2: 2005',
                        (3, 1): 'IEC 61400-3 Ed. 1: 2006',
                        }
        sumstring_format = """
        Turbulence model used                            =  {TurbModel_desc}
        Turbulence characteristic                        =  {IECturbc}
        IEC turbulence type                              =  {IECwindtype_desc}
        IEC standard                                     =  {IECstandard_desc}
        IEC Length scale (Lambda)                        =  {Lambda:0.4g} [m]
        IEC Sigma                                        =  {Sigma:0.4g} [m/s]
        ETM 'c' value                                    =  {etmc}
        """
        data = dict(
            TurbModel_desc=self.model_desc,
            IECturbc=(self.IECturbc if isinstance(self.IECturbc, basestring)
                      else '0.4g [%]'.format(self.IECturbc)),
            IECwindtype_desc=windtype_desc[self.IECwindtype],
            IECstandard_desc=edition_desc[(self.IECstandard, self.IECedition)],
            etmc='N/A' if self.ETMc is None else '{0:0.4g} [m/s]'.format(self.ETMc),
            Lambda=self.Lambda(tsrun.grid.zhub),
            Sigma=self.IEC_Sigma(tsrun.prof.uhub),
        )
        return sumstring_format.format(**data)

    def Lambda(self, zhub):
        """
        Compute the value of Lambda for height `zhub`.

        See also
        --------
        :func:`pyts.misc.Lambda`
        """
        return Lambda(zhub, self.IECedition)

    def _check_ewm(self, grid):
        if (self.IECturbc.__class__ is str and
            self.IECstandard == 1 and
            self.IECedition == 3 and
            self.IECwindtype.upper()[1:4] == 'EWM' and
                self.grid.time_sec_out != 600.):
            warnings.warn("The extreme wind model is only valid \
                          for 10min(600s) runs.  Setting \
                          'UsableTime' to 600s.")
            grid.time_sec_out = 600.

    def IEC_Sigma(self, uhub):
        r"""
        Calculate the default value of the standard deviation of
        u-component wind speed, :math:`\sigma` or :math:`\sigma_u`.

        Notes
        -----

        For input :class:`IECturbc <iecbase>` a numeric value, it
        simply specifies the turbulence intensity. That is,

          .. math::
             \sigma = \mathrm{IECturbc}\times u_{hub}

        Otherwise only IECversion == 1 is supported.  In that case:

        - For IECedition == 2 the windtype must be 'NTM', in that case:

          .. math::

              \sigma = Ti (\frac{15+\beta u_{hub}}{\beta + 1})

          Where,

            Ti = (0.18,0.16) for input variable :class:`IECturbc
            <iecbase>` = ('a','b'), respectively.

            :math:`\beta` = (2.0,3.0) for input variable
            :class:`IECturbc <iecbase>` = ('a','b'), respectively.

        - For IECedition == 3, Ti=(0.16,0.14,0.12) for
          IECturbc=(a,b,c), respectively. In this case, different
          formulations are used for different :class:`IECwindtype
          <iecbase>`.

            - For IECwindtype == 'NTM':

              .. math::
                 \sigma = Ti(0.75u_{hub} + 5.6)

            - For IECwindtype == 'xETM', the value of 'x' in that
              string provides another input variable,
              Vref=(50,42.5,37.5) for x=1,2,3.

              .. math::
                 \sigma = \mathrm{ETMc} \times Ti (0.072(0.2
                 V_{ref}/\mathrm{ETMc}+3)(u_{hub}/\mathrm{ETMc}-4)+10)

            - For IECwindtype == 'xEWM1' | 'xEWM50', the same value of
              Vref apply and

              .. math::
                 \sigma = 0.11 V_{ref}
        """
        iecver = self.IECstandard
        if self.IECturbc.__class__ is str:
            # !!!VERSION_INCONSISTENCY: add 'khtest' functionality.
            val = self.IECturbc.lower()
            wndtp = self.IECwindtype.lower()
            edi = self.IECedition
            if iecver is None:
                return None
            if iecver == 1:  # Onshore-big wind.
                if edi == 2:  # 2nd edition
                    if (wndtp != 'ntm'):
                        raise InvalidConfig("For IEC Turbulence models \
                        other than NTM, the iec edition must be 3.")
                    if val == 'a':
                        TurbInt15 = 0.18
                        SigmaSlope = 2.0
                    elif val == 'b':
                        TurbInt15 = 0.16
                        SigmaSlope = 3.0
                    else:
                        raise InvalidConfig(
                            "For the 61400-1 2nd edition, IECturbc must be \
                            set to 'a', 'b', or a number (Turbulence \
                            intensity)."
                        )

                    IEC_Sigma = TurbInt15 * \
                        ((15.0 + SigmaSlope * uhub) / (SigmaSlope + 1))
                    return IEC_Sigma

                elif edi == 3:  # 3rd edition
                    if val == 'a':
                        TurbInt15 = 0.16
                    elif val == 'b':
                        TurbInt15 = 0.14
                    elif val == 'c':
                        TurbInt15 = 0.12
                    else:
                        raise InvalidConfig(
                            "For the 61400-1 3rd edition, IECturbc must be \
                            set to 'a', 'b', 'c', or a number (Turbulence \
                            intensity)."
                        )

                    if wndtp == 'ntm':
                        IEC_Sigma = TurbInt15 * (0.75 * uhub + 5.6)  # /uhub
                        return IEC_Sigma
                    elif wndtp[0] not in ['1', '2', '3']:
                        raise InvalidConfig(
                            "A wind turbine class (1, 2 or 3) must be \
                            specified with the extreme turbulence and \
                            extreme wind types (e.g. '1ETM' or '2EWM')."
                        )

                    elif wndtp[1:4] in ['etm', 'ewm']:
                        Vref = {'1': 50, '2': 42.5, '3': 37.5}[wndtp[0]]
                        wndtp = wndtp[1:]
                        if wndtp == 'etm':
                            if self.ETMc is None:
                                self.ETMc = 2.0
                            IEC_Sigma = self.ETMc * TurbInt15 * \
                                (0.072 * (0.2 * Vref / self.ETMc + 3.) * (
                                    uhub / self.ETMc - 4) + 10.)
                            return IEC_Sigma
                        else:
                            return 0.11 * Vref
                    else:
                        raise InvalidConfig("Invalid 'IEC_WindType' specified in config file.")
            elif iecver == 2:  # Small wind.
                raise InvalidConfig("The 'small wind' spectral model (IEC version 2) is not "
                                    "implemented in PyTurbSim")
            elif iecver == 3:  # Offshore wind.
                raise InvalidConfig("The offshore wind IEC spectral model (IEC version 3) is "
                                    "not implemented in PyTurbSim")
        else:  # The IECturbc is numeric.
            if wndtp != 'ntm':
                raise InvalidConfig("If the 'IECturbc' config option is a number (specifying "
                                    "turbulence intensity), the IEC_WindType must be 'NTM'.")


class IECKai(iecbase):

    r"""IEC Kaimal spectral model.

    Notes
    -----

    The form of this model is,

    .. math::

        S_k(f) = \frac{4 \sigma_k^2/\hat{f}_k}{(1+6 f/\hat{f}_k
        )^{5/3}} \qquad \mathrm{for}\ k=u,v,w

    Where,

      :math:`\hat{f}_k = \alpha_k \bar{u}_{hub}/\Lambda`

      :math:`\alpha_k =` (8.1,2.7,0.66) for k= (u,v,w)

      :math:`\sigma_u` is defined in :attr:`IEC_Sigma <iecbase.IEC_Sigma>`

      :math:`\sigma_v=0.8\sigma_u` and :math:`\sigma_w=0.5\sigma_u`

      :math:`\Lambda` is defined in :attr:`Lambda <iecbase.Lambda>`

    """

    def __call__(self, tsrun):
        """Create the spectral object for a `tsrun` instance.

        Parameters
        ----------
        tsrun :         :class:`tsrun <pyts.main.tsrun>`
                        A TurbSim run object.

        Returns
        -------
        out :           :class:`specObj <.mBase.specObj>`
                        An IEC spectral object for the grid in `tsrun`.

        """
        self._check_ewm(tsrun.grid)
        out = specObj(tsrun)
        sig2 = 4 * self.IEC_Sigma(tsrun.prof.uhub) ** 2
        fctr = np.array([1, 0.64, 0.25], dtype=ts_float)
        L_u = self.Lambda(tsrun.grid.zhub) / tsrun.prof.uhub * \
            np.array([8.10, 2.70, 0.66], dtype=ts_float)
        for comp in self.comp:
            out[comp] = (sig2 * fctr[comp] * L_u[comp] / (
                1 + 6 * out.f * L_u[comp]) ** self.pow5_3)[None, None, :]
        return out


class IECVKm(iecbase):

    r"""IEC Von-Karman spectral model

    Notes
    -----

    The form of this model is,

    .. math::

          S_u(f) = \frac{4 \sigma^2/\hat{f}}{(1+71(f/\hat{f})^2)^{5/6}}

          S_v(f) = S_w(f) = (1+189(f/\hat{f})^2\frac{2\sigma^2/\hat{f}}
          {(1+71 (f/\hat{f})^2)^{11/6}}

    Where,

      :math:`\hat{f} = \bar{u}_{hub}/\Lambda`

      :math:`\sigma` is defined in :attr:`IEC_Sigma <iecbase.IEC_Sigma>`

      :math:`\Lambda` is defined in :attr:`Lambda <iecbase.Lambda>`

    """

    def __call__(self, tsrun):
        """
        Create and calculate the spectral object for a `tsrun`
        instance.

        Parameters
        ----------
        tsrun :         :class:`tsrun <pyts.main.tsrun>`
                        A TurbSim run object.

        Returns
        -------
        out :           :class:`specObj <.mBase.specObj>`
                        An IEC spectral object for the grid in `tsrun`.

        """
        self._check_ewm(tsrun.grid)
        out = specObj(tsrun)
        sig2 = 4 * self.IEC_Sigma(tsrun.prof.uhub) ** 2
        L_u = 3.5 * self.Lambda(tsrun.grid.zhub) / tsrun.prof.uhub
        dnm = 1 + 71 * (out.f * L_u) ** 2
        out[0] = (sig2 * L_u / (dnm) ** 0.8333333)[None, None, :]
        out[2] = out[1] = (sig2 / 2 * L_u / (dnm) ** 1.8333333 *
                           (1 + 189 * (out.f * L_u) ** 2))[None, None, :]
        return out
