"""
This module is for reading/writing PyTurbSim data objects to
Bladed (Trademark: GL Garrad-Hassan) format binary files.

The functions in this module were translated directly from the
original TSsubs.f90 file.
"""
from .base import convname
import numpy as np
from struct import pack, unpack
from .base import e


def write(fname, tsdat):
    """
    Write the data to a Bladed-format (.wnd) binary file.


    Parameters
    ----------
    fname : str
            The filename to which the data should be written.
    tsdat : :class:`tsdata <pyts.main.tsdata>`
            A TurbSim data object.

    """
    prms = tsdat.parameters
    lat = prms.get('Latitude', 0.0)
    Z0 = prms.get('Z0', 0.0)
    ts = tsdat.utotal
    ti = np.sqrt(tsdat.tke[:, tsdat.ihub[0], tsdat.ihub[1]]) / tsdat.UHUB
    ti[ti < 1e-5] = 1
    scale = 1000. / (tsdat.UHUB * ti[:, None, None, None])
    off = np.array([1000. / (ti[0]), 0, 0])[:, None, None, None]
    fl = file(convname(fname, '.wnd'), 'wb')
    # First write some setup data:
    fl.write(
        pack(e + '2hl3f', -99, 4, 3, lat, Z0, tsdat.grid.z[0] + tsdat.grid.height / 2.0))
    # Now write the turbulence intensity, grid spacing, numsteps, and hub mean wind speed
    # For some reason this takes half the number of timesteps...
    fl.write(pack(e + '3f', *(100 * ti)))
    fl.write(pack(e + '3flf', tsdat.grid.dz, tsdat.grid.dy,
             tsdat.UHUB * tsdat.dt, tsdat.shape[-1] / 2, tsdat.UHUB))
    fl.write(pack(e + '3fl', *([0] * 4)))  # Unused bytes
    fl.write(
        pack(e + '3l', tsdat.info['RandSeed'], tsdat.grid.n_z, tsdat.grid.n_y))
    fl.write(pack(e + '6l', *([0] * 6)))  # Unused bytes
    if tsdat.grid.clockwise:
        out = (ts[:,:, ::-1,:]*scale-off).astype(np.int16)
    else:
        out = (ts * scale - off).astype(np.int16)
    # Swap the y and z indices so that fortran-order writing agrees with the
    # file format.
    out = np.rollaxis(out, 2, 1)
    # Write the data so that the first index varies fastest (F order).
    # With the swap of y and z indices above, the indexes vary in the following
    # (decreasing) order:
    # component (fastest), y-index, z-index, time (slowest).
    fl.write(out.tostring(order='F'))
    #fl.write(out.tostring(order='F'))
    fl.close()


def read(fname,):
    """
    Read Bladed format (.wnd, .bl) full-field time-series binary data files.

    Parameters
    ----------
    fname : str
            The filename from which to read the data.

    Returns
    -------
    tsdat : array_like
            An array of the TurbSim-simulated turbulence data.

    """
    ## !!!FIXTHIS, this should return a tsData object:
    ## *tsdat*  - A tsdata object that contains the data.
    with file(fname, 'rb') as fl:
        junk, nffc, ncomp, lat, z0, zoff = unpack(e + '2hl3f', fl.read(20))
        if junk != -99 or nffc != 4:
            error
        ti = np.array(unpack(e + '3f', fl.read(12))) / 100
        dz, dy, dx, n_f, uhub = unpack(e + '3flf', fl.read(20))
        n_t = int(2 * n_f)
        fl.seek(16, 1)  # Unused bytes
        randseed, n_z, n_y = unpack(e + '3l', fl.read(12))
        fl.seek(24, 1)  # Unused bytes
        nbt = ncomp * n_y * n_z * n_t
        dat = np.rollaxis(np.fromstring(fl.read(2 * nbt), dtype=np.int16).astype(
            np.float32).reshape([ncomp, n_y, n_z, n_t], order='F'), 2, 1)
    dat[0] += 1000.0 / ti[0]
    dat /= 1000. / (uhub * ti[:, None, None, None])
    return dat
