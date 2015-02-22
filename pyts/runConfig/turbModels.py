"""
This module contains functions for producing the appropriate turbulence
model for a specific TurbSim config object (derived from an input
file).

The term 'TurbModels' encompasses the 'specModel', 'cohereModel' and
'stressModel' functionalities of the PyTurbSim program.  Within the
'runConfig' package all three of these statistics are handled in this
module.  Thus, each wrapper function for a 'TurbModel' should should
specify/define a model for each of these statistics.

More information on the specific TurbModels can be found in the
corresponding package for the statistic of interest.

To make a new specModel, cohereModel, or stressModel available from
input files add a wrapper function for it here.

"""
from ..specModels import api as sm
from ..cohereModels import api as cm
from ..stressModels import api as rm


def getModel(tsconfig):
    """
    This is the wrapper function for all turbulence models implemented
    in the runConfig package.

    Parameters
    ----------
    tsconfig :  :class:`tscfg <.base.tscfg>`
                A TurbSim config object.

    Returns
    -------
    specModel :         A subclass of :class:`.specModelBase`
                        The appropriately initialized 'spectral model' object
                        specified in `tsconfig`.
    cohereModel :       A subclass of :class:`.cohereModelBase`
                        The appropriately initialized 'coherence model' object
                        specified in `tsconfig`.
    stressModel :       A subclass of :class:`.stressModelBase`
                        The appropriately initialized 'stress model' object
                        specified in `tsconfig`.

    """
    # This executes the sub-wrapper function (defined below) specified
    # in the tsconfig-object (input file TurbModel line)
    return eval('_' + tsconfig['TurbModel'].lower() + '(tsconfig)')


def _tidal(tsconfig):
    smodel = sm.tidal(tsconfig['UStar'], tsconfig['RefHt'])
    cmodel = cm.nwtc(tsconfig.incdec_a, tsconfig.incdec_b, tsconfig['CohExp'])
    rmodel = rm.tidal(tsconfig['UStar'], tsconfig['RefHt'])
    return smodel, cmodel, rmodel


def _river(tsconfig):
    smodel = sm.river(tsconfig['UStar'],
                      tsconfig['RefHt'])
    cmodel = cm.nwtc(tsconfig.incdec_a,
                     tsconfig.incdec_b,
                     tsconfig['CohExp'])
    rmodel = rm.tidal(tsconfig['UStar'],
                      tsconfig['RefHt'])
    return smodel, cmodel, rmodel


def _ieckai(tsconfig):
    smodel = sm.ieckai(tsconfig['IEC_WindType'],
                       tsconfig['IECstandard'],
                       tsconfig['IECedition'],
                       tsconfig['IECturbc'],
                       tsconfig['ETMc'])
    cmodel = cm.iec(tsconfig['IECedition'])
    # The IEC models do not look at Reynold's Stress.
    rmodel = rm.uniform(upvp_=0.0,
                        upwp_=0.0,
                        vpwp_=0.0)
    return smodel, cmodel, rmodel


def _iecvkm(tsconfig):
    smodel = sm.iecvkm(tsconfig['IEC_WindType'],
                       tsconfig['IECstandard'],
                       tsconfig['IECedition'],
                       tsconfig['IECturbc'],
                       tsconfig['ETMc'])
    cmodel = cm.iec(tsconfig['IECedition'])
    # The IEC models do not look at Reynold's Stress.
    rmodel = rm.uniform(upvp_=0.0,
                        upwp_=0.0,
                        vpwp_=0.0)
    return smodel, cmodel, rmodel


def _nwtcup(tsconfig):
    smodel = sm.nwtcup(tsconfig['UStar'], tsconfig['RICH_NO'], tsconfig['ZI'])
    cmodel = cm.nwtc(tsconfig.incdec_a, tsconfig.incdec_b, tsconfig['CohExp'])
    rmodel = rm.uniform(upvp_=tsconfig['PC_UV'],
                        upwp_=tsconfig['PC_UW'],
                        vpwp_=tsconfig['PC_VW'])
    return smodel, cmodel, rmodel


def _smooth(tsconfig):
    smodel = sm.nwtc.smooth(
        tsconfig['UStar'], tsconfig['RICH_NO'], tsconfig['ZI'])
    cmodel = cm.nwtc(tsconfig.incdec_a, tsconfig.incdec_b, tsconfig['CohExp'])
    rmodel = rm.uniform(upvp_=tsconfig['PC_UV'],
                        upwp_=tsconfig['PC_UW'],
                        vpwp_=tsconfig['PC_VW'])
    return smodel, cmodel, rmodel
