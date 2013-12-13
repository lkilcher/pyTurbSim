from base import tsdata,tsGrid,np,tslib,ts_float,ts_complex
import profModels as pm
import turbModels as tm
from runConfig import buildModel

# To find inconsistencies between this and older versions of TurbSim search for:
# !!!VERSION_INCONSISTENCY

# !!!CHECKTHIS
# means I need to ensure that something is right.
# !!!FIXTHIS
# means I know I am doing something wrong.

# !!!ADDDOC
# Means add documentation here

# TODO:
#  - 'Object'-ify turbulence models.
#    . Only IEC models remain.
#  - Revamp this file to separate building models from config files from pythonic use.
#  - Remove all 'import *' statements.
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

def run_main(tsconfig):
    """
    The primary TurbSim executor program.

    Returns the tsdata output object.
    """
    turbModel=buildModel(tsconfig)
    
    turbTimeSeries=calcTimeSeries(turbModel)

    return tsdata(turbModel,turbTimeSeries,turbModel.profModel._u)

def calcTimeSeries(turbModel):
    """
    Compute the u,v,w, timeseries based on the provided turbulence model.

    This function performs the work of taking a specified spectrum and coherence function and
    transforming it into a spatial timeseries.  It performs the steps outlined in Veers84's
    equations 7 and 8.

    References
    =================

    The full reference of 'Veers84' is:
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
    grid=turbModel.grid
    ts=np.empty((3,grid.n_p,grid.n_t),dtype=ts_float,order='F')
    if hasattr(turbModel,'stressModel'):
        # Correlate the random phases between components to set the stress.
        turbModel.stressModel._setPhases()
    if tslib is not None:# and False:
        # This uses the fortran library to compute the Cholesky factorization.
        # This is much faster than the 'pure-python' method below.
        for idx,Sij in enumerate(turbModel.cohModel):
            sp=tslib.veers84(Sij,turbModel.rand[idx],grid.n_p,grid.n_f,)
            ts[idx]=np.fft.irfft(sp)
    else:
        # This is the pure-python method of computing the cholesky factorization.
        # Though it is slower, it is useful when there are issues compiling the Fortran libraries.
        for idx,Sij in enumerate(turbModel.cohModel.iter_full):
            ts[idx]=np.fft.irfft(Veers84(Sij,turbModel.rand[idx]))
    # Select only the time period requested, and reshape the array to 4-D (uvw,z,y,time)
    ts=grid.reshape(ts[...,grid.i0_out:grid.i0_out+grid.n_t_out])/(grid.dt/grid.n_f)**0.5
    return ts

def Veers84(Sij,X):
    """
    Paul Veers' method for computing timeseries from input spectra and cross-spectra.  Returns the timeseries at each point.

    Full Reference:
       Veers, Paul (1984) 'Modeling Stochastic Wind Loads on Vertical Axis Wind Turbines',
       Sandia Report 1909, 17 pages.

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

