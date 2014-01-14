# !!!ADDDOC
from ..base import tsGrid
from ..main import tsrun
from ..io.config import read as readConfig
from turbModels import getModel as tm_getModel
from profModels import getModel as pm_getModel

def run(tsconfig):
    # !!!ADDDOC
    
    tsr=cfg2tsrun(tsconfig)
    tsr.grid=cfg2grid(tsconfig)
    
    return tsr()

def write(tsdat,tsconfig,fname=None):
    # !!!ADDDOC
    """
    Write out the requested summary and binary files.
    """
    if fname is None:
        fname=tsconfig.fname
    if tsconfig['WrBLFF']:
        tsdat.writeBladed(fname)
    if tsconfig['WrADFF']:
        tsdat.writeAero(fname)

def cfg2grid(tsconfig):

    return tsGrid(tsconfig['HubHt'],ny=tsconfig['NumGrid_Y'],nz=tsconfig['NumGrid_Z'],width=tsconfig['GridWidth'],height=tsconfig['GridHeight'],time_sec=tsconfig['AnalysisTime'],time_sec_out=tsconfig['UsableTime']+tsconfig['GridWidth']/tsconfig['URef'],dt=tsconfig['TimeStep'],clockwise=tsconfig['Clockwise'])

def cfg2tsrun(tsconfig):
    """
    Produce a 'tsrun' object that matches the configuration options in *tsconfig*.

    Parameters
    ----------
    *tsconfig* - 
    """

    tsr=tsrun(tsconfig['RandSeed'])
    
    tsr.profModel=pm_getModel(tsconfig)

    tsr.specModel,tsr.cohereModel,tsr.stressModel=tm_getModel(tsconfig)

    return tsr

