"""
This module contains functions for producing the appropriate turbulence
model for a specific TurbSim input object (derived from an input
file).

The term 'TurbModels' encompasses the 'specModel', 'cohereModel' and
'stressModel' functionalities of the PyTurbSim program.  Within the
'runInput' package all three of these statistics are handled in this
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


def getModel(tsinput):
    """
    This is the wrapper function for all turbulence models implemented
    in the runInput package.

    Parameters
    ----------
    tsinput :  :class:`tscfg <.base.tscfg>`
                A TurbSim input object.

    Returns
    -------
    specModel :         A subclass of :class:`.specModelBase`
                        The appropriately initialized 'spectral model' object
                        specified in `tsinput`.
    cohereModel :       A subclass of :class:`.cohereModelBase`
                        The appropriately initialized 'coherence model' object
                        specified in `tsinput`.
    stressModel :       A subclass of :class:`.stressModelBase`
                        The appropriately initialized 'stress model' object
                        specified in `tsinput`.

    """
    # This executes the sub-wrapper function (defined below) specified
    # in the tsinput-object (input file TurbModel line)
    return eval('_' + tsinput['TurbModel'].lower() + '(tsinput)')


def _tidal(tsinput):
    smodel = sm.tidal(tsinput['UStar'], tsinput['RefHt'])
    cmodel = cm.nwtc(tsinput.incdec_a, tsinput.incdec_b, tsinput['CohExp'])
    rmodel = rm.tidal(tsinput['UStar'], tsinput['RefHt'])
    return smodel, cmodel, rmodel


def _river(tsinput):
    smodel = sm.river(tsinput['UStar'],
                      tsinput['RefHt'])
    cmodel = cm.nwtc(tsinput.incdec_a,
                     tsinput.incdec_b,
                     tsinput['CohExp'])
    rmodel = rm.tidal(tsinput['UStar'],
                      tsinput['RefHt'])
    return smodel, cmodel, rmodel


def _ieckai(tsinput):
    smodel = sm.ieckai(tsinput['IEC_WindType'],
                       tsinput['IECstandard'],
                       tsinput['IECedition'],
                       tsinput['IECturbc'],
                       tsinput['ETMc'])
    cmodel = cm.iec(tsinput['IECedition'])
    # The IEC models do not look at Reynold's Stress.
    rmodel = rm.uniform(upvp_=0.0,
                        upwp_=0.0,
                        vpwp_=0.0)
    return smodel, cmodel, rmodel


def _iecvkm(tsinput):
    smodel = sm.iecvkm(tsinput['IEC_WindType'],
                       tsinput['IECstandard'],
                       tsinput['IECedition'],
                       tsinput['IECturbc'],
                       tsinput['ETMc'])
    cmodel = cm.iec(tsinput['IECedition'])
    # The IEC models do not look at Reynold's Stress.
    rmodel = rm.uniform(upvp_=0.0,
                        upwp_=0.0,
                        vpwp_=0.0)
    return smodel, cmodel, rmodel


def _nwtcup(tsinput):
    smodel = sm.nwtcup(tsinput['UStar'], tsinput['RICH_NO'], tsinput['ZI'])
    cmodel = cm.nwtc(tsinput.incdec_a, tsinput.incdec_b, tsinput['CohExp'])
    rmodel = rm.uniform(upvp_=tsinput['PC_UV'],
                        upwp_=tsinput['PC_UW'],
                        vpwp_=tsinput['PC_VW'])
    return smodel, cmodel, rmodel


def _smooth(tsinput):
    smodel = sm.nwtc.smooth(
        tsinput['UStar'], tsinput['RICH_NO'], tsinput['ZI'])
    cmodel = cm.nwtc(tsinput.incdec_a, tsinput.incdec_b, tsinput['CohExp'])
    rmodel = rm.uniform(upvp_=tsinput['PC_UV'],
                        upwp_=tsinput['PC_UW'],
                        vpwp_=tsinput['PC_VW'])
    return smodel, cmodel, rmodel
