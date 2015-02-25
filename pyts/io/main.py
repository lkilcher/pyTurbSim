"""
This is the main (top-level) io module. It defines the 'readModel'
function, which is useful for collecting information from available
TurbSim input/output files.
"""

import bladed
import aerodyn
import config as cfg_io
from base import convname
from ..main import tsdata
from ..runConfig import main as runConfig
import os

readers = {'wnd': bladed.read,
           'bl': bladed.read,
           'bts': aerodyn.read, }


def readModel(fname, inp_fname=None):
    """
    Read a TurbSim data and input file and return a
    :class:`tsdata <pyts.main.tsdata>` data object.

    Parameters
    ----------
    fname : str
            The filename to load.  If `fname` ends in .inp, it reads
            this input file, and searches for a binary file that can
            be read (throws error if none is found). Otherwise,

    inp_fname : str, optional
                The input file name to associate with the data-file
                `fname`.

    Returns
    -------
    tsdata : :class:`tsdata <pyts.main.tsdata>`
             The TurbSim data contained in the binary data file.

    Notes
    -----

    If `fname` is a filetype that can be read, it reads that file and
    the associated .inp file.

    In other words::
      tsdat=readModel('TurbSim.inp')

    and::
      tsdat=readModel('TurbSim.bts')

    Do essentially the same thing.

    """
    if fname.endswith('.inp'):
        config = cfg_io.read(fname)
        foundfile = False

        for sfx, rdr in readers.iteritems():
            fnm = convname(fname, sfx)
            if os.path.isfile(fnm):
                foundfile = True
                utmp = rdr(fnm)
                break

        if not foundfile:
            raise IOError('TurbSim output file not found. Run pyTurbSim '
                          'on the input file %s, before loading...' % (fname))

    else:
        if inp_fname is None:
            config = cfg_io.read(convname(fname, 'inp'))
        else:
            config = cfg_io.read(inp_fname)

        sfx = fname.split('.')[-1]
        if sfx in readers.keys():
            rdr = readers[sfx]
            utmp = rdr(fname)
        else:
            raise IOError('No reader for this file type.')

    umn = utmp.mean(-1)
    utmp -= umn[:, :, :, None]

    out = tsdata(runConfig.cfg2grid(config))
    out.uturb = utmp
    out.uprof = umn
    return out
