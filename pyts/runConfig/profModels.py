"""
This module contains functions for producing the appropriate profile
model for a specific TurbSim config object (derived from an input
file).

When a new model is added to the profModels package, it will need a
wrapper function here in order to be accessible using input files.

"""
from ..profModels import api as pm


def getModel(tsconfig):
    """
    This is the wrapper function for all profile models implemented in
    the runConfig package.

    Parameters
    ----------
    tsconfig :  :class:`tscfg <.base.tscfg>`
                A TurbSim config object.

    Returns
    -------
    profModel : A subclass of :class:`profModelBase <pyts.profModels.mBase.profModelBase>`
                The appropriately initialized 'profile model' object
                specified in `tsconfig`.

    """
    # This executes the sub-wrapper function (defined below) specified
    # in the tsconfig-object (input file WINDPROFILETYPE line)
    return eval('_' + tsconfig['WindProfileType'].lower() + '(tsconfig)')


def _h2l(tsconfig):
    """
    This function parses the correct variables from the tsconfig
    object and supplies them to the 'H2O log' profile model.

    Parameters
    ----------
    tsconfig :  :class:`tscfg <.base.tscfg>`
                A TurbSim config object (with WindProfileType 'h2l').

    Returns
    -------
    profModel : :class:`pyts.profModels.log.H2O`
                H2O-log mean profile model instance.

    """
    return pm.h2l(tsconfig['URef'],
                  tsconfig['RefHt'],
                  tsconfig['UStar'])


def _log(tsconfig):
    """
    This function parses the correct variables from the tsconfig
    object and supplies them to the wind 'log' profile model.

    Parameters
    ----------
    tsconfig :  :class:`tscfg <.base.tscfg>`
                A TurbSim config object (with WindProfileType 'log').

    Returns
    -------
    profModel : :class:`pyts.profModels.log.nwtc`
                wind log mean profile model instance.

    """
    return pm.log(tsconfig['URef'],
                  tsconfig['RefHt'],
                  tsconfig['Z0'],
                  tsconfig['RICH_NO'],
                  tsconfig['TurbModel'])


def _pl(tsconfig):
    """
    This function parses the correct variables from the tsconfig
    object and supplies them to the wind 'power-law' profile model.

    Parameters
    ----------
    tsconfig :  :class:`tscfg <.base.tscfg>`
                A TurbSim config object (with WindProfileType 'pl').

    Returns
    -------
    profModel : :class:`pyts.profModels.power.nwtc`
                power-law mean profile model instance.

    """
    return pm.pl(tsconfig['URef'],
                 tsconfig['RefHt'],
                 tsconfig['PLExp'])


def _iec(tsconfig):
    """
    This function parses the correct variables from the tsconfig
    object and supplies them to the wind 'IEC' profile model.

    Parameters
    ----------
    tsconfig :  :class:`tscfg <.base.tscfg>`
                A TurbSim config object (with WindProfileType 'IEC').

    Returns
    -------
    profModel : :class:`pyts.profModels.iec.main`
                IEC mean profile model instance.

    """
    return pm.iec(tsconfig['URef'],
                  tsconfig['RefHt'],
                  tsconfig['Z0'],
                  tsconfig['PLExp'],
                  tsconfig['TurbModel'],)
