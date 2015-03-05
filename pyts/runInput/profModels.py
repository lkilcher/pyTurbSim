"""
This module contains functions for producing the appropriate profile
model for a specific TurbSim input object (derived from an input
file).

When a new model is added to the profModels package, it will need a
wrapper function here in order to be accessible using input files.

"""
from ..profModels import api as pm


def getModel(tsinput):
    """
    This is the wrapper function for all profile models implemented in
    the runInput package.

    Parameters
    ----------
    tsinput :  :class:`.tsinput`
                A TurbSim input object.

    Returns
    -------
    profModel : A subclass of :class:`.profModelBase`
                The appropriately initialized 'profile model' object
                specified in `tsinput`.

    """
    # This executes the sub-wrapper function (defined below) specified
    # in the tsinput-object (input file WINDPROFILETYPE line)
    return eval('_' + tsinput['WindProfileType'].lower() + '(tsinput)')


def _h2l(tsinput):
    """
    This function parses the correct variables from the tsinput
    object and supplies them to the 'H2O log' profile model.

    Parameters
    ----------
    tsinput :  :class:`.tsinput`
                A TurbSim input object (with WindProfileType 'h2l').

    Returns
    -------
    profModel : :class:`pyts.profModels.log.H2O`
                H2O-log mean profile model instance.

    """
    return pm.h2l(tsinput['URef'],
                  tsinput['RefHt'],
                  tsinput['UStar'])


def _log(tsinput):
    """
    This function parses the correct variables from the tsinput
    object and supplies them to the wind 'log' profile model.

    Parameters
    ----------
    tsinput :  :class:`.tsinput`
                A TurbSim input object (with WindProfileType 'log').

    Returns
    -------
    profModel : :class:`pyts.profModels.log.nwtc`
                wind log mean profile model instance.

    """
    return pm.log(tsinput['URef'],
                  tsinput['RefHt'],
                  tsinput['Z0'],
                  tsinput['RICH_NO'],
                  tsinput['TurbModel'])


def _pl(tsinput):
    """
    This function parses the correct variables from the tsinput
    object and supplies them to the wind 'power-law' profile model.

    Parameters
    ----------
    tsinput :  :class:`.tsinput`
                A TurbSim input object (with WindProfileType 'pl').

    Returns
    -------
    profModel : :class:`pyts.profModels.power.nwtc`
                power-law mean profile model instance.

    """
    return pm.pl(tsinput['URef'],
                 tsinput['RefHt'],
                 tsinput['PLExp'])


def _iec(tsinput):
    """
    This function parses the correct variables from the tsinput
    object and supplies them to the wind 'IEC' profile model.

    Parameters
    ----------
    tsinput :  :class:`.tsinput`
                A TurbSim input object (with WindProfileType 'IEC').

    Returns
    -------
    profModel : :class:`pyts.profModels.iec.main`
                IEC mean profile model instance.

    """
    return pm.iec(tsinput['URef'],
                  tsinput['RefHt'],
                  tsinput['Z0'],
                  tsinput['PLExp'],
                  tsinput['TurbModel'],)
