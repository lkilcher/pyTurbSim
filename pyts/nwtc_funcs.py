import numpy as np
from misc import kappa


def zL(Ri,TurbModel=None):
    """
    *zL* is the Monin-Obhukov (M-O) stability parameter z/L, where L is the M-O length.

    zL>0 means stable conditions.
    """
    if TurbModel.__class__ is str and TurbModel.lower()=='nwtcup':
        Ri=max( min(Ri,0.155),-1.)
        if Ri<=-0.1:
            return -0.254 + 1.047*Ri
        elif Ri<0:
            return 10.369*Ri/(1.-19.393*Ri)
        else:
            return 2.535*Ri/(1.-6.252*Ri)
    elif TurbModel.__class__ is str and TurbModel.lower()=='gp_llj':
        Ri=max( min(Ri,0.1367),-1.)
        if Ri<=-0.1:
            return -0.047 + 1.056*Ri
        elif Ri<0:
            return 2.213*Ri/(1.-4.698*Ri)
        else:
            return 3.132*Ri/(1.-6.762*Ri)
    else:
        # This is the relationship between zL and Ri detailed in:
        # Businger etal 'Flux-Profile Relationships in the Atmospheric Surface Layer' 1971,
        if Ri<0:
            return Ri
        elif Ri<.16666666:
            return Ri/(1-5.*Ri)
        else:
            return 1


def psiM(Ri,TurbModel=None):
    zl=zL(Ri,TurbModel)
    if zl>=0:
        return -5.0*min(zl,1.0)
    else:
        tmp=(1.-15.0*zl)**0.25
        return -np.log(0.125*((1.0+tmp)**2*(1.0+tmp**2)))+2.0*np.arctan(tmp)-0.5*np.pi


class InvalidConfig(Exception):
    """
    Exception raised by the baseModel classes.  Used to indicate that a model has not defined a necessary attribute.
    """
    def __init__(self,msg='Invalid option specified in config file.'):
        self.msg=msg
