from base import np,tslib,ts_float,ts_complex,Veers84,gridProps,dbg
#from profModels import mBase as pm_mBase
from _version import __version__,__prog_name__,__version_date__
from io import bladed,aerodyn

# !!!VERSION_INCONSISTENCY
# inconsistency between this and older versions of TurbSim
# !!!CHECKTHIS
# means I need to ensure that something is right.
# !!!FIXTHIS
# means I know I am doing something wrong.
# !!!ADDDOC
# Means add documentation here

# TODO:
#  - Add ability to rotate mean velocity field (for a prof instance and a profModel).
#  - Still need to check nwtcup model. Otherwise all models seem to be working, except:
#     . Something is wrong with the iec coherence model.
#     . The defaults are wrong for the stress and coherence models (for NWTCUP and others?)
#  - DOCUMENTATION!!!
#  - Update these files and add them to the repository:
#    .turbModels/newModel_example.py
#    .turbModels/newCohereModel_example.py
#  - 'User-defined' models
#  - Add parameter logging, so that we can write summary files that track all parameters that were input.
#  - Write summary files (tsio.py), (so they are fully self-contained).
#  - Write FF files (tsio.py).
#  - Write HubHeight files (tsio.py).
#  X? GUI! 
#  - Parallelize?
#  - Add KHtest functionality? (rgrep for '#KHTEST')
#  - Write 'events' (includes adding 'coherent events' to TS)

class tsrun(object):
    """
    A TurbSim 'run' object.  
    """
    def __init__(self,RandSeed=None,ncore=0):
        # Initialize the random number generator before doing anything else.
        if RandSeed is None:
            self.RandSeed=np.random.randint(1e6,1e18)
        else:
            self.RandSeed=RandSeed
        self.randgen=np.random.RandomState(self.RandSeed)
        self.ncore=ncore
        if dbg:
            self.timer=dbg.timer('Veers84')
        
    def clear(self,):
        del self.prof
        del self.spec
        del self.cohere
        del self.stress
    
    def set_profModel(self,profModel):
        self.profModel=profModel

    def set_specModel(self,specModel):
        self.specModel=specModel

    def set_cohereModel(self,cohModel):
        self.cohereModel=cohModel

    def set_stressModel(self,stressModel):
        self.stressModel=stressModel
        
    @property
    def info(self,):
        out=dict()
        out['version']=(__prog_name__,__version__,__version_date__)
        out['RandSeed']=self.RandSeed
        for nm in ['profModel','specModel','cohereModel','stressModel']:
            if hasattr(self,nm):
                out[nm]=str(getattr(self,nm).__class__).rsplit(nm)[-1].rstrip("'>").lstrip('s.')
                out[nm+'_params']=getattr(self,nm).parameters
        return out
    
    def __call__(self,):
        if dbg:
            tmr=dbg.timer('Total CPU time')
            tmr.start()
        self.prof=self.profModel(self)
        self.spec=self.specModel(self)
        self.cohere=self.cohereModel(self)
        self.stress=self.stressModel(self)
        self.timeseries=self._calcTimeSeries()
        if dbg:
            tmr.stop()
            print tmr
            print self.timer
            print self.cohereModel.timer
        return self._build_outdata()

    run=__call__ # A more explicit shortcut...

    def _build_outdata(self,):
        out=tsdata(self.grid)
        out.uturb=self.timeseries
        out.uprof=self.prof.data
        out.info=self.info
        return out
        
    def _calcTimeSeries(self,):
        """
        Compute the u,v,w, timeseries based on the provided turbulence model.

        This function performs the work of taking a specified spectrum and coherence function and
        transforming it into a spatial timeseries.  It performs the steps outlined in Veers84's
        equations 7 and 8.

        References
        =================

        The full reference for 'Veers84' is:
           Veers, Paul (1984) 'Modeling Stochastic Wind Loads on Vertical Axis Wind Turbines',
           Sandia Report 1909, 17 pages.

        Notes
        =================

        1) Veers84's equation 7 is actually a 'Cholesky Factorization'.  Therefore, rather than
        writing this functionality explicitly we call 'cholesky' routines to do this work.
        
        2) This function uses one of two methods for computing the Cholesky factorization.  If
        the Fortran library tslib is available it is used (it is much more efficient), otherwise
        the numpy implementation of Cholesky is used.

        """
        grid=self.grid
        ts=np.empty((grid.n_comp,grid.n_p,grid.n_t),dtype=ts_float)
        phases=self.stress.calcPhases()
        for idx,Sij in enumerate(self.cohere):
            self.timer.start()
            ts[idx]=np.fft.irfft(Veers84(Sij,self.spec.flat[idx],phases[idx],self.ncore))
            self.timer.stop()
        # Select only the time period requested, and reshape the array to 4-D (uvw,z,y,time)
        i0_out=self.randgen.randint(grid.n_t-grid.n_t_out+1) # Grab a random number of where to cut the timeseries from.
        ts=grid.reshape(ts[...,i0_out:i0_out+grid.n_t_out])/(grid.dt/grid.n_f)**0.5
        ts-=ts.mean(-1)[...,None] # Make sure the turbulence has zero mean.
        return ts

class tsdata(gridProps):
    """
    A data object for TurbSim output.  It contains all information about the simulation.
    """

    @property
    def parameters(self,):
        out={}
        if hasattr(self,'info'):
            for nm in ['profModel_params','specModel_params','cohereModel_params','stressModel_params']:
                if self.info.has_key(nm):
                    out.update(self.info[nm])
        return out
                

    def __init__(self,grid):
        self.grid=grid

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
        return '<TurbSim data object:\n%d %4.2fs-timesteps, %0.2fx%0.2fm (%dx%d) z-y grid (hubheight=%0.2fm).>' % (self.uturb.shape[-1],self.dt,self.grid.height,self.grid.width,self.grid.n_z,self.grid.n_y,self.grid.zhub)

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

    def writeBladed(self,filename):
        bladed.write(filename,self)

    def writeAero(self,filename):
        aerodyn.write(filename,self)

    def writeSum(self,filename):
        # !!!FIXTHIS
        pass
    
