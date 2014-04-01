"""
This module brings together the main components of the TurbSim program
and defines the primary high-level objects that users of the Python
interface will utilize.

This module, however, contains more functions and objects than the
typical user will want access to. For a more compact version of the
PyTurbSim interface import the ./api.py package.

"""
from base import np,tslib,ts_float,ts_complex,gridProps,dbg,modelBase
from profModels.mBase import profModelBase,profObj
from specModels.mBase import specModelBase,specObj
from cohereModels.mBase import cohereModelBase,cohereObj,cohereUser
from stressModels.mBase import stressModelBase,stressObj
from phaseModels.api import randPhase
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
#  - Add ability to add veer to mean velocity field (prof instance and profModel).
#  - DOCUMENTATION!!!
#  - Update these files and add them to the repository:
#    .turbModels/newModel_example.py
#    .turbModels/newCohereModel_example.py
#  - 'User-defined' models
#  - Add parameter logging, so that we can write summary files that track all parameters that were input.
#  - Write .sum summary files (tsio.py), (so they are fully self-contained).
#  - Write FF files (tsio.py).
#  - Write HubHeight files (tsio.py).
#  - Add KHtest functionality? (rgrep for '#KHTEST')
#  - Write 'events' (includes adding 'coherent events' to TS)

class tsrun(object):
    """
    This is the PyTurbSim 'run' class. This class provides the
    interface for controlling PyTurbSim simulations and output.

    Examples of how to use this class, and the PyTurbSim interface in
    general can be found in the PyTurbSim /examples directory.

    """
    def __init__(self,RandSeed=None,ncore=1):
        """
        PyTurbSim 'run' objects can be initialized with a specific
        random seed, *RandSeed*, and number of cores, *ncore*.
        """
        # Initialize the random number generator before doing anything else.
        if RandSeed is None:
            self.RandSeed=np.random.randint(-2147483648,2147483647)
        else:
            self.RandSeed=RandSeed
        # Seeds for numpy must be positive, but original-TurbSim had negative seeds.
        # In order to attempt to be consistent, we use the values in the files but make them positive for the numpy random generator.
        self.randgen=np.random.RandomState(self.RandSeed+2147483648)
        self.ncore=ncore
        if dbg:
            self.timer=dbg.timer('Veers84')

    phase=randPhase() # For now this is a place-holder, I may want to make this an 'input property' eventually.

    @property
    def prof(self):
        """
        This is the 'mean velocity profile' input property. This
        property can be defined with three types of objects:
          1) define it with a 'profile model' (recommended), e.g.:
          
                  ts_run.prof=a_prof_model
            
             In this case the model is set to my_ts_run.profModel, and
             this model is called to produce a profObj AS NEEDED.  At
             the end of the ts_run call that profObj is cleared so
             that subsequent runs do not use a fixed profObj (i.e. in
             the case that the model is modified or another
             model/object that the profile model depends on is
             changed between runs).

          2) define it with a profObj directly (profile
             statistic-object), e.g.:

              ts_run.prof=a_prof_model(ts_run)
              
             In this case the profObj is FIXED. That is, all
             subsequent PyTurbSim runs will utilize this profile,
             which is based on the state of the a_prof_model and
             ts_run at the time of the profObj creation.

          3) define it with an array directly, e.g.:

               ts_run.prof=a_numpy_array   [units: m/s]

             In this case the profObj is again fixed and defined by
             the input array.  The numpy array dimensions must match
             those of the tsGrid.  That is, the dimensions of the
             array should be (3 x grid.n_z x grid.n_y).  The first
             dimension is for each component of the profile (u,v,w),
             the next two are for each point (z,y) in the grid.
        
        This property always returns a 'profObj' object or raises an
        AttributeError.  

        See Also
        --------
        Other input properties:
          tsrun.spec
          tsrun.cohere
          tsrun.stress

        the 'profModels' package for a list of available profile
        models and more detailed documentation.
        
        """
        if hasattr(self,'profModel') and not hasattr(self,'_prof'):
            self._prof=self.profModel(self)
        return self._prof
    @prof.setter
    def prof(self,val):
        if profModelBase in val.__class__.__mro__:
            self.profModel=val
        elif np.ndarray in val.__class__.__mro__:
            self._prof=profObj(self)
            self._prof.array[:]=val
        elif profObj in val.__class__.__mro__:
            self._prof=val
        else:
            raise Exception('The input must be a profile model, profile object or numpy array; it is none of these.')
    @prof.deleter
    def prof(self,):
        if hasattr(self,'profModel'):
            del self._prof

    @property
    def spec(self):
        """
        This is the 'tke spectrum' input property. This property can
        be defined with three types of objects:
          1) define it with a 'spectral model' (recommended), e.g.:
          
                  ts_run.spec=a_spec_model
            
             In this case the model is set to my_ts_run.specModel, and
             this model is called to produce a specObj AS NEEDED.  At
             the end of the ts_run call that specObj is cleared so
             that subsequent runs do not use a fixed specObj (i.e. in
             the case that another model/object that the spectral model
             depends on is changed between runs).

          2) define it with a specObj directly, e.g.:

              ts_run.spec=a_spec_model(ts_run)
              
             In this case the specObj is FIXED. That is, all
             subsequent PyTurbSim runs will utilize this spectral
             model, which is based on the state of ts_run at the time
             of the specObj creation.

          3) define it with an array directly, e.g.:

               ts_run.spec=a_numpy_array  - [units: m^2/(s^2.Hz)]

             In this case the specObj is again fixed and defined by
             the input array.  The numpy array dimensions must match
             those of the tsGrid.  That is, the dimensions of the
             array should be (3 x grid.n_z x grid.n_y x grid.n_f).
             The first dimension is for each component of the spectrum
             (u,v,w), the next two are for each point (z,y) in the
             grid, and the last dimension is the frequency dependence
             of the spectrum.

        This property always returns a 'specObj' object or raises an
        AttributeError.

        See Also
        --------
        Other input properties:
          tsrun.prof
          tsrun.cohere
          tsrun.stress

        'specModels' package for a list of available spectral
        models and more detailed documentation.
        
        """
        if hasattr(self,'specModel') and not hasattr(self,'_spec'):
            self._spec=self.specModel(self)
        return self._spec
    @spec.setter
    def spec(self,val):
        if specModelBase in val.__class__.__mro__:
            self.specModel=val
        elif np.ndarray in val.__class__.__mro__:
            self._spec=specObj(self)
            self._spec.array[:]=val
        elif specObj in val.__class__.__mro__:
            self._spec=val
        else:
            raise Exception('The input must be a spectral model, spectra object or numpy array; it is none of these.')
    @spec.deleter
    def spec(self,):
        if hasattr(self,'specModel'):
            del self._spec
    
    @property
    def cohere(self):
        """
        This is the 'coherence' input property.

        Because the bulk of PyTurbSim's computational requirements
        (memory and processor time) are consumed by dealing with this
        statistic, it behaves somewhat differently from the others. In
        particular, rather than relying on arrays for holding data
        'coherence objects' define functions that are called as
        needed.  This dramatically reduces the memory requirements of
        PyTurbSim without increasing.  See the cohereModels package
        documentation for further details.  Fortunately, at this
        level, coherence is specified identically to other
        statistics...

        This property can be defined with three types of objects:
          1) define it with a 'coherence model' (recommended), e.g.:
          
                  ts_run.cohere=a_coherence_model
            
             In this case the model is set to my_ts_run.cohereModel,
             and this model sets the is called at runtime to produce the phase
             array. At the end of the ts_run call that phase array is
             cleared so that subsequent runs do not use a fixed
             phase information (i.e. in the case that the coherence
             model is modified or another model/object that the
             coherence model depends on is changed between runs).

          2) define it with a cohereObj directly, e.g.:

              ts_run.spec=a_coherence_model(ts_run)
              
             In this case the cohereObj is FIXED. That is, all
             subsequent PyTurbSim runs will utilize this coherence
             model, which is based on the state of ts_run at the time
             of execution of this command.

          3) define it with an array directly, e.g.:

               ts_run.cohere=a_numpy_array  - [units: non-dimensional]

             In this case the coherence will be fixed and defined by
             this input array.  The numpy array dimensions must match
             those of the tsGrid.  That is, the dimensions of the
             array should be (3 x grid.n_p x grid.n_p x grid.n_f).
             The first dimension is for each component of the spectrum
             (u,v,w), the next two are for each point-pair (z,y) in the
             grid, and the last dimension is the frequency dependence
             of the spectrum.

             This approach for specifying the coherence - while
             explicit and flexible - requires considerably more memory
             than the 'coherence model' approach.  Furthermore using
             this approach one must be careful to make sure that the
             ordering of the array agrees with that of the 'flattened
             grid' (see the tsGrid.flatten method, and/or the
             cohereUser coherence model for more information).

        This property always returns a 'cohereObj' object or raises an
        AttributeError (if a coherence model is not defined).

        See Also
        --------
        Other input properties:
          tsrun.prof
          tsrun.spec
          tsrun.stress

        the 'cohereModels' package for a list of available coherence
        models and more detailed documentation.

        'cohereUser' coherence model (in the cohereModels/mBase.py
        file)

        """
        if hasattr(self,'cohereModel') and not hasattr(self,'_cohere'):
            self._cohere=self.cohereModel(self)
        return self._cohere
    @cohere.setter
    def cohere(self,val):
        if cohereModelBase in val.__class__.__mro__:
            self.cohereModel=val
        elif np.ndarray in val.__class__.__mro__:
            self.cohereModel=cohereUser(val)
        elif cohereObj in val.__class__.__mro__:
            self.cohere=val
        else:
            raise Exception('The input must be a coherence model, coherence object or numpy array; it is none of these.')
    @cohere.deleter
    def cohere(self,):
        if hasattr(self,'cohereModel'):
            del self._cohere

    @property
    def stress(self):
        """
        This is the Reynold's stress input property. This property can
        be defined with three types of objects:
          1) define it with a 'spectral model' (recommended), e.g.:
          
                  ts_run.stress=a_stress_model
            
             In this case the model is set to my_ts_run.stressModel, and
             this model is called to produce a stressObj AS NEEDED.  At
             the end of the ts_run call that stressObj is cleared so
             that subsequent runs do not use a fixed stressObj (i.e. in
             the case that another model/object that the stress model
             depends on is changed between runs).

          2) define it with a stressObj directly, e.g.:

              ts_run.stress=a_stress_model(ts_run)
              
             In this case the stressObj is FIXED. That is, all
             subsequent PyTurbSim runs will utilize this stress
             model, which is based on the state of ts_run at the time
             of the stressObj creation.

          3) define it with an array directly, e.g.:

               ts_run.stress=a_numpy_array  - [units: m^2/s^2]

             In this case the stressObj is again fixed and defined by
             the input array.  The numpy array dimensions must match
             those of the tsGrid.  That is, the dimensions of the
             array should be (3 x grid.n_z x grid.n_y).
             The first dimension is for each component of the stress
             (u,v,w), the next two are for each point (z,y) in the
             grid.

        This property always returns a 'stressObj' object or raises an
        AttributeError (if no stressModel is defined).

        See Also
        --------
        Other input properties:
          tsrun.prof
          tsrun.spec
          tsrun.cohere

        'stressModels' package for a list of available stress models
        and more detailed documentation.
        
        """
        if hasattr(self,'stressModel') and not hasattr(self,'_stress'):
            self._stress=self.stressModel(self)
        return self._stress
    @stress.setter
    def stress(self,val):
        if stressModelBase in val.__class__.__mro__:
            self.stressModel=val
        elif np.ndarray in val.__class__.__mro__:
            self._stress=stressObj(self)
            self._stress.array[:]=val
        elif stressObj in val.__class__.__mro__:
            self._stress=val
        else:
            raise Exception('The input must be a stress model, stress object or numpy array; it is none of these.')
    @stress.deleter
    def stress(self,):
        if hasattr(self,'stressModel'):
            del self._stress

    def reset(self,seed=None):
        """
        Clear the input statistics and reset the Random Number
        generator to its initial state.
        """
        del self.prof
        del self.spec
        del self.cohere
        del self.stress
        if RandSeed is None:
            self.randgen.seed(self.RandSeed)
        
    @property
    def info(self,):
        """
        Model names and initialization parameters.
        """
        out=dict()
        out['version']=(__prog_name__,__version__,__version_date__)
        out['RandSeed']=self.RandSeed
        for nm in ['profModel','specModel','cohereModel','stressModel']:
            if hasattr(self,nm):
                out[nm]=str(getattr(self,nm).__class__).rsplit(nm)[-1].rstrip("'>").lstrip('s.')
                out[nm+'_params']=getattr(self,nm).parameters
        return out
    
    def __call__(self,):
        """
        Run PyTurbSim.

        Before calling this method be sure that the following
        properties of this run-object have been set to the desired
        values:
        prof   - The mean profile model, object or array.
        spec   - The tke spectrum model, object or array.
        cohere - The coherence model, object or array.
        stress - The Reynold's stress model, object or array.

        Returns
        -------
        PyTurbSim tsdata object.
        
        """
        if dbg:
            tmr=dbg.timer('Total CPU time')
            tmr.start()
        self.timeseries=self._calcTimeSeries()
        if dbg:
            tmr.stop()
            print tmr
            print self.timer
            print self.cohereModel.timer
        out=self._build_outdata()
        self.clear()
        return out

    run=__call__ # A more explicit shortcut...

    def _build_outdata(self,):
        """
        Construct the output data object and return it.
        """
        out=tsdata(self.grid)
        out.uturb=self.timeseries
        out.uprof=self.prof.array
        out.info=self.info
        return out
        
    def _calcTimeSeries(self,):
        """
        Compute the u,v,w, timeseries based on the spectral, coherence
        and Reynold's stress models.
        
        This method performs the work of taking a specified spectrum
        and coherence function and transforming it into a spatial
        timeseries.  It performs the steps outlined in Veers84's
        equations 7 and 8.

        Returns
        -------
        turb - the turbulent velocity timeseries array (3 x nz x ny x
               nt) for this PyTurbSim run.


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
        tmp=np.zeros((grid.n_comp,grid.n_z,grid.n_y,grid.n_f+1),dtype=ts_complex)
        if dbg:
            self.timer.start()
        # First calculate the 'base' set of random phases:
        phases=self.phase(self)
        # Now correlate the phases at each point to set the Reynold's stress:
        phases=self.stress.calc_phases(phases)
        # Now correlate the phases between points to set the spatial coherence:
        phases=self.cohere.calc_phases(phases)
        # Now multiply the phases by the spectrum...
        tmp[...,1:]=np.sqrt(self.spec.array)*grid.reshape(phases)
        # and compute the inverse fft to produce the timeseries:
        ts=np.fft.irfft(tmp)
        if dbg:
            self.timer.stop()
        # Select only the time period requested:
        i0_out=self.randgen.randint(grid.n_t-grid.n_t_out+1) # Grab a random number of where to cut the timeseries.
        ts=ts[...,i0_out:i0_out+grid.n_t_out]/(grid.dt/grid.n_f)**0.5
        ts-=ts.mean(-1)[...,None] # Make sure the turbulence has zero mean.
        return ts

class tsdata(gridProps):
    """
    TurbSim output data object.  In addition to the output of a
    simulation (velocity timeseries array) it also includes all
    information for reproducing the simulation.
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
        """
        Initialize a tdata object with a grid object.
        """
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
        """
        Save the data in this tsdata object in 'bladed' format.
        
        Parameters
        ----------
        *filename*  - The filename to which the data should be written.
        
        """
        bladed.write(filename,self)

    def writeAero(self,filename):
        """
        Save the data in this tsdata object in 'AeroDyn' format.

        Parameters
        ----------
        *filename*  - The filename to which the data should be written.
        """
        aerodyn.write(filename,self)

    def writeSum(self,filename):
        """
        Currently PyTurbSim does not support writing summary (.sum) files.
        """
        #!!!FIXTHIS!!!
        pass
    
