"""
The 'main' module for the PyTurbSim runConfig package defines the
'run' and 'write' routines for performing a TurbSim run and
writing-out data.

Example usage
-------------

First import the PyTurbSim api and runConfig package.
>>> import pyts.api as pyts
>>> import pyts.runConfig as runConfig

First create a tsconfig object from an input file using the io.config.read function:

>>> tsconfig=pyts.io.config.read('MyInputFile.inp')

Now run PyTurbSim using the runConfig 'run' function:

>>> tsdata=runConfig.run(tsconfig)

This data can be written to the files specified in the input file
(tsconfig) using:

>>> runConfig.write(tsdata,tsconfig)

"""
from ..base import tsGrid
from ..main import tsrun
from ..io.config import read as readConfig
from turbModels import getModel as tm_getModel
from profModels import getModel as pm_getModel


def run_fname(fname):
    """
    Perform a PyTurbSim run based on the input file `fname`.

    Parameters
    ----------
    fname :  str
             A TurbSim input file.

    Returns
    -------
    tsdata :    :class:`tsdata <pyts.main.tsdata>`
                A PyTurbSim data object.
    """
    config = readConfig(fname)
    return run(config)


def run(tsconfig):
    """
    Perform a PyTurbSim run based on the input/config object *tsconfig*.

    Parameters
    ----------
    tsconfig :  :class:`tscfg <.base.tscfg>`
                A PyTurbSim config object.

    Returns
    -------
    tsdata :    :class:`tsdata <pyts.main.tsdata>`
                A PyTurbSim data object.
    """
    tsr = cfg2tsrun(tsconfig)

    return tsr()


def write(tsdat, tsconfig, fname=None):
    """
    Write TurbSim-output to a file.

    Parameters
    ----------
    tsdat :     :class:`tsdata <pyts.main.tsdata>`
                The PyTurbSim data object to write out.
    tsconfig :  :class:`tscfg <.base.tscfg>`
                A PyTurbSim config object.
    fname :     str, optional
                The filename to writeout (default obtained from `tsconfig`)

    This function determines which file-types to writeout (bladed or
    TurbSim) from the `tsconfig` object
    """
    if fname is None:
        fname = tsconfig.fname
    if tsconfig['WrBLFF']:
        tsdat.write_bladed(fname)
    if tsconfig['WrADFF']:
        tsdat.write_turbsim(fname)
    tsdat.write_sum(fname)


def cfg2grid(tsconfig):
    """
    cfg2grid produces a TurbSim-grid object that matches the
    specificitions in the *tsconfig* object.

    Parameters
    ----------
    tsconfig :  :class:`tscfg <.base.tscfg>`
                A PyTurbSim config object.

    Returns
    -------
    tsgrid :    :class:`tsGrid <pyts.base.tsGrid>`
                A PyTurbSim grid object.

    """
    return tsGrid(tsconfig['HubHt'],
                  ny=tsconfig['NumGrid_Y'], nz=tsconfig['NumGrid_Z'],
                  dt=tsconfig['TimeStep'],
                  width=tsconfig['GridWidth'], height=tsconfig['GridHeight'],
                  time_sec=tsconfig['AnalysisTime'],
                  time_sec_out=(tsconfig['UsableTime'] + tsconfig['GridWidth']
                                / tsconfig['URef']),
                  clockwise=tsconfig['Clockwise'])


def cfg2tsrun(tsconfig):
    """
    Produce a `tsrun` object that matches the configuration options in
    tsconfig.

    Parameters
    ----------
    tsconfig :  str
                A TurbSim config object.

    Returns
    -------
    tsrun :     str
                A TurbSim run object with grid, profModel, specModel,
                cohereModel and stressModel that match the input
                `tsconfig` object.

    """

    tsr = tsrun(tsconfig['RandSeed'])

    tsr.grid = cfg2grid(tsconfig)

    tsr.profModel = pm_getModel(tsconfig)

    tsr.specModel, tsr.cohereModel, tsr.stressModel = tm_getModel(tsconfig)

    # Store this for use when writing sum files.
    tsr._config = tsconfig

    return tsr
