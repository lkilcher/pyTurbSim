# !!!ADDDOC
import numpy as np
from misc import lowPrimeFact_near
from os import path
try:
    from tslib import tslib
except ImportError:
    print """
    ***Warning***: 'tslib' did not load correctly.  pyTurbSim
    will produce accurate results, but less efficiently. To improve
    performance recompile the library as decribed in the 'Building
    tslib' section of the README file.
    """
    tslib=None

dbg=None
import dbg

tsroot=path.realpath(__file__).replace("\\","/").rsplit('/',1)[0]+'/'
userroot=path.expanduser('~')

ts_float=np.float32
ts_complex=np.complex64
#ts_float={'dtype':np.float32,'order':'F'}
#ts_complex={'dtype':np.complex64,'order':'F'}

class tsBaseObj(object):
    """
    An abstract, base object, that contains the component (u,v,w) information for derived classes.
    """
    comp_name=['u','v','w']
    n_comp=len(comp_name)
    comp=range(n_comp)

class calcObj(tsBaseObj):
    """
    
    """
    _alias0=['u','v','w']

    def __getitem__(self,ind):
        if ind in self._alias0:
            ind=self._alias0.index(ind)
        if hasattr(self,'_alias1') and ind in self._alias1:
            ind=self._alias1.index(ind)
        return self.data[ind]

    def __setitem__(self,ind,val):
        if ind in self._alias0:
            ind=self._alias0.index(ind)
        if hasattr(self,'_alias1') and ind in self._alias1:
            ind=self._alias1.index(ind)
        self.data[ind]=val


class gridProps(tsBaseObj):
    """
    A list of shortcuts for objects that have the grid as one of their attributes.
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
    

class tsGrid(tsBaseObj):
    """
    A TurbSim 'grid' object.
    
    The grid is defined so that the first row is the bottom, and the last is the top.
    """

    def __init__(self,center=None,ny=None,nz=None,width=None,height=None,dy=None,dz=None,nt=None,time_sec=None,time_min=None,dt=None,time_sec_out=None,findClose_nt_lowPrimeFactors=True,prime_max=31,RandSeed=None,clockwise=True):
        """
        Initialize the TurbSim time-space grid object.

        Each grid dimension (x,y,time) can be specified by any combination of 2 inputs,
          for the x-grid, for example, you may specify:
              dx and nx, or width and dx, or width and nx.

        Input Parameters
        ----------------
        
        Spatial dimension inputs (in meters):
          center       - height of the center of the grid.
          ny,nz        - number of points in the y and z directions.
          width,height - total width and height of grid.
          dy,dx        - spacing between points in the y and z directions (subordinate to ny,nz and width,height).
          
        Time dimension inputs:
          nt           - number of timesteps
          time_sec     - length of run (seconds)
          time_min     - length of run (minutes, subordinate to time_sec)
          dt           - timestep (seconds, subordinate to nt and time_sec)
          time_sec_out - length of output timeseries (seconds, defaults to time_sec)

        Other inputs:
          findClose_nt_lowPrimeFactors - Adjust nfft to be a multiple of low primes (True or False, default: True).
          prime_max    - The maximum prime number allowed as a 'low prime'.
          RandSeed     - Specify a random seed for the random number generator (default: generate a random one).
          clockwise    - Should the simulation write a 'clockwise' rotation output file (True or False, default: True).
                         This is only used when writing 'Bladed' output files.
          
        """
        if center is None:
            raise TypeError("tsGrid objects require that the height of the grid center (input parameter 'center') be specified.")
        self.n_y,self.width,self.dy=self._parse_inputs(ny,width,dy)
        self.n_z,self.height,self.dz=self._parse_inputs(nz,height,dz)
        if time_sec is None:
            time_sec=time_min*60.
        if time_sec_out is None:
            time_sec_out=time_sec
        else:
            time_sec=max(time_sec_out,time_sec)
        self.n_t,self.time_sec,self.dt=self._parse_inputs(nt,time_sec,dt,plus_one=0)
        self.n_t_out,self.time_sec_out,junk=self._parse_inputs(None,time_sec_out,self.dt,plus_one=0)
        if findClose_nt_lowPrimeFactors:
            self.n_t=lowPrimeFact_near(self.n_t,nmin=self.n_t_out,pmax=prime_max)
            self.n_t,self.time_sec,junk=self._parse_inputs(self.n_t,None,self.dt,plus_one=0)
        self.df=1./self.time_sec
        self.n_f=self.n_t/2
        self.f=np.arange(self.n_f,dtype=ts_float)*self.df+self.df  # !!!CHECKTHIS
        self.n_p=self.n_y*self.n_z
        self._zdata=center+np.arange(self.height/2,-(self.height/2+self.dz/10),-self.dz,dtype=ts_float)
        self._ydata=np.arange(-self.width/2,self.width/2+self.dy/10,self.dy,dtype=ts_float)
        self.ihub=(self.n_z/2,self.n_y/2)
        self.tower=False
        self.clockwise=clockwise
        self.n_tower=0 # A place holder, we need to add this later.

    def __repr__(self,):
        return '<TurbSim Grid:%5.1fm high x %0.1fm wide grid  (%d x %d points), centered at %0.1fm.\n              %5.1fsec simulation, dt=%0.1fsec (%d timesteps).>' % (self.height,self.width,self.n_z,self.n_y,self.zhub,self.time_sec,self.dt,self.n_t)

    def _parse_inputs(self,n,l,d,plus_one=1):
        if (n is None)+(l is None)+(d is None)>1:
            raise Exception('Invalid inputs to Grid Initialization.')
        if n is None:
            d=ts_float(d)
            n=int(l/d)+plus_one
            l=(n-plus_one)*d
        elif l is None:
            d=ts_float(d)
            l=(n-plus_one)*d
        else: # Always override d if the other two are specified.
            l=ts_float(l)
            d=l/(n-plus_one)
        return n,l,d

    @property
    def shape(self,):
        """
        A shortcut to the grid shape.
        """
        return [self.n_z,self.n_y]

    @property
    def shape_wf(self,):
        """
        A shortcut to the grid shape, including the frequency dimension.
        """
        return [self.n_z,self.n_y,self.n_f]
    @property
    def _shape(self,):
        return [self.n_comp,self.n_z,self.n_z]
    @property
    def _shape_wf(self,):
        return [self.n_comp,self.n_z,self.n_z,self.n_f]

    @property
    def z(self,):
        """
        Returns the y-position of the grid points.
        """
        return self._zdata
    
    @property
    def y(self,):
        """
        Returns the y-position of the grid points.
        """
        return self._ydata

    def dist(self,ii,jj):
        """
        Returns the distance between the points ii=(iz,iy) and jj=(jz,jy).
        """
        if not hasattr(ii,'__len__'):
            ii=self.ind2sub(ii)
        if not hasattr(jj,'__len__'):
            jj=self.ind2sub(jj)
        return np.sqrt((self._ydata[ii[1]]-self._ydata[jj[1]])**ts_float(2)+(self._zdata[ii[0]]-self._zdata[jj[0]])**ts_float(2))

    @property
    def zhub(self,):
        return self.z[self.ihub[0]]

    @property
    def rotor_diam(self,):
        return min(self.width,self.height)
    
    def ind2sub(self,ind):
        """
        Return the subscripts (iz,iy) corresponding to the `flattened' index *ind* (column-order) for this grid.
        """
        iy=ind/self.n_z
        if iy>=self.n_y:
            raise IndexError('Index beyond range of grid.')
        iz=np.mod(ind,self.n_z)
        return (iz,iy)
    
    def sub2ind(self,subs):
        """
        Return the `flattened' index (column-order) corresponding to the subscript *subs* (iz,iy) for this grid.
        """
        return subs[1]*self.n_z+subs[0]

    def flatten(self,arr):
        """
        Reshape an array so that the z-y grid points are one-dimension of the array (for Cholesky factorization).
        """
        if arr.ndim>2 and arr.shape[0]==3 and arr.shape[1]==self.n_z and arr.shape[2]==self.n_y:
            shp=[3,self.n_p]+list(arr.shape[3:])
        elif arr.shape[0]==self.n_z and arr.shape[1]==self.n_y:
            shp=[self.n_p]+list(arr.shape[2:])
        else:
            raise ValueError('The array shape does not match this grid.')
        return arr.reshape(shp,order='F')

    def reshape(self,arr):
        """
        Reshape the array *arr* so that its z-y grid points are two-dimensions of the array (after Cholesky factorization).
        """
        if arr.shape[0]==3 and arr.shape[1]==self.n_p:
            shp=[3,self.n_z,self.n_y]+list(arr.shape[2:])
        elif arr.shape[0]==self.n_p:
            shp=[self.n_z,self.n_y]+list(arr.shape[1:])
        else:
            raise ValueError('The array shape does not match this grid.')
        return arr.reshape(shp,order='F')


class modelBase(tsBaseObj):
    """
    An abstract base class for all TurbSim models.
    """
    
    @property
    def parameters(self,):
        return dict(self.__dict__)


def Veers84(Sij,Sii,X,ncore=1):
    """
    Paul Veers' method for computing timeseries from input spectra and cross-spectra.  Returns the spectrum, ready for irfft.

    Full Reference:
       Veers, Paul (1984) 'Modeling Stochastic Wind Loads on Vertical Axis Wind Turbines',
       Sandia Report 1909, 17 pages.

    Inputs: 
      Sij  - Input cross-spectra matrix for all points (Np,Np,Nf).
      X    - Random (phase) vector, shape = (Np,Nf,)

    Notes
    =================

    1) Veers84's equation 7 is actually a 'Cholesky Factorization'.  Therefore, rather than
    writing this functionality explicitly we call 'cholesky' routines to do this work.

    2) This function uses one of two methods for computing the Cholesky factorization.  If
    the Fortran library tslib is available it is used (it is much more efficient), otherwise
    the numpy implementation of Cholesky is used.
    
    """
    n_f=X.shape[-1]
    n_p=X.shape[0]
    out=np.zeros((n_p,n_f+1),dtype=ts_complex,order='F')
    if tslib is not None:
        tslib.veers84(out[:,1:],Sij,X,ncore,n_p,n_f)
        out[:,1:]*=np.sqrt(Sii)
        return out
    H=np.zeros((n_p,n_p,n_f),dtype=ts_float)
    for ff in range(n_f):
        H[:,:,ff]=np.linalg.cholesky(Sij[:,:,ff])
    out[:,1:]=np.einsum('ijk,jk->ik',H,X)
    return out

#ts_float=np.float32
#ts_complex=np.complex64

def empty(shape,view=None):
    arr=np.empty(shape,dtype=ts_float)
    if view is None:
        return arr
    return arr.view(view)

## class tsarray(np.ndarray,gridProps):

##     def __new__(cls,dim_names,grid,buffer=None,offset=0,strides=None,dtype=ts_float['dtype'],order=ts_float['order']):
##         shape=[]
##         for nm in dim_names:
##             shape.append(getattr(grid,'n_'+nm))
##         obj=super(tsarray,cls).__new__(cls,shape,buffer=buffer,offset=offset,srides=strides,dtype=dtype,order=order)
##         obj.grid=grid
##         return obj
        
##     def __array_finalize__(self,obj):

##         if obj is None:
##             return
##         self.grid=getattr(obj,'grid',None)
        


## class tsarray(np.ndarray):
        
## class tsarray_complex(np.ndarray):
##     def __new__(cls,*args,**kwargs):
##         kwargs['order']='F'
##         kwargs['dtype']=ts_complex
##         return super(tsarray,cls).__new__(cls,*args,**kwargs)
