from struct import unpack
from .base import e
import numpy as np
from ..main import tsdata
from ..base import tsGrid


def bladed(fname,):
    """
    Read Bladed format (.wnd, .bl) full-field time-series binary data files.

    Parameters
    ----------
    fname : str
            The filename from which to read the data.

    Returns
    -------
    tsdata : :class:`tsdata <pyts.main.tsdata>`
             The TurbSim data contained in the binary data file.

    """
    with file(fname, 'rb') as fl:
        junk, nffc, ncomp, lat, z0, center = unpack(e + '2hl3f', fl.read(20))
        if junk != -99 or nffc != 4:
            raise IOError("The file %s does not appear to be a valid 'bladed (.bts)' format file."
                          % fname)
        ti = np.array(unpack(e + '3f', fl.read(12))) / 100
        dz, dy, dx, n_f, uhub = unpack(e + '3flf', fl.read(20))
        n_t = int(2 * n_f)
        fl.seek(12, 1)  # Unused bytes
        clockwise, randseed, n_z, n_y = unpack(e + '4l', fl.read(16))
        fl.seek(24, 1)  # Unused bytes
        nbt = ncomp * n_y * n_z * n_t
        dat = np.rollaxis(np.fromstring(fl.read(2 * nbt), dtype=np.int16)
                          .astype(np.float32).reshape([ncomp,
                                                       n_y,
                                                       n_z,
                                                       n_t], order='F'),
                          2, 1)
    dat[0] += 1000.0 / ti[0]
    dat /= 1000. / (uhub * ti[:, None, None, None])
    # Create the grid object:
    dt = dx / uhub
    if clockwise == 0:
        # Not specified in the binary file, try reading a .sum file?
        # !!!MOREHERE read .sum?
        # else assume it's true:
        clockwise = True
    else:
        clockwise = bool(clockwise - 1)
    if clockwise:
        # flip the data back
        dat = dat[:, :, ::-1, :]
    # Create the tsdata object.
    grid = tsGrid(center=center,
                  ny=n_y, nz=n_z,
                  dy=dy, dz=dz,
                  dt=dt, nt=n_t,
                  clockwise=clockwise)
    out = tsdata(grid)
    out.uprof = dat.mean(-1)
    out.uturb = dat - out.uprof[:, :, :, None]
    return out


def turbsim(fname):
    """
    Read TurbSim format (.bts) full-field time-series binary
    data files.

    Parameters
    ----------
    fname : str
            The filename from which to read the data.

    Returns
    -------
    tsdata : :class:`tsdata <pyts.main.tsdata>`
             The TurbSim data contained in the binary data file.

    """
    u_scl = np.zeros(3, np.float32)
    u_off = np.zeros(3, np.float32)
    fl = file(fname, 'rb')
    (junk,
     n_z,
     n_y,
     n_tower,
     n_t,
     dz,
     dy,
     dt,
     uhub,
     zhub,
     z0,
     u_scl[0],
     u_off[0],
     u_scl[1],
     u_off[1],
     u_scl[2],
     u_off[2],
     strlen) = unpack(e + 'h4l12fl', fl.read(70))
    center = z0 + n_z * dz / 2.0
    #print fname, u_scl, u_off
    desc_str = fl.read(strlen)  # skip these bytes.
    nbt = 3 * n_y * n_z * n_t
    dat = np.rollaxis(np.fromstring(fl.read(2 * nbt), dtype=np.int16).astype(
        np.float32).reshape([3, n_y, n_z, n_t], order='F'), 2, 1)[:, ::-1]
    dat -= u_off[:, None, None, None]
    dat /= u_scl[:, None, None, None]
    # Create the tsdata object.
    grid = tsGrid(center=center,
                  ny=n_y, nz=n_z,
                  dy=dy, dz=dz,
                  dt=dt, nt=n_t, )
    out = tsdata(grid)
    out.uprof = dat.mean(-1)
    out.uturb = dat - out.uprof[:, :, :, None]
    return out
