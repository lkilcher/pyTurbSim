import numpy as np
try:
    import tslib
except ImportError:
    print """
    ***Warning***: 'tslib' did not load correctly.  pyTurbSim
    will produce accurate results, but less efficiently. To improve
    performance recompile the library as decribed in the 'Building
    tslib' section of the README file.
    """
    tslib=None

from misc import lowPrimeFact_near,kappa

#tslib=None
prog={'name':'pyTurbSim',
      'ver':'0.2',
      'date':'Dec-13-2013',
      }

ts_float=np.float32
ts_complex=np.complex64

class tsarray(np.ndarray):
    pass
        
class gridProps(object):
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

class modelBase(gridProps):
    """
    A base class for all TurbSim models.
    """
    comp_name=['u','v','w']
    n_comp=len(comp_name)
    comp=range(n_comp)


class tsdata(gridProps):
    """
    A data object for TurbSim output.  It contains all information about the simulation.
    """

    def __init__(self,turbModel,uturb=None,uprof=None):
        self.turbModel=turbModel
        self.grid=turbModel.grid
        if uturb is not None:
            # Make sure the turbulence component has zero mean.
            self.uturb=uturb-uturb.mean(-1)[...,None]
        if uprof is not None:
            self.uprof=uprof

    @property
    def shape(self,):
        """
        The shape of the turbulence time-series (output) array.
        """
        return self.uturb.shape

    @property
    def ihub(self,):
        """
        The index of the hub.
        """
        return self.grid.ihub

    @property
    def time(self,):
        """
        The time vector, in seconds, starting at zero.
        """
        if not hasattr(self,'_time'):
            self._time=np.arange(0,self.uturb.shape[-1]*self.dt,self.dt)
        return self._time


    def __repr__(self,):
        return '<TurbSim data object: %s spectral model.\n%d %4.2fs-timesteps, %0.2fx%0.2fm (%dx%d) z-y grid (hubheight=%0.2fm).>' % (self.turbModel.__class__, self.uturb.shape[-1],self.dt,self.grid.height,self.grid.width,self.grid.n_z,self.grid.n_y,self.grid.zhub)

    @property
    def utotal(self,):
        """
        The total (mean + turbulent), 3-d velocity array
        """
        return self.uturb+self.uprof[:,:,:,None]

    @property
    def u(self,):
        """
        The total (mean + turbulent), u-component of velocity.
        """
        return self.uturb[0]+self.uprof[0,:,:,None]
    @property
    def v(self,):
        """
        The total (mean + turbulent), v-component of velocity.
        """
        return self.uturb[1]+self.uprof[1,:,:,None]
    @property
    def w(self,):
        """
        The total (mean + turbulent), w-component of velocity.
        """
        return self.uturb[2]+self.uprof[2,:,:,None]

    @property
    def UHUB(self,):
        """
        The hub-height mean velocity.
        """
        return self.uprof[0][self.ihub]
    
    @property
    def uhub(self,):
        """
        The hub-height u-component time-series.
        """
        return self.u[self.ihub]
    @property
    def vhub(self,):
        """
        The hub-height v-component time-series.
        """
        return self.v[self.ihub]
    @property
    def whub(self,):
        """
        The hub-height w-component time-series.
        """
        return self.w[self.ihub]

    @property
    def tke(self,):
        """
        The turbulence kinetic energy.
        """
        return (self.uturb**2).mean(-1)

    @property
    def Ti(self,):
        """
        The turbulence intensity, std(u')/U, at each point in the grid.
        """
        return np.std(self.uturb[0],axis=-1)/self.uprof[0]

    @property
    def upvp_(self,):
        """
        Returns the u'v' component of the Reynold's stress.
        """
        return np.mean(self.uturb[0]*self.uturb[1],axis=-1)

    @property
    def upwp_(self,):
        """
        Returns the u'w' component of the Reynold's stress.
        """
        return np.mean(self.uturb[0]*self.uturb[2],axis=-1)

    @property
    def vpwp_(self,):
        """
        Returns the v'w' component of the Reynold's stress.
        """
        return np.mean(self.uturb[1]*self.uturb[2],axis=-1)

    @property
    def stats(self,):
        """
        Compute and return relevant statistics for this turbsim time-series.
        """
        slc=[slice(None)]+list(self.ihub)
        stats={}
        stats['Ti']=self.tke[slc]/self.UHUB
        return stats

def getGrid(tsconfig):
    return tsGrid(tsconfig['HubHt'],ny=tsconfig['NumGrid_Y'],nz=tsconfig['NumGrid_Z'],width=tsconfig['GridWidth'],height=tsconfig['GridHeight'],time_sec=tsconfig['AnalysisTime'],time_sec_out=tsconfig['UsableTime'],dt=tsconfig['TimeStep'],RandSeed=tsconfig['RandSeed'],clockwise=tsconfig['Clockwise'])

class tsGrid(object):
    """
    A TurbSim grid object.  The grid is defined so that the first row is the bottom, and the last is the top.
    """
    def __init__(self,center=None,ny=None,nz=None,width=None,height=None,dy=None,dz=None,nt=None,time_sec=None,time_min=None,dt=None,time_sec_out=None,findClose_nt_lowPrimeFactors=True,prime_max=31,RandSeed=None,clockwise=True):
        """
        The TurbSim time-space grid object.

        Each grid dimension (x,y,time) can be specified by any combination of 2 inputs,
          for the x-grid, for example, you may specify:
              dx and nx, or width and dx, or width and nx.
        
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
        # Initialize the random number generator before doing anything else.
        if RandSeed is None:
            self.RandSeed=np.random.randint(1e6,1e18)
        else:
            self.RandSeed=RandSeed
        self.randgen=np.random.RandomState(self.RandSeed) # We may want to move this to a 'tsrun' object, if we create that. For now, we'll put it here.
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
        self.i0_out=self.randgen.randint(self.n_t-self.n_t_out+1) # Grab a random number of where to cut the timeseries from.

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
        return (self.n_z,self.n_y)

    @property
    def shape_wt(self,):
        """
        A shortcut to the grid shape, including the time dimension.
        """
        return (self.n_z,self.n_y,self.n_t)

    @property
    def shape_wf(self,):
        """
        A shortcut to the grid shape, including the frequency dimension.
        """
        return (self.n_z,self.n_y,self.n_f)

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
        Return the subscripts (iz,iy) corresponding to the `flattened' index *ind* (row-order) for this grid.
        """
        iz=ind/self.n_y
        if iz>self.n_z:
            raise IndexError('Index beyond range of grid.')
        iy=np.mod(ind,self.n_y)
        return (iz,iy)
    
    def sub2ind(self,subs):
        """
        Return the `flattened' index (row-order) corresponding to the subscript *subs* (iz,iy) for this grid.
        """
        return subs[0]*self.n_y+subs[1]

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
        return arr.reshape(shp,order='C')

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
        return arr.reshape(shp,order='C')

