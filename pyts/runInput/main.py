"""
The 'main' module for the PyTurbSim runInput package defines the
'run' and 'write' routines for performing a TurbSim run and
writing-out data.

Example usage
-------------

First import the PyTurbSim api and runInput package.
>>> import pyts.api as pyts
>>> import pyts.runInput as runInput

First create a tsinput object from an input file using the io.input.read function:

>>> tsinput=pyts.io.input.read('MyInputFile.inp')

Now run PyTurbSim using the runInput 'run' function:

>>> tsdata=runInput.run(tsinput)

This data can be written to the files specified in the input file
(tsinput) using:

>>> runInput.write(tsdata,tsinput)

"""
from ..base import tsGrid
from ..main import tsrun
from ..io.input import read as readInput
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
    inp = readInput(fname)
    return run(inp)


def run(tsinput):
    """Perform a PyTurbSim run based on the input object `tsinput`.

    Parameters
    ----------
    tsinput :  :class:`.tsinput`
                A PyTurbSim input object.

    Returns
    -------
    tsdata :    :class:`.tsdata`
                A PyTurbSim data object.
    """
    tsr = cfg2tsrun(tsinput)

    return tsr()


def write(tsdat, tsinput, fname=None):
    """
    Write TurbSim-output to a file.

    Parameters
    ----------
    tsdat :     :class:`.tsdata`
                The PyTurbSim data object to write out.
    tsinput :  :class:`.tsinput`
                A PyTurbSim input object.
    fname :     str, optional
                The filename to writeout (default obtained from `tsinput`)

    This function determines which file-types to writeout (bladed or
    TurbSim) from the `tsinput` object
    """
    if fname is None:
        fname = tsinput.fname
    if tsinput['WrBLFF']:
        tsdat.write_bladed(fname)
    if tsinput['WrADFF']:
        tsdat.write_turbsim(fname)
    tsdat.write_sum(fname)


def cfg2grid(tsinput):
    """
    cfg2grid produces a TurbSim-grid object that matches the
    specificitions in the *tsinput* object.

    Parameters
    ----------
    tsinput :  :class:`tscfg <.base.tscfg>`
                A PyTurbSim input object.

    Returns
    -------
    tsgrid :    :class:`tsGrid <pyts.base.tsGrid>`
                A PyTurbSim grid object.

    """
    return tsGrid(tsinput['HubHt'],
                  ny=tsinput['NumGrid_Y'], nz=tsinput['NumGrid_Z'],
                  dt=tsinput['TimeStep'],
                  width=tsinput['GridWidth'], height=tsinput['GridHeight'],
                  time_sec=tsinput['AnalysisTime'],
                  time_sec_out=(tsinput['UsableTime'] + tsinput['GridWidth']
                                / tsinput['URef']),
                  clockwise=tsinput['Clockwise'])


def cfg2tsrun(tsinput):
    """
    Produce a `tsrun` object that matches the configuration options in
    tsinput.

    Parameters
    ----------
    tsinput :  str
                A TurbSim input object.

    Returns
    -------
    tsrun :     str
                A TurbSim run object with grid, profModel, specModel,
                cohereModel and stressModel that match the input
                `tsinput` object.

    """

    tsr = tsrun(tsinput['RandSeed'])

    tsr.grid = cfg2grid(tsinput)

    tsr.profModel = pm_getModel(tsinput)

    tsr.specModel, tsr.cohereModel, tsr.stressModel = tm_getModel(tsinput)

    # Store this for use when writing sum files.
    tsr._config = tsinput

    return tsr
