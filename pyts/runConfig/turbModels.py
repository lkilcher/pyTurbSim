# !!!ADDDOC
from .. import specModels as sm
from .. import cohereModels as cm
from .. import stressModels as rm

def getModel(tsconfig):
    # !!!ADDDOC
    return eval(tsconfig['TurbModel'].lower()+'(tsconfig)')

def tidal(tsconfig):
    # !!!ADDDOC
    smodel=sm.tidal(tsconfig['UStar'],tsconfig['RefHt'])
    cmodel=cm.nwtc(tsconfig.incdec_a,tsconfig.incdec_b,tsconfig['CohExp'])
    rmodel=rm.tidal(tsconfig['RefHt'])
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
