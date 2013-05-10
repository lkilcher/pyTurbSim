from base import *
from copy import deepcopy
import profModels as pm
import turbModels as tm

# To find inconsistencies between this and older versions of TurbSim search for:
# !!!VERSION_INCONSISTENCY

# !!!CHECKTHIS
# means I need to ensure that something is right.
# !!!FIXTHIS
# means I know I am doing something wrong.

# TODO:
#  - Debug changes to code in which defaults were moved from defaults.py to the models.
#       .Search for calls to 'InvalidConfig' and 'ConfigWarning'.
#       .Flesh-out which defaults (config-variables) go with which models.
#          ..Does this mean creating new base-class objects to be sub-classed?
#  - Debug spectral models.
#  - Reynolds stress!
#  - Write summary files (tsio.py).
#    (so they are fully self-contained).
#  - Write FF files (tsio.py).
#  - Write HubHeight files (tsio.py).
#  - Tower capabilities:
#      a) Add tower points to grid.
#      b) incorporate into turbModel.
#      c) Write tower points to files (tsio.py).
#  - GUI!
#  - Parallelize?
#  - Add KHtest functionality? (rgrep for '#KHTEST')
#  - Write 'events' (includes adding 'coherent events' to TS)

def run_main(tsconfig):
    """
    The primary TurbSim executor program.

    Returns the tsdata output object.
    """
    turbModel=buildModel(tsconfig)
    
    turbTimeSeries=calcTimeSeries(turbModel)

    return tsdata(turbModel.config,turbTimeSeries,turbModel.profModel._u)

def buildModel(tsconfig):
    """
    Produce the grid, profModel and turbModel objects based on *tsconfig*.
    """
    tsconfig.__original__=deepcopy(tsconfig)

    #print 'Building model.'
    # Initialize the random number generator before doing anything else.
    if not tsconfig.has_key('RandSeed') or tsconfig['RandSeed'] is None:
        tsconfig['RandSeed']=np.random.randint(1e6,1e18)
    np.random.seed(tsconfig['RandSeed'])
    
    grid=tsGrid(tsconfig['NumGrid_Y'],tsconfig['NumGrid_Z'],tsconfig['GridWidth'],tsconfig['GridHeight'],tsconfig['HubHt'])

    profModel=pm.getModel(tsconfig,grid)
    
    turbModel=tm.getModel(tsconfig,profModel)

    return turbModel

def calcTimeSeries(turbModel):
    """
    Compute the u,v,w, timeseries based on the provided turbulence model.

    This function (and its subroutines) does the bulk of the work of TurbSim.
    """
    ts=np.empty((3,turbModel.n_p,turbModel.n_t),dtype=ts_float,order='F')
    if tslib is not None:
        #print 'Using fortran method.'
        for idx,Sij in enumerate(turbModel):
            sp=tslib.veers84(Sij,turbModel.rand[idx],turbModel.n_p,turbModel.n_f,)
            ts[idx]=np.fft.irfft(sp)
    else:
        #print 'Using python method.'
        for idx,Sij in enumerate(turbModel.iter_full):
            ts[idx]=np.fft.irfft(Veers84(Sij,turbModel.rand[idx]))
    # Select only the time period requested, and reshape the array to 4-D (uvw,z,y,time)
    ts=turbModel.grid.reshape(ts[...,turbModel.i0_out:turbModel.i0_out+turbModel.n_t_out])/(turbModel.dt/turbModel.n_f)**0.5
    #print "Done with 'math'."
    return ts

def Veers84(Sij,X):
    """
    Paul Veers' method for computing timeseries from input spectra and cross-spectra.  Returns the timeseries at each point.

    Full Reference:
      

    Inputs: 
      Sij  - Input cross-spectra matrix for all points (Np,Np,Nf).
      X    - Random (phase) vector, shape = (Np,Nf,)
      
    """
    n_f=X.shape[-1]
    n_p=X.shape[0]
    H=np.zeros((n_p,n_p,n_f),dtype=ts_float)
    out=np.zeros((n_p,n_f+1),dtype=ts_complex)
    for ff in range(n_f):
        H[:,:,ff]=np.linalg.cholesky(Sij[:,:,ff])
    out[:,1:]=np.einsum('ijk,jk->ik',H,X)
    return out

