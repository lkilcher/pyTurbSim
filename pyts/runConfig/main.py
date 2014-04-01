"""
The 'main' module for the PyTurbSim runConfig package defines the
'run' and 'write' routines for performing a TurbSim run and
writing-out data.

Example usage
-------------

# First create a tsconfig object using the io.config.read function:
tsconfig=pyts.io.config.read('MyInputFile.inp')

# Now run PyTurbSim using the runConfig 'run' function:
tsdata=runConfig.run(tsconfig)

# This data can be written to the files specified in the input file
# (tsconfig) using:
runConfig.write(tsdata,tsconfig)

"""
from ..base import tsGrid
from ..main import tsrun
from ..io.config import read as readConfig
from turbModels import getModel as tm_getModel
from profModels import getModel as pm_getModel

def run(tsconfig):
    """
    Perform a PyTurbSim run based on the input/config object *tsconfig*.

    Returns
    -------
    A PyTurbSim data object.
    """
    tsr=cfg2tsrun(tsconfig)
    tsr.grid=cfg2grid(tsconfig)
    
    return tsr()

def write(tsdat,tsconfig,fname=None):
    """
    Write the data in the TurbSim data object *tsdat* to summary and
    binary files specified in the tsconfig object.
    """
    if fname is None:
        fname=tsconfig.fname
    if tsconfig['WrBLFF']:
        tsdat.writeBladed(fname)
    if tsconfig['WrADFF']:
        tsdat.writeAero(fname)

def cfg2grid(tsconfig):
    """
    cfg2grid produces a TurbSim-grid object that matches the
    specificitions in the *tsconfig* object.

    Parameters
    ----------
    tsconfig  - A TurbSim config object.

    Returns
    -------
    tsgrid   - A TurbSim grid object.
    
    """
    return tsGrid(tsconfig['HubHt'],ny=tsconfig['NumGrid_Y'],nz=tsconfig['NumGrid_Z'],width=tsconfig['GridWidth'],height=tsconfig['GridHeight'],time_sec=tsconfig['AnalysisTime'],time_sec_out=tsconfig['UsableTime']+tsconfig['GridWidth']/tsconfig['URef'],dt=tsconfig['TimeStep'],clockwise=tsconfig['Clockwise'])

def cfg2tsrun(tsconfig):
    """
    Produce a 'tsrun' object that matches the configuration options in *tsconfig*.

    Parameters
    ----------
    *tsconfig* - A TurbSim config object.

    Returns
    -------
    *tsrun* - A TurbSim run object with profModel, specModel,
              cohereModel and stressModel consistent with the input
              *tsconfig* object.

    """

    tsr=tsrun(tsconfig['RandSeed'])
    
    tsr.profModel=pm_getModel(tsconfig)

    tsr.specModel,tsr.cohereModel,tsr.stressModel=tm_getModel(tsconfig)

    return tsr

