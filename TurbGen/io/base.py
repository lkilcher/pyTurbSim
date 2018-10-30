"""
A base module for the io package.
"""

# This defines the 'endianness' for reading/writing binary files in PyTurbSim.
e = '<'
from os.path import isfile


def convname(fname, extension=None):
    """
    Change the file extension.
    """
    if extension is None:
        return fname
    if extension != '' and not extension.startswith('.'):
        extension = '.' + extension
    return fname.rsplit('.', 1)[0] + extension


def checkname(fname, extensions=[]):
    """Test whether fname exists.

    If it does not, change the file extension in the list of
    extensions until a file is found. If no file is found this
    function raises IOError.
    """
    if isfile(fname):
        return fname
    if isinstance(extensions, basestring):
        # If extensions is a string make it a single-element list.
        extensions = [extensions]
    for e in extensions:
        fnm = convname(fname, e)
        if isfile(fnm):
            return fnm
    raise IOError("No such file or directory: '%s', and no "
                  "files found with specified extensions." % fname)
