"""
The 'main' module for the TurbGen runInput package defines the
'run' and 'write' routines for performing a TurbSim run and
writing-out data.

Example usage
-------------

First import the TurbGen api and runInput package.
>>> import TurbGen.api as tg
>>> import TurbGen.runInput as runInput

First create a tsinput object from an input file using the io.input.read function:

>>> tsinput=tg.io.input.read('MyInputFile.inp')

Now run TurbGen using the runInput 'run' function:

>>> tsdata=runInput.run(tsinput)

This data can be written to the files specified in the input file
(tsinput) using:

>>> runInput.write(tsdata,tsinput)

"""
from ..base import RectGrid
from ..main import TGrun
from ..io.input import read as readInput
from turbModels import getModel as tm_getModel
from profModels import getModel as pm_getModel


def run_fname(fname):
    """
    Perform a TurbGen run based on the input file `fname`.

    Parameters
    ----------
    fname :  str
             A TurbSim input file.

    Returns
    -------
    tsdata :    :class:`tsdata <TurbGen.main.tsdata>`
                A TurbGen data object.
    """
    inp = readInput(fname)
    return run(inp)


def run(tsinput):
    """Perform a TurbGen run based on the input object `tsinput`.

    Parameters
    ----------
    tsinput :  :class:`.tsinput`
                A TurbGen input object.

    Returns
    -------
    tsdata :    :class:`.tsdata`
                A TurbGen data object.
    """
    tgr = cfg2tgrun(tsinput)

    return tgr()


def write(tsdat, tsinput, fname=None):
    """
    Write TurbSim-output to a file.

    Parameters
    ----------
    tsdat :     :class:`.tsdata`
                The TurbGen data object to write out.
    tsinput :  :class:`.tsinput`
                A TurbGen input object.
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
    if tsinput['WrFMTFF']:
        tsdat.write_formatted(fname)
    tsdat.write_sum(fname)


def cfg2grid(tsinput):
    """
    cfg2grid produces a TurbSim-grid object that matches the
    specificitions in the *tsinput* object.

    Parameters
    ----------
    tsinput :  :class:`tscfg <.base.tscfg>`
                A TurbGen input object.

    Returns
    -------
    grid :    :class:`gridObj <TurbGen.base.gridObj>`
                A TurbGen grid object.

    """
    return RectGrid(tsinput['HubHt'],
                    ny=tsinput['NumGrid_Y'], nz=tsinput['NumGrid_Z'],
                    dt=tsinput['TimeStep'],
                    width=tsinput['GridWidth'], height=tsinput['GridHeight'],
                    time_sec=tsinput['AnalysisTime'],
                    time_sec_out=(tsinput['UsableTime'] + tsinput['GridWidth']
                                  / tsinput['URef']),
                    clockwise=tsinput['Clockwise'])


def cfg2tgrun(tsinput):
    """
    Produce a `tgrun` object that matches the configuration options in
    tsinput.

    Parameters
    ----------
    tsinput :  str
                A TurbSim input object.

    Returns
    -------
    tgrun :     str
                A TurbSim run object with grid, profModel, specModel,
                cohereModel and stressModel that match the input
                `tsinput` object.

    """

    tgr = TGrun(tsinput['RandSeed'])

    tgr.grid = cfg2grid(tsinput)

    tgr.profModel = pm_getModel(tsinput)

    tgr.specModel, tgr.cohereModel, tgr.stressModel = tm_getModel(tsinput)

    # Store this for use when writing sum files.
    tgr._config = tsinput

    return tgr
