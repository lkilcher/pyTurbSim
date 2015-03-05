"""
This is the main (top-level) io module. It defines the 'readModel'
function, which is useful for collecting information from available
TurbSim input/output files.
"""

import read

readers = {'wnd': read.bladed,
           'bl': read.bladed,
           'bts': read.turbsim, }


def readModel(fname, ):
    """
    Read a TurbSim data and input file and return a
    :class:`tsdata <pyts.main.tsdata>` data object.

    Parameters
    ----------
    fname : str
            The filename to load.
            If the file ends in:
              .bl or .wnd,  the file is assumed to be a bladed-format file.
              .bts, the file is assumed to be a TurbSim-format file.
    Returns
    -------
    tsdata : :class:`tsdata <pyts.main.tsdata>`
             The TurbSim data contained in the binary data file.
    """

    for sfx, rdr in readers.iteritems():
        if fname.endswith(sfx):
            return rdr(fname)

    # Otherwise try reading it as a .wnd file.
    read.bladed(fname)  # This will raise an error if it doesn't work.
