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
    # !!!ADDDOC
    return eval(tsconfig['TurbModel'].lower()+'(tsconfig)')

def tidal(tsconfig):
    # !!!ADDDOC
    smodel=sm.tidal(tsconfig['UStar'],tsconfig['RefHt'])
    cmodel=cm.nwtc(tsconfig.incdec_a,tsconfig.incdec_b,tsconfig['CohExp'])
    rmodel=rm.tidal(tsconfig['UStar'],tsconfig['RefHt'])
    return smodel,cmodel,rmodel

def river(tsconfig):
    # !!!ADDDOC
    smodel=sm.river(tsconfig['UStar'],tsconfig['RefHt'])
    cmodel=cm.nwtc(tsconfig.incdec_a,tsconfig.incdec_b,tsconfig['CohExp'])
    rmodel=rm.tidal(tsconfig['RefHt'])
    return smodel,cmodel,rmodel

def ieckai(tsconfig):
    # !!!ADDDOC
    smodel=sm.ieckai(tsconfig['IEC_WindType'],tsconfig['IECstandard'],tsconfig['IECedition'],tsconfig['IECturbc'],tsconfig['ETMc'])
    cmodel=cm.iec(tsconfig['IECedition'])
    rmodel=rm.uniform(upvp_=tsconfig['PC_UV'],upwp_=tsconfig['PC_UW'],vpwp_=tsconfig['PC_VW'])
    return smodel,cmodel,rmodel

def iecvkm(tsconfig):
    # !!!ADDDOC
    smodel=sm.iecvkm(tsconfig['IEC_WindType'],tsconfig['IECstandard'],tsconfig['IECedition'],tsconfig['IECturbc'],tsconfig['ETMc'])
    cmodel=cm.iec(tsconfig['IECedition'])
    rmodel=rm.uniform(upvp_=tsconfig['PC_UV'],upwp_=tsconfig['PC_UW'],vpwp_=tsconfig['PC_VW'])
    return smodel,cmodel,rmodel

def nwtcup(tsconfig):
    # !!!ADDDOC
    smodel=sm.nwtcup(tsconfig['UStar'],tsconfig['RICH_NO'],tsconfig['ZI'])
    cmodel=cm.nwtc(tsconfig.incdec_a,tsconfig.incdec_b,tsconfig['CohExp'])
    rmodel=rm.uniform(upvp_=tsconfig['PC_UV'],upwp_=tsconfig['PC_UW'],vpwp_=tsconfig['PC_VW'])
    return smodel,cmodel,rmodel

def smooth(tsconfig):
    # !!!ADDDOC
    smodel=sm.nwtc.smooth(tsconfig['UStar'],tsconfig['RICH_NO'],tsconfig['ZI'])
    cmodel=cm.nwtc(tsconfig.incdec_a,tsconfig.incdec_b,tsconfig['CohExp'])
    rmodel=rm.uniform(upvp_=tsconfig['PC_UV'],upwp_=tsconfig['PC_UW'],vpwp_=tsconfig['PC_VW'])
    return smodel,cmodel,rmodel
