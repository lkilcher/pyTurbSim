# !!!ADDDOC
from .mBase import specModelBase,np,ts_float,specObj
from ..misc import InvalidConfig,Lambda

class iecbase(specModelBase):
    """
    This is a base class for the IEC spectral models (IECKAI and IECVKM).
    """
    
    def __init__(self,IECwindtype,IECstandard,IECedition,IECturbc,ETMc=None):
        """
        
        """
        # !!!ADDDOC
        if ETMc is None:
            ETMc=2.0
        self.IECwindtype=IECwindtype
        self.IECstandard=IECstandard
        self.IECedition=IECedition
        self.IECturbc=IECturbc
        self.ETMc=ETMc

    def Lambda(self,zhub):
        return Lambda(zhub,self.IECedition)

    def check_ewm(self,grid):
        if self.IECturbc.__class__ is str and self.IECstandard==1 and self.IECedition==3 and self.IECwindtype.lower()[1:4]=='ewm' and self.grid.time_sec_out!=600.:
            warnings.warn("The extreme wind model is only valid for 10min (600s) runs.  Setting 'UsableTime' to 600s.")
            grid.time_sec_out=600.

    def IEC_Sigma(self,uhub):
        """
        Calculate the default value of the standard deviation of wind speed.
        """
        iecver=self.IECstandard
        if iecver is None:
            return None
        if self.IECturbc.__class__ is str:
            # !!!VERSION_INCONSISTENCY: add 'khtest' functionality.
            val=self.IECturbc.lower()
            wndtp=self.IECwindtype.lower()
            edi=self.IECedition
            if iecver==1: # Onshore-big wind.
                if edi==2: #2nd edition
                    if wndtp!='ntm':
                        raise InvalidConfig("For IEC Turbulence models other than NTM, the iec edition must be 3.")
                    if val=='a':
                        TurbInt15=0.18
                        SigmaSlope=2.0
                    elif val=='b':
                        TurbInt15=0.16
                        SigmaSlope=3.0
                    else:
                        raise InvalidConfig("For the 61400-1 2nd edition, IECturbc must be set to 'a', 'b', or a number (Turbulence intensity).")
                    IEC_Sigma=TurbInt15*(( 15.0 + SigmaSlope*uhub)/(SigmaSlope +1))
                    return IEC_Sigma
                elif edi==3: #3rd edition
                    if val=='a':
                        TurbInt15 = 0.16
                    elif val=='b':
                        TurbInt15 = 0.14
                    elif val=='c':
                        TurbInt15 = 0.12
                    else:
                        raise InvalidConfig("For the 61400-1 3rd edition, IECturbc must be set to 'a', 'b', 'c', or a number (Turbulence intensity).")
                    if wndtp=='ntm':
                        IEC_Sigma=TurbInt15*(0.75*uhub+5.6)#/uhub
                        return IEC_Sigma
                    elif wndtp[0] not in ['1','2','3']:
                        raise InvalidConfig("A wind turbine class (1, 2 or 3) must be specified with the extreme turbulence and extreme wind types (e.g. '1ETM' or '2EWM').")
                    elif wndtp[1:4] in ['etm','ewm']:
                        Vref={'1':50,'2':42.5,'3':37.5}[wndtp[0]]
                        wndtp=wndtp[1:]
                        if wndtp=='etm':
                            vave=0.2*Vref
                            IEC_Sigma=self.ETMc*TurbInt15*(0.072*(0.2*Vref/self.ETMc+3.)*(uhub/self.ETMc-4)+10.)
                            return IEC_Sigma
                        else:
                            IEC_Sigma=0.11*uhub
                            return 0.11 # Fixed turbulence intensity for the EWM models.
                    else:
                        raise InvalidConfig("Invalid 'IEC_WindType' specified in config file.")
            elif iecver==2: # Small wind.
                pass
            elif iecver==3: # Offshore wind.
                pass
        else: # The IECturbc is numeric.
            if wndtp!='ntm':
                raise InvalidConfig("If the 'IECturbc' config option is a number (specifying turbulence intensity), the IEC_WindType must be 'NTM'.")

class ieckai(iecbase):
    # !!!ADDDOC

    def __call__(self,tsrun):
        # !!!ADDDOC
        self.check_ewm(tsrun.grid)
        out=specObj(tsrun)
        sig2=4*self.IEC_Sigma(tsrun.prof.uhub)**2
        fctr=np.array([1,0.64,0.25],dtype=ts_float)
        L_u=self.Lambda(tsrun.grid.zhub)/tsrun.prof.uhub*np.array([8.10,2.70,0.66],dtype=ts_float)
        for comp in self.comp:
            out[comp]=(sig2*fctr[comp]*L_u[comp]/(1+6*out.f*L_u[comp])**self.pow5_3)[None,None,:]
        return out
    
class iecvkm(iecbase):
    # !!!ADDDOC

    def __call__(self,tsrun):
        # !!!ADDDOC
        self.check_ewm(tsrun.grid)
        out=specObj(tsrun)
        sig2=4*self.IEC_Sigma(tsrun.prof.uhub)**2
        L_u=3.5*self.Lambda(tsrun.grid.zhub)/tsrun.prof.uhub
        dnm=1+71*(out.f*L_u)**2
        out[0]=(sig2*L_u/(dnm)**0.8333333)[None,None,:]
        out[2]=out[1]=(sig2/2*L_u/(dnm)**1.8333333*(1+189*(out.f*L_u)**2))[None,None,:]
        return out
