"""
This module is for reading/writing PyTurbSim input (.inp) files.
"""
from os import listdir
import pkg_resources
from pyts import _version as ver
from pyts.runInput.base import tsinput
from copy import deepcopy
import numpy as np
from pyts.base import ts_float
from pyts.io.formatter import SuperFormatter


class InputFormatter(SuperFormatter):

    """
    This formatter is defined to format/parse the templates/inp
    file.
    """

    format_prfx = '<20'

    def _format_qs(self, value):
        """
        The "quote string" format specifier.
        """
        if not value.startswith('"'):
            value = '"' + value
        if not value.endswith('"'):
            value += '"'
        return value

    def _format_bool(self, value):
        return format(value.__repr__(),
                      self.format_prfx + 's')

    def _format_dec(self, value):
        if isinstance(value, (float, int, long)):
            return format(value, self.format_prfx + '.2g')
        return format('"%0.2f %0.2f"' % value, self.format_prfx + 's')


# This is the input-file template object:
template = InputFormatter(
    pkg_resources.resource_string(ver.pkg_name,
                                  'io/templates/inp'))


inputfile_form = dict()
for idx, ln in enumerate(template.template.split('\n')):
    if ln.startswith('{'):
        nm = ln[1:].split('!')[0].split(':')[0]
        inputfile_form[idx] = nm


def write(filename, in_dict):
    """
    Write an input file.
    """

    outstr = template(**in_dict)

    with open(filename, 'w') as outfl:
        outfl.write(outstr)
    return outstr


def read(fname):
    """
    Read a TurbSim input (.inp) file.

    Parameters
    ----------
    fname   :   str
                The filename to read from.

    Returns
    -------
    tsinput  :   :class:`.tsinput`, dict
                A PyTurbSim input dictionary.

    """
    # TurbSim input files are static:
    #   Variable are determined by line number.
    #   Only the first string on the line matters.
    #   All else is commenting.
    #   Therefore we simply assign variables by line number.
    ril = _readInputLine
    out = tsinput()
    out.filename = fname
    out['UserProfile'] = False
    with open(fname) as fl:
        dat = fl.readlines()
    fl.close()
    out['header'] = dat[0]
    # Header line at top of file.
    # (Sometimes used to indicate the files specific use)
    # Deal the data from the file:
    for idx, ln in enumerate(dat):
        if idx in inputfile_form:
            out[inputfile_form[idx]] = ril(dat[idx])
    # Customize the input fields for pyTurbSim...
    if out['RandSeed2'].__class__ is str and \
       out['RandSeed2'].upper() == 'RANLUX':
        out['RandSeed2'] = None
    for nm in ['IncDec1', 'IncDec2', 'IncDec3']:
        if out[nm] is not None:
            if out[nm].__class__ is str:
                try:
                    out[nm] = np.array(out[nm].split(), dtype=ts_float)
                except ValueError:
                    # This allows strings that don't convert to pass through.
                    pass
            else:
                out[nm] = np.array([out[nm], 0])
    if len(dat) >= 70 and dat[64].split()[1] == 'NumUSRz':
        # This file has a user-defined profile.
        out['UserProf_H'] = np.empty(out['NumUSRz'], dtype='float32')
        out['UserProf_U'] = np.empty_like(out['UserProf_H'])
        out['UserProf_Ang'] = np.empty_like(out['UserProf_H'])
        out['UserProf_Std'] = np.empty_like(out['UserProf_H'])
        out['UserProf_L'] = np.empty_like(out['UserProf_H'])
        for i in range(out['NumUSRz']):
            tmp = dat[72 + i].split()
            out['UserProf_H'][i] = ts_float(tmp[0])
            out['UserProf_U'][i] = ts_float(tmp[1])
            out['UserProf_Ang'][i] = ts_float(tmp[2])
            out['UserProf_Std'][i] = ts_float(tmp[3])
            out['UserProf_L'][i] = ts_float(tmp[4])
        out['UserProfile'] = True
        fls = listdir(fname.rpartition('/')[0])
        for fl in [fname.rpartition('/')[2].rpartition('.')[0] + '_Spec.inp',
                   'UsrSpec.inp', ]:
            if fl in fls:
                break
        out['psd'] = readInPSD(fname.rpartition('/')[0] + '/' + fl)
    for ky, val in out.iteritems():
        if val == 'default':
            out[ky] = None
    out.__original__ = deepcopy(out)
    return out


def _readInputLine(line):
    """
    This function parses data from input file lines and returns it as the
    correct 'type' (e.g. int, float, bool, str).
    """
    types = [np.int32, np.float32, bool, str]
    if line[0] == '"':
        val = line.split('"')[1]
    elif line[0] == "'":
        val = line.split("'")[1]
    else:
        val = line.split()[0]
    idx = 0
    if val == 'default':
        return None
    while True:
        try:
            if types[idx] is bool:
                tmp = val.lower().replace('"', '').replace("'", "")
                if not (tmp == 'false' or tmp == 'true'):
                    raise ValueError
                else:
                    return tmp == 'true'
            out = types[idx](val)
            if types[idx] is str and out.startswith('"') and out.endswith('"'):
                out = out[1:-1]
            return out
        except ValueError:
            idx += 1


def readInPSD(fname):
    """
    Read the input spectrum from file *fname*, and return it as a
    dictionary.

    Parameters
    ----------
    fname :     str
                The filename to read the PSD from.

    The frequency in the input file should be in units of hz, and the
    spectrum should be in units of m^2/s^2/hz.
    """
    ril = _readInputLine
    out = {}
    if fname.__class__ is file:
        dat = fname.readlines()
    else:
        with open(fname) as fl:
            dat = fl.readlines()
    NumUSRf = ril(dat[3])
    SpecScale1 = ril(dat[4])
    SpecScale2 = ril(dat[5])
    SpecScale3 = ril(dat[6])
    out['freq'] = np.empty(NumUSRf, **ts_float)
    out['Suu'] = np.empty(NumUSRf, **ts_float)
    out['Svv'] = np.empty(NumUSRf, **ts_float)
    out['Sww'] = np.empty(NumUSRf, **ts_float)
    for ind in range(out.NumUSRf):
        tmp = dat[ind + 11].split()
        out['freq'][ind] = tmp[0]
        out['Suu'][ind] = tmp[1]
        out['Svv'][ind] = tmp[2]
        out['Sww'][ind] = tmp[3]
    out['Suu'] *= SpecScale1
    out['Svv'] *= SpecScale2
    out['Sww'] *= SpecScale3
    return out


if __name__ == '__main__':

    def dict_diff(d1, d2):
        out = dict()
        for ky in d1:
            if ky in d2.keys():
                if not d2[ky] == d1[ky]:
                    out[ky] = str(d1[ky]) + ' - ' + str(d2[ky])
            else:
                out[ky] = d1[ky]
        for ky in d2:
            if ky not in d1.keys():
                out[ky] = d2[ky]
        return out

    dout = dict(
        PC_UW=0.2,
        URef=19.3,
        RandSeed1=34728904,
        RandSeed2=34728904,
        WrBHHTP=True,
        WrADHH=True,
        NumGrid_Z=10,
        NumGrid_Y=10,
        TimeStep=0.01,
        AnalysisTime=600,
        UsableTime=600,
        HubHt=80,
        GridHeight=90,
        GridWidth=90,
        TurbModel='SMOOTH',
        RefHt=90,
        IncDec1=(10.444, 0.1),
        IncDec2=10
        )

    fl = write('tmp/testfile.inp', dout)

    ## print dict_diff(inputfile_form, ifile_form_old)

    dnew = read('tmp/testfile.inp')
