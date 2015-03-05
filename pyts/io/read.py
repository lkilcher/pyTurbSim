from struct import unpack
from .base import e, checkname, convname
import numpy as np
from ..main import tsdata
from ..base import tsGrid
from warnings import warn


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
    fname = checkname(fname, ['.wnd', '.bl'])
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
    # Determine the clockwise value.
    if clockwise == 0:
        try:
            d = sum_scan(convname(fname, '.sum'))
            clockwise = d['clockwise']
        except IOError:
            warn("Value of 'CLOCKWISE' not specified in binary file, "
                 "and no .sum file found. Assuming CLOCKWISE = True.")
            clockwise = True
        except KeyError:
            warn("Value of 'CLOCKWISE' not specified in binary file, "
                 "and %s has no line containing 'clockwise'. Assuming "
                 "CLOCKWISE = True." % convname(fname, '.sum'))
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
    fname = checkname(fname, ['.bts'])
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


def sum_scan(filename,):
    """
    Scan a sum file for specific variables.

    Parameters
    ----------
    filename : string
        The file to scan.

    Returns
    -------
    out : dict
        A dictionary of values identified.
    """
    # Currently this routine only searches for 'clockwise'.
    out = dict()
    with open(checkname(filename, ['.sum', '.SUM']), 'r') as infl:
        for ln in infl:
            ln = ln.lower()
            if 'clockwise' in ln.lower():
                v = ln.split()[0]
                if v in ['t', 'y']:
                    out['clockwise'] = True
                else:
                    out['clockwise'] = False
    return out
