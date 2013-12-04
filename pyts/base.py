import numpy as np # Because we'd be lost without it.
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

#tslib=None
prog={'name':'pyTurbSim',
      'ver':'0.1',
      'date':'June-16-2013',
      }

ts_float=np.float32
ts_complex=np.complex64

kappa=0.41 # Von-Karman's constant

def pfactor(n,pmax=31):
    primes=np.array([2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71])
    primes=primes[primes<=pmax]
    lst=set()
    for ip in primes:
        while np.mod(n,ip)==0:
            lst.add(ip)
            n/=ip
    if n!=1:
        lst.add(n)
    return np.sort(list(lst))

def lowPrimeFact_near(n,pmax=31,nmin=None,evens_only=True):
    if (np.array(pfactor(n,pmax))<pmax).all():
        return n
    if evens_only: # Only deal with evens.
        dl=2
        if np.mod(n,2)>0:
            n+=1
    else:
        dl=1
    lowval=None
    ih=n
    if nmin is not None:
        il=n-dl
        while il>nmin:
            if (np.array(pfactor(il,pmax))<pmax).all():
                return il
            elif (np.array(pfactor(ih,pmax))<pmax).all():
                return ih
            il-=dl
            ih+=dl
    while not (np.array(pfactor(ih,pmax))<pmax).all():
        ih+=dl
    return ih

class tsdata(object):
    """
    A data object for TurbSim output.  It contains all information about the simulation.
    """

    def __init__(self,tsconfig,uturb=None,uprof=None):
        self.config=tsconfig
        self.dt=tsconfig['TimeStep']
        self.grid=getGrid(tsconfig)
        self.z=self.grid.z
        self.y=self.grid.y
        if uturb is not None:
            self.uturb=uturb
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
        return '<TurbSim data object: %s spectral model.\n%d %4.2fs-timesteps, %0.2fx%0.2fm (%dx%d) z-y grid (hubheight=%0.2fm).>' % (self.config['TurbModel'], self.uturb.shape[-1],self.dt,self.grid.height,self.grid.width,self.grid.n_z,self.grid.n_y,self.grid.zhub)

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
    def stats(self,):
        """
        Compute and return relevant statistics for this turbsim time-series.
        """
        stats={}
        slc=[slice(None)]+list(self.ihub)
        stats['Ti']=np.std(self.uturb[slc],axis=-1)/self.uprof[slc][0]
        return stats

class tscfg(dict):
    """
    The TurbSim config object and 'global defaults' handler.

    Regarding global defaults:
    The '_dflt_...' functions define 'global' default definitions (used by multiple profModels and/or turbModels).  Other, model specific, defaults are defined in the model itself.
    """
    
    def __getitem__(self,key):
        """
        Gets the item *key* from the dictionary.

        If there is no value, or it is 'None', and there is a '_dflt_<key>' property, it uses this property to 'set the default'.

        Otherwise return *None*.
        """
        if key=='RandSeed':
            return self.randseed
        if not self.has_key(key) or dict.__getitem__(self,key) is None:
            if hasattr(self,'_dflt_'+key):
                self[key]=self.__getattribute__('_dflt_'+key)
                self._dict_isdefault[key]=2
                return dict.__getitem__(self,key)
            else:
                return None
        else:
            return dict.__getitem__(self,key)
        
    def __setitem__(self,key,val):
        if key=='RandSeed':
            self.randseed=val
        else:
            dict.__setitem__(self,key,val)

    def __init__(self,*args,**kwargs):
        self._dict_isdefault={}
        dict.__init__(self,*args,**kwargs)

    def isdefault(self,key):
        """
        Is the given variable a default?
        
        True  : The value is not specified and there is no '_dflt_...' function.
        2     : The value is defined by a '_dflt_...' function.
        False : The value is specified explicitly in the configuration.
        
        """
        if self[key] is None:
            return True
        if self._dict_isdefault.has_key(key):
            return self._dict_isdefault[key]
        else:
            return False

    @property
    def randseed(self,):
        tmpval=0
        if self.has_key('RandSeed1') and self['RandSeed1'] is not None:
            tmpval+=np.uint32(self['RandSeed1'])
        if self.has_key('RandSeed2') and self['RandSeed2'] is not None:
            tmpval+=np.uint32(self['RandSeed2'])<<32
        if tmpval==0:
            return None
        return tmpval

    @randseed.setter
    def randseed(self,val):
        if val is None:
            self['RandSeed1']=None
            self['RandSeed2']=None
        else:
            self['RandSeed1']=np.int32(val & 2**32-1)
            val2=np.int32(val>>32)
            if val2>0:
                self['RandSeed2']=val2
            else:
                self['RandSeed2']=None

    @property
    def _dflt_WindProfileType(self,):
        if self['TurbModel'].lower()=='gp_llj':
            return 'JET'
        elif self['TurbModel'].lower() in ['river','tidal']:
            return 'H2L'
        else:
            return 'IEC'

    # These are only called if the key is not in the dictionary:
    @property
    def _dflt_Z0(self,):
        return {'ieckai':0.03,
                'iecvkm':0.03,
                'smooth':0.01,
                'gp_llj':0.005,
                'nwtcup':0.021,
                'wf_upw':0.018,
                'wf_07d':0.064,
                'wf_14d':0.233,
                'tidal':0.1,
                'river':0.1
                }[self['TurbModel'].lower()]

    @property
    def _dflt_UStar(self,):
        if (not self.has_key('URef') or self['URef'] is None) and (not self.has_key('UStar') or self['UStar'] is None):
            raise InvalidConfig('Either URef or UStar must be defined in the input file.')
        mdl=self['TurbModel'].lower()
        if mdl=='smooth':
            ustar=ustar0
        elif mdl=='nwtcup':
            ustar=0.2716 + 0.7573*ustar0**1.2599
        elif mdl=='gp_llj':
            ustar=0.17454 + 0.72045*ustar0**1.36242
        elif mdl=='wf_upw':
            if self.zL<0:
                ustar=1.162*ustar0**0.66666
            else:
                ustar=0.911*ustar0**0.66666
        elif mdl in ['wf_07d','wf_14d']:
            if self.zL<0:
                ustar=1.484*ustar0**0.66666
            else:
                ustar=1.370*ustar0**0.66666
        elif mdl in ['tidal', 'river']:
            ustar=self['URef']*0.05
        return ustar

    @property
    def _dflt_Latitude(self,):
        return 45.0
    
    @property
    def _dflt_ZI(self,):
        if self['UStar']<self.ustar0:
            return 400*self['URef']/np.log(self['RefHt']/self['Z0'])
        else:
            return self['UStar']/(12*7.292116e-5*np.sin(np.pi/180*np.abs(self['Latitude'])))
    
    ### These are helper functions, not 'default input parameters':
    @property
    def ustar0(self,):
        return kappa*self['URef']/(np.log(self['RefHt']/self['Z0'])-self.psiM)
    
    @property
    def zL(self,):
        """
        *zL* is the Monin-Obhukov (M-O) stability parameter z/L, where L is the M-O length.
        
        zL>0 means stable conditions.
        
        This is the relationship between zL and Ri detailed in Businger etal, and used in TurbSim for models requiring it, except for NWTCUP and GP_LLJ.
        """
        if not hasattr(self,'_val_zL'):
            # !!!VERSION_INCONSISTENCY:
            #      This function needs to depend on the turbulence model.
            Ri=self['RICH_NO']
            if Ri<0:
                self._val_zL=Ri
            elif Ri<1.66666:
                self._val_zL=Ri/(1-5.*Ri)
            else:
                self._val_zL=1
        return self._val_zL

    @property
    def psiM(self,):
        if not hasattr(self,'_val_psiM'):
            if self.zL>=0:
                self._val_psiM = -5.0*min(self.zL,1.0)
            else:
                tmp=(1.-15.0*self.zL)**0.25
                self._val_psiM = -np.log(0.125*((1.0+tmp)**2*(1.0+tmp**2)))+2.0*np.arctan(tmp)-0.5*np.pi
        return self._val_psiM

class undefinedModel(Exception):
    """
    Exception raised by the baseModel classes.  Used to indicate that a model has not defined a necessary attribute.
    """
    def __init__(self,msg='Attribute undefined in model.'):
        self.msg=msg

class modelBase(object):
    """
    A base class for all TurbSim models.

    Default values of many input parameters -- used by the various models -- are defined here.
    """
    comp_name=['u','v','w']
    n_comp=len(comp_name)
    comp=range(n_comp)

    def initModel(self,tsConfig,profModel=None):
        """
        User-initialization method.

        This function only raises an error.  It should be overridden in each model's definition (subclass of modelBase).
        """
        raise undefinedModel()

    #Note: subclasses of modelBase create the self.config attribute (i.e. the classes defined in profModel.mBase and turbModel.mBase).
    @property
    def zL(self,):
        return self.config.zL
    
    @property
    def psiM(self,):
        return self.config.psiM

    @property
    def turbmodel(self,):
        return self.config['TurbModel'].lower()
    
    @property
    def Ri(self,):
        return self.config['RICH_NO']

    @property
    def HubHt(self,):
        return self.grid.zhub # This should be the same as self.config['HubHt']

    @property
    def RefHt(self,):
        return self.config['RefHt']
    
    @property
    def URef(self,):
        return self.config['URef']
    
    @property
    def UStar(self,):
        return self.config['UStar']

    @property
    def Z0(self,):
        return self.config['Z0']

def getGrid(tsconfig):
    return tsGrid(tsconfig['HubHt'],ny=tsconfig['NumGrid_Y'],nz=tsconfig['NumGrid_Z'],width=tsconfig['GridWidth'],height=tsconfig['GridHeight'],time_sec=tsconfig['AnalysisTime'],time_sec_out=tsconfig['UsableTime'],dt=tsconfig['TimeStep'],)

class tsGrid(object):
    """
    A TurbSim grid object.  The grid is defined so that the first row is the bottom, and the last is the top.
    """
    def __init__(self,center,ny=None,nz=None,width=None,height=None,dy=None,dz=None,nt=None,time_sec=None,time_min=None,dt=None,time_sec_out=None,findClose_nt_lowPrimeFactors=True,prime_max=31):
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
          findClose_nt_lowPrimeFactors - Adjust nfft to be a multiple of low primes (True or False).
          prime_max                    - The maximum prime number allowed as a 'low prime'
          
        """
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
            self.n_t,self.time_sec,junk=self._parse_inputs(self.n_t,None,self.dt)
        self.df=1./self.time_sec
        self.n_f=self.n_t/2
        self.f=np.arange(self.n_f,dtype=ts_float)*self.df+self.df  # !!!CHECKTHIS
        self.n_p=self.n_y*self.n_z
        self._zdata=center+np.arange(self.height/2,-(self.height/2+self.dz/10),-self.dz,dtype=ts_float)
        self._ydata=np.arange(-self.width/2,self.width/2+self.dy/10,self.dy,dtype=ts_float)
        self.ihub=(self.n_z/2,self.n_y/2)
        self.tower=False
        self.n_tower=0 # A place holder, we need to add this later.
        self.i0_out=np.random.randint(self.n_t-self.n_t_out+1) # Grab a random number of where to cut the timeseries from.

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
        if arr.shape[0]==3 and arr.shape[1]==self.n_z and arr.shape[2]==self.n_y:
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

def fix2range(vals,minval,maxval):
    """
    A helper function that sets the value of the array or number *vals* to
    fall within the range minval<=vals<=maxval.
    
    Values of *vals* outside the range are fixed to minval or maxval.
    """
    if not hasattr(vals,'__len__'):
        return max( min( vals,maxval),minval)
    vals[vals>maxval],vals[vals<minval]=maxval,minval
    return vals


class ConfigWarning(Warning):
    pass

class InvalidConfig(Exception):
    """
    Exception raised by the baseModel classes.  Used to indicate that a model has not defined a necessary attribute.
    """
    def __init__(self,msg='Invalid option specified in config file.'):
        self.msg=msg
