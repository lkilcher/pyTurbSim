import numpy as np

kappa=0.41 # Von-Karman's constant

def Lambda(zhub,IECedition):
    """
    Equation 23 of TurbSim Manual.
    """
    if IECedition<=2:
        return 0.7*min(30,zhub)
    return 0.7*min(60,zhub)


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

def pfactor(n,pmax=31):
    primes=np.array([2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71])
    primes=primes[primes<=pmax]
    lst=set()
    for ip in primes:
        while np.mod(n,ip)==0:
            lst.add(ip)
            n/=ip
    if n!=1:
        lst.add(n)
    return np.sort(list(lst))

def lowPrimeFact_near(n,pmax=31,nmin=None,evens_only=True):
    if (np.array(pfactor(n,pmax))<pmax).all():
        return n
    if evens_only: # Only deal with evens.
        dl=2
        if np.mod(n,2)>0:
            n+=1
    else:
        dl=1
    lowval=None
    ih=n
    if nmin is not None:
        il=n-dl
        while il>nmin:
            if (np.array(pfactor(il,pmax))<pmax).all():
                return il
            elif (np.array(pfactor(ih,pmax))<pmax).all():
                return ih
            il-=dl
            ih+=dl
    while not (np.array(pfactor(ih,pmax))<pmax).all():
        ih+=dl
    return ih

def fix2range(vals,minval,maxval):
    """
    A helper function that sets the value of the array or number *vals* to
    fall within the range minval<=vals<=maxval.
    
    Values of *vals* outside the range are fixed to minval or maxval.
    """
    if not hasattr(vals,'__len__'):
        return max( min( vals,maxval),minval)
    vals[vals>maxval],vals[vals<minval]=maxval,minval
    return vals

class InvalidConfig(Exception):
    """
    Exception raised by the baseModel classes.  Used to indicate that a model has not defined a necessary attribute.
    """
    def __init__(self,msg='Invalid option specified in config file.'):
        self.msg=msg
