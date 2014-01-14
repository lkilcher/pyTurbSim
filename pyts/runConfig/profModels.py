# !!!ADDDOC
from .. import profModels as pm

def getModel(tsconfig):
    # !!!ADDDOC
    return eval(tsconfig['WindProfileType'].lower()+'(tsconfig)')

def h2l(tsconfig):
    return pm.h2l(tsconfig['URef'],tsconfig['RefHt'],tsconfig['UStar'])

def log(tsconfig):
    return pm.log(tsconfig['URef'],tsconfig['RefHt'],tsconfig['Z0'],tsconfig['RICH_NO'],tsconfig['TurbModel'])

def pl(tsconfig):
    return pm.pl(tsconfig['URef'],tsconfig['RefHt'],tsconfig['PLExp'])
    
def iec(tsconfig):
    return pm.iec(tsconfig['URef'],tsconfig['RefHt'],tsconfig['Z0'],tsconfig['RICH_NO'],tsconfig['PLExp'],tsconfig['TurbModel'],)

