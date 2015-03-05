"""
This is the 'base' module for the PyTurbSim program.

This module:

 a) imports common numpy functions/methods (from pyts_numpy.py),

 b) defines the :class:`gridObj` class (and the :func:`tsGrid` helper
    function),

 c) imports the tslib Fortran module (if it is available) and

 d) Defines several abstract base classes.

"""
from . import pyts_numpy as np
from numpy import float32, complex64
from .misc import lowPrimeFact_near
from os import path
try:
    from .tslib import tslib  # The file tslib.so contains the module 'tslib'.
except ImportError:
    print """
    ***Warning***: 'tslib' did not load correctly.  pyTurbSim
    will produce accurate results, but MUCH less efficiently.
    Consider compiling the tslib to improve performance.
    """
    tslib = None

dbg = None
#import dbg

tsroot = path.realpath(__file__).replace("\\", "/").rsplit('/', 1)[0] + '/'
userroot = path.expanduser('~')

ts_float = float32
ts_complex = complex64
#ts_float={'dtype':np.float32,'order':'F'}
#ts_complex={'dtype':np.complex64,'order':'F'}


class statObj(float):

    def __new__(self, dat, ubar=None):
        return float.__new__(self, dat.mean())

    @property
    def mean(self):
        return self

    def __init__(self, dat, ubar=None):

        self.max = dat.max()
        self.min = dat.min()
        self.sigma = np.std(dat)
        if ubar is None:
            ubar = self.mean
        self.ti = (self.sigma / ubar) * 100

    def __repr__(self,):
        return '<statObj mean: %0.2f, min: %0.2f, max: %0.2f>' % (self.mean, self.min, self.max)


class tsBaseObj(object):

    """
    An abstract, base object, that contains the component (u,v,w)
    information for derived classes.
    """
    comp_name = ['u', 'v', 'w']
    n_comp = len(comp_name)
    comp = range(n_comp)


class calcObj(tsBaseObj):

    """
    This is a base class for objects that are have .array properties.
    It creates a shortcut for accessing the array through the getitem
    method.

    This is used in each of the model packages as a base-class for the
    output 'statistics' of that class. In other words: profObj,
    specObj, stressObj, and cohereObj all derive from this class.
    """
    _alias0 = ['u', 'v', 'w']

    def __getitem__(self, ind):
        if ind in self._alias0:
            ind = self._alias0.index(ind)
        if hasattr(self, '_alias1') and ind in self._alias1:
            ind = self._alias1.index(ind)
        return self.array[ind]

    def __setitem__(self, ind, val):
        if ind in self._alias0:
            ind = self._alias0.index(ind)
        if hasattr(self, '_alias1') and ind in self._alias1:
            ind = self._alias1.index(ind)
        self.array[ind] = val


class gridProps(tsBaseObj):

    """
    An abstract base class that provides shortcuts for objects that
    have the grid as one of their attributes.
    """

    @property
    def z(self,):
        return self.grid.z

    @property
    def y(self,):
        return self.grid.y

    @property
    def f(self,):
        return self.grid.f

    @property
    def n_p(self,):
        return self.grid.n_p

    @property
    def n_z(self,):
        return self.grid.n_z

    @property
    def n_y(self,):
        return self.grid.n_y

    @property
    def n_f(self,):
        return self.grid.n_f

    @property
    def dt(self,):
        return self.grid.dt


def _parse_inputs(n, l, d, plus_one=1):
    """
    Parse inputs that describe a grid dimension.

    Parameters
    ----------
    n : int
        The number of points in that dimension.
    l : float
        The total length of that dimension.
    d : float
        The spacing between points.
    plus_one : bool
        Specifies whether or not the number of points
        includes an endpoint, or not. This should be 1 for
        spatial inputs, and 0 for time inputs.

    Returns
    -------
    n : int
        number of points
    l : float
        length of dimension
    d : float
        delta between points

    Notes
    -----

    Any one of `n`,`l`,`d` may be 'None', in which case it is
    computed from the other two. If all three are specified the
    value of `d` is disregaurded and computed from `n` and `l`.

    """
    if (n is None) + (l is None) + (d is None) > 1:
        raise Exception('Invalid inputs to Grid Initialization.')
    if n is None:
        d = ts_float(d)
        n = int(l / d) + plus_one
        l = (n - plus_one) * d
    elif l is None:
        d = ts_float(d)
        l = (n - plus_one) * d
    else:  # Always override d if the other two are specified.
        l = ts_float(l)
        d = l / (n - plus_one)
    return n, l, d


def tsGrid(center=None, ny=None, nz=None,
           width=None, height=None, dy=None, dz=None,
           nt=None, time_sec=None, time_min=None, dt=None, time_sec_out=None,
           findClose_nt_lowPrimeFactors=True, prime_max=31,
           clockwise=True):
    """
    Create a TurbSim grid.

    Parameters
    ----------

    center       : float
        height of the center of the grid.
    ny, nz        : int, optional*
        number of points in the y and z directions.
    width,height : float, optional*
        total width and height of grid.
    dy, dz        : float, optional*
        spacing between points in the y and z directions.

    nt           : int, optional*
        number of timesteps
    time_sec     : float, optional*
        length of run (seconds)
    time_min     : float, optional*
        length of run (minutes, subordinate to time_sec)
    dt           : float, optional*
        timestep (seconds, subordinate to nt and time_sec)
    time_sec_out : float, optional (`time_sec`)
        length of output timeseries in seconds, must be >=`time_sec`

    findClose_nt_lowPrimeFactors : bool, optional (True)
        Adjust nfft to be a multiple of low primes?
    prime_max    : int, optional (31)
        The maximum prime number allowed as a 'low prime'.
    clockwise    : bool, optional (True)
        Should the simulation write a 'clockwise' rotation output file.
        This is only used when writing 'Bladed' output files.

    Notes
    -----

    * Each grid dimension (z,y,time) can be specified by any
      combination of 2 inputs. For the y-grid, for example, you
      may specify: dy and ny, or width and dy, or width and ny. If
      all three are specified, dy ignored and computed from ny and
      width.

    """
    out = gridObj()
    if center is None:
        raise TypeError(
            "tsGrid objects require that the height of the grid center \
            (input parameter 'center') be specified.")
    if time_sec is None and time_min is not None:
        time_sec = time_min * 60.
    if time_sec_out is None and time_sec is not None:
        time_sec_out = time_sec
    if not (time_sec_out is None or time_sec is None):
        time_sec = max(time_sec_out, time_sec)
    n_y, width, dy = _parse_inputs(ny, width, dy)
    n_z, height, dz = _parse_inputs(nz, height, dz)
    out.y = np.arange(-width / 2, width / 2 + dy / 10, dy, dtype=ts_float)
    out.z = center + np.arange(-height / 2,
                               height / 2 + dz / 10,
                               dz, dtype=ts_float)

    out.n_t, out.time_sec, out.dt = _parse_inputs(nt, time_sec, dt, plus_one=0)
    if time_sec_out is None:
        time_sec_out = out.time_sec
    (out.n_t_out,
     time_sec_out,
     junk) = _parse_inputs(None,
                           time_sec_out,
                           dt, plus_one=0)

    if findClose_nt_lowPrimeFactors:
        out.n_t = lowPrimeFact_near(out.n_t, nmin=out.n_t_out, pmax=prime_max)
        out.n_t, out.time_sec, junk = _parse_inputs(
            out.n_t, None, out.dt, plus_one=0)
    out.f = np.arange(out.n_f, dtype=ts_float) * out.df + out.df  # !!!CHECKTHIS
    return out


class gridObj(tsBaseObj):

    """
    The base 'grid' class.

    In general, functions should be used to construct the grid.

    Notes
    -----

    1) The grid is defined so that the first row is the bottom and the
       last is the top.

    2) Irregular grids are not yet supported.

    """
    clockwise = True
    n_tower = 0  # This is a placeholder.

    def __getitem__(self, ind):
        if hasattr(ind, '__len__'):
            if len(ind) == 1:
                iy = ind[0]
                iz = slice(None)
            elif len(ind) == 2:
                iy, iz = ind
            else:
                raise Exception(
                    "Indices for accessing grids must have len==1 or 2.")
        else:
            iy = ind
            iz = slice(None)
        out = type(self)()
        out.n_t = self.n_t
        out.n_t_out = self.n_t_out
        out.dt = self.dt
        out.f = self.f
        out.time_sec = self.time_sec
        out.y = self.y[iy]
        out.z = self.z[iz]
        return out

    def __repr__(self,):
        return ('<TurbSim Grid:%5.1fm high x %0.1fm wide grid  (%d x %d points)'
                ', centered at %0.1fm.\n              %5.1fsec simulation, dt=%0.1fsec '
                '(%d timesteps).>' % (self.height, self.width,
                                      self.n_z, self.n_y,
                                      self.zhub, self.time_sec,
                                      self.dt, self.n_t))

    @property
    def time_sec_out(self,):
        return self.dt * self.n_t_out

    @property
    def width(self,):
        return self.y[-1] - self.y[0]

    @property
    def height(self,):
        return self.z[-1] - self.z[0]

    @property
    def dz(self,):
        return self.height / (self.n_z - 1)

    @property
    def dy(self,):
        return self.width / (self.n_y - 1)

    @property
    def n_z(self):
        return len(self.z)

    @property
    def n_y(self):
        return len(self.y)

    @property
    def n_f(self,):
        return self.n_t / 2

    @property
    def df(self,):
        return 1. / self.time_sec

    @property
    def n_p(self,):
        return self.n_y * self.n_z

    @property
    def ihub(self,):
        return (self.n_z / 2, self.n_y / 2)

    @property
    def shape(self,):
        """
        The grid shape: (n_z, n_y).
        """
        return [self.n_z, self.n_y]

    @property
    def shape_wf(self,):
        """
        The grid shape, including frequency (n_z, n_y, n_f).
        """
        return [self.n_z, self.n_y, self.n_f]

    def dist(self, ii, jj):
        """
        Compute the distance between the points `ii` and `jj`.

        Parameters
        ----------
        ii : Index of first grid-point.
        jj : Index of second grid-point.

        Returns
        -------
        r : The distance between the two grid points.

        Notes
        -----
        Each input index can either be a grid-point pair (e.g. a tuple,
        indicating the grid-point, or a linear index such as would be
        returned by :attr:`sub2ind`).

        """
        if not hasattr(ii, '__len__'):
            ii = self.ind2sub(ii)
        if not hasattr(jj, '__len__'):
            jj = self.ind2sub(jj)
        return np.sqrt((self.y[ii[1]] - self.y[jj[1]]) ** ts_float(2) +
                       (self.z[ii[0]] - self.z[jj[0]]) ** ts_float(2))

    @property
    def zhub(self,):
        """
        The height of the hub.
        """
        return self.z[self.ihub[0]]

    @property
    def rotor_diam(self,):
        """
        Return the min of the grid width and height.

        This is how TurbSim quantifies rotor diameter.
        """
        return min(self.width, self.height)

    ## def ind2sub(self,ind):
    ##     """
    ##     Return the subscripts (iz,iy) corresponding to the
    ##     `flattened' index *ind* (column-order) for this grid.
    ##     """
    ##     iy=ind/self.n_z
    ##     if iy>=self.n_y:
    ##         raise IndexError('Index beyond range of grid.')
    ##     iz=np.mod(ind,self.n_z)
    ##     return (iz,iy)

    ## def sub2ind(self,subs):
    ##     """
    ##     Return the `flattened' index (column-order) corresponding
    ##     to the subscript *subs* (iz,iy) for this grid.
    ##     """
    ##     return subs[1]*self.n_z+subs[0]

    ## def flatten(self,arr):
    ##     """
    ##     Reshape an array so that the z-y grid points are
    ##     one-dimension of the array (for Cholesky factorization).
    ##     """
    ##     if arr.ndim>2 and arr.shape[0]==3 and
    ##     arr.shape[1]==self.n_z and arr.shape[2]==self.n_y:
    ##         shp=[3,self.n_p]+list(arr.shape[3:])
    ##     elif arr.shape[0]==self.n_z and arr.shape[1]==self.n_y:
    ##         shp=[self.n_p]+list(arr.shape[2:])
    ##     else:
    ##         raise ValueError('The array shape does not match this grid.')
    ##     return arr.reshape(shp,order='F')

    ## def reshape(self,arr):
    ##     """
    ##     Reshape the array *arr* so that its z-y grid points are
    ##     two-dimensions of the array (after Cholesky factorization).
    ##     """
    ##     if arr.shape[0]==3 and arr.shape[1]==self.n_p:
    ##         shp=[3,self.n_z,self.n_y]+list(arr.shape[2:])
    ##     elif arr.shape[0]==self.n_p:
    ##         shp=[self.n_z,self.n_y]+list(arr.shape[1:])
    ##     else:
    ##         raise ValueError('The array shape does not match this grid.')
    ##     return arr.reshape(shp,order='F')

    def ind2sub(self, ind):
        """
        Return the subscripts (iz,iy) corresponding to the 'flattened'
        index `ind` (row/C-order) for this grid.
        """
        iz = ind / self.n_y
        if iz >= self.n_z:
            raise IndexError('Index beyond range of grid.')
        iy = np.mod(ind, self.n_y)
        return (iz, iy)

    def sub2ind(self, subs):
        """
        Return the 'flattened' index (row/C-order) corresponding to
        the subscript `subs` (iz,iy) for this grid.
        """
        if subs[0] < 0:
            subs = (self.n_z + subs[0], subs[1])
        if subs[1] < 0:
            subs = (subs[0], self.n_y + subs[1])
        return subs[0] * self.n_y + subs[1]

    def flatten(self, arr):
        """
        Reshape `arr` so that the z-y grid points are one-dimension
        of the array (e.g. prior to Cholesky factorization).
        """
        if (
           arr.ndim > 2 and
           arr.shape[0] == 3 and
           arr.shape[1] == self.n_z and
           arr.shape[2] == self.n_y
           ):
            shp = [3, self.n_p] + list(arr.shape[3:])
        elif arr.shape[0] == self.n_z and arr.shape[1] == self.n_y:
            shp = [self.n_p] + list(arr.shape[2:])
        else:
            raise ValueError('The array shape does not match this grid.')
        return arr.reshape(shp, order='C')

    def reshape(self, arr):
        """
        Reshape `arr` so that its z-y grid points are two-dimensions
        of the array.
        """
        if arr.shape[0] == 3 and arr.shape[1] == self.n_p:
            shp = [3, self.n_z, self.n_y] + list(arr.shape[2:])
        elif arr.shape[0] == self.n_p:
            shp = [self.n_z, self.n_y] + list(arr.shape[1:])
        else:
            raise ValueError('The array shape does not match this grid.')
        return arr.reshape(shp, order='C')


class modelBase(tsBaseObj):

    """
    An abstract base class for all TurbSim models.
    """

    @property
    def model_name(self,):
        """The model name is the class definition name"""
        return str(self.__class__).rsplit('.', 1)[-1].rstrip("'>")

    @property
    def model_desc(self,):
        """The model description is the first line of the docstring."""
        return self.__doc__.splitlines()[0].rstrip('.')

    @property
    def parameters(self,):
        """
        This property stores information about the TurbSim model
        initialization variables, for writing to summary files.

        This functionality is not yet implemented, and this is a
        placeholder for now.
        """
        return dict(self.__dict__)

    def _sumfile_string(self, tsrun, ):
        return "## No '_sumfile_string' defined for %s ##\n" % (str(self.__class__))
