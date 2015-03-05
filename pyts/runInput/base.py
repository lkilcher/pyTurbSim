"""
The base module for the runInput package. This module defines the
TurbSim input class (tsinput). The tsinput class is a dictionary for
storing data from a TurbSim input file. The class contains several
methods that specify default values for several input variables. Those
defaults documented in the Original-TurbSim documentation:
https://wind.nrel.gov/designcodes/preprocessors/turbsim/TurbSim.pdf

"""
from ..base import np
from numpy import uint32
from ..misc import kappa, InvalidConfig, zL, psiM


class tsinput(dict):

    """
    The TurbSim input object and 'global defaults' handler.

    This class works essentially as a dictionary, but with various
    functions and routines for providing default values in the event
    that 'input' values are not specified explicitly by the user.

    Regarding global defaults:
    The '_dflt_...' functions define 'global' default definitions
    (used by multiple profModels and/or turbModels).  Other, model
    specific, defaults are defined in the model itself.

    For further information on the 'defaults' defined here, consult
    the O-TurbSim documentation:
    https://wind.nrel.gov/designcodes/preprocessors/turbsim/TurbSim.pdf

    """

    def __getitem__(self, key):
        """
        Gets the item *key* from the dictionary.

        If there is no value, or it is 'None', and there is a
        '_dflt_<key>' property in the class, it uses this property to
        'set the default'.

        Otherwise return *None*.
        """
        if key == 'RandSeed':
            return self.randseed
        if key in ['IECstandard', 'IECedition'] and \
           dict.__getitem__(self, 'IECstandard').__class__ is str:
            self['IECstandard'], self['IECedition'] = self.parse_IEC_standard(dict.__getitem__(self, 'IECstandard'))  # noqa
        if key not in self or dict.__getitem__(self, key) is None:
            if hasattr(self, '_dflt_' + key):
                self[key] = self.__getattribute__('_dflt_' + key)
                self._dict_isdefault[key] = 2
                return self[key]
            else:
                return None
        return dict.__getitem__(self, key)

    def __setitem__(self, key, val):
        if key == 'RandSeed':
            self.randseed = val
        else:
            dict.__setitem__(self, key, val)

    @property
    def incdec_a(self,):
        """
        The 'a' coherence decrement.
        """
        out = [None, None, None]
        if self['IncDec1'] is not None:
            if hasattr(self['IncDec1'], '__len__'):
                out[0] = self['IncDec1'][0]
            else:
                out[0] = self['IncDec1']
        if self['IncDec2'] is not None:
            if hasattr(self['IncDec2'], '__len__'):
                out[1] = self['IncDec2'][0]
            else:
                out[1] = self['IncDec2']
        if self['IncDec3'] is not None:
            if hasattr(self['IncDec3'], '__len__'):
                out[2] = self['IncDec3'][0]
            else:
                out[2] = self['IncDec3']
        return out

    @property
    def incdec_b(self,):
        out = [0., 0., 0.]
        if self['IncDec1'] is not None and hasattr(self['IncDec1'], '__len__'):
            out[0] = self['IncDec1'][1]
        if self['IncDec2'] is not None and hasattr(self['IncDec2'], '__len__'):
            out[1] = self['IncDec2'][1]
        if self['IncDec3'] is not None and hasattr(self['IncDec3'], '__len__'):
            out[2] = self['IncDec3'][1]
        return out

    def parse_IEC_standard(self, iecstd):
        if iecstd.__class__ is str:
            iecstd = iecstd.lower()
            tmp = int(iecstd[0])
            if len(iecstd) > 1 and tmp == 1:
                iecedt = int(iecstd[-1])
            else:
                iecedt = None
                # There are no editions to the -2 and -3 standards.
            iecstd = tmp
        elif iecstd == 1 or iecstd is None:
            iecstd = 1
            if self.turbmodel == 'ieckai':
                iecedt = 3
            else:
                iecedt = 2
        else:
            iecedt = None  # There are no editions to the -2 and -3 standards.
        if iecedt == 3 and self.turbmodel == 'iecvkm':
            raise InvalidConfig("The von-Karman spectral model (IECVKM) \
            is not valid for IEC standard 61400-1's 3rd edition. Either \
            change TurbModel to IECKAI, or change the IECstandard to '1-ed2' \
            or simply '1'.")
        elif iecedt > 1 and self['IEC_WindType'].lower() != 'ntm':
            raise InvalidConfig("If the IECstandard is 1-ed2 or 1-ed3, \
            than the WindType must be 'NTM'.")
        return (iecstd, iecedt)

    def __init__(self, *args, **kwargs):
        self._dict_isdefault = {}
        dict.__init__(self, *args, **kwargs)

    def isdefault(self, key):
        """
        Is the given variable a default?

        True : The value is not specified and there is no '_dflt_...' function.
        2    : The value is defined by a '_dflt_...' function.
        False: The value is specified explicitly in the configuration.

        """
        if self[key] is None:
            return True
        if key in self._dict_isdefault:
            return self._dict_isdefault[key]
        else:
            return False

    @property
    def randseed(self,):
        tmpval = 0
        if 'RandSeed1' in self and self['RandSeed1'] is not None:
            tmpval += uint32(self['RandSeed1'])
        if 'RandSeed2' in self and self['RandSeed2'] is not None:
            tmpval += uint32(self['RandSeed2']) << 32
        if tmpval == 0:
            return None
        return tmpval

    @randseed.setter
    def randseed(self, val):
        if val is None:
            self['RandSeed1'] = None
            self['RandSeed2'] = None
        else:
            self['RandSeed1'] = np.int32(val & 2 ** 32 - 1)
            val2 = np.int32(val >> 32)
            if val2 > 0:
                self['RandSeed2'] = val2
            else:
                self['RandSeed2'] = None

    @property
    def _dflt_WindProfileType(self,):
        if self.turbmodel == 'gp_llj':
            return 'JET'
        elif self.turbmodel in ['river', 'tidal']:
            return 'H2L'
        else:
            return 'IEC'

    @property
    def turbmodel(self,):
        return self['TurbModel'].lower()

    # These are only called if the key is not in the dictionary:
    @property
    def _dflt_Z0(self,):
        return {'ieckai': 0.03,
                'iecvkm': 0.03,
                'smooth': 0.01,
                'gp_llj': 0.005,
                'nwtcup': 0.021,
                'wf_upw': 0.018,
                'wf_07d': 0.064,
                'wf_14d': 0.233,
                'tidal': 0.1,
                'river': 0.1
                }[self.turbmodel]

    @property
    def _dflt_UStar(self,):
        if ('URef' not in self or self['URef'] is None) and \
           ('UStar' not in self or self['UStar'] is None):
            raise InvalidConfig('Either URef or UStar must be defined in the input file.')
        mdl = self.turbmodel
        ustar0 = self.ustar0
        if mdl == 'smooth':
            ustar = ustar0
        elif mdl == 'nwtcup':
            ustar = 0.2716 + 0.7573 * ustar0 ** 1.2599
        elif mdl == 'gp_llj':
            ustar = 0.17454 + 0.72045 * ustar0 ** 1.36242
        elif mdl == 'wf_upw':
            if self.zL < 0:
                ustar = 1.162 * ustar0 ** 0.66666
            else:
                ustar = 0.911 * ustar0 ** 0.66666
        elif mdl in ['wf_07d', 'wf_14d']:
            if self.zL < 0:
                ustar = 1.484 * ustar0 ** 0.66666
            else:
                ustar = 1.370 * ustar0 ** 0.66666
        elif mdl in ['tidal', 'river']:
            ustar = self['URef'] * 0.05
        return ustar

    @property
    def _dflt_Latitude(self,):
        return 45.0

    @property
    def _dflt_ZI(self,):
        if self['UStar'] < self.ustar0:
            return 400 * self['URef'] / np.log(self['RefHt'] / self['Z0'])
        else:
            return self['UStar'] / (12 * 7.292116e-5 * np.sin(np.pi / 180 * np.abs(self['Latitude'])))  # noqa

    @property
    def _dflt_PC_UV(self,):
        return 0.0

    @property
    def _dflt_PC_UW(self,):
        return 0.0

    @property
    def _dflt_PC_VW(self,):
        return 0.0

    @property
    def _dflt_PLExp(self,):
        """
        The default Wind Profile power law exponent.
        """
        tm = self.turbmodel
        Ri = self['RICH_NO']
        if tm in ['ieckai', 'iecvkm']:
            if self['IECstandard'] == 1 and \
               self['IEC_WindType'].lower() == 'ewm':
                plexp = 0.11
            elif self['IECstandard'] == 3:
                plexp = 0.14
            plexp = {'ewm': 0.11, 'ntm': 0.14}.get(
                self['WindProfileType'], 0.2)
        elif tm in ['wf_upw', 'nwtcup']:
            if self['IECturbc'].lower() == 'khtest' and \
               self.turbmodel == 'nwtcup':
                plexp = 0.3
            if Ri > 0:
                plexp = 0.14733
            else:
                plexp = 0.087688 + 0.059641 * np.exp(Ri / 0.04717783)
        elif tm in ['wf_07d', 'wf_14d']:
            if Ri > 0.04:
                plexp = 0.17903
            else:
                plexp = 0.1277 + 0.031229 * np.exp(Ri / 0.0805173)
        else:  # ['smooth','gp_llj','tidal','river']:
            plexp = 0.143
        return plexp

    ### These are helper functions, not 'default input parameters':
    @property
    def ustar0(self,):
        return (kappa * self['URef'] /
                (np.log(self['RefHt'] / self['Z0']) - self.psiM))

    @property
    def zL(self,):
        if not hasattr(self, '_val_zL'):
            self._val_zL = zL(self['RICH_NO'], self['TurbModel'])
        return self._val_zL

    @property
    def psiM(self,):
        if not hasattr(self, '_val_psiM'):
            self._val_psiM = psiM(self['RICH_NO'], self['TurbModel'])
        return self._val_psiM
