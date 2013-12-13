# !!!ADDDOC
from .mBase import turbModelBase,cohModelIEC,stressModelUniform,np
from ..nwtc_funcs import InvalidConfig

def cfg_ieckai(tsconfig,profModel):
    # !!!ADDDOC
    out=ieckai(profModel,tsconfig['IEC_WindType'],tsconfig['IECstandard'],tsconfig['IECedition'],tsconfig['IECturbc'],tsconfig['ETMc'])
    out.set_cohereModel(cohModelIEC(out))
    out.set_stressModel(stressModelUniform(out,upvp_=tsconfig['PC_UV'],upwp_=tsconfig['PC_UW'],vpwp_=tsconfig['PC_VW']))
    return out

def cfg_iecvkm(tsconfig,profModel):
    # !!!ADDDOC
    out=iecvkm(profModel,tsconfig['IEC_WindType'],tsconfig['IECstandard'],tsconfig['IECedition'],tsconfig['IECturbc'],tsconfig['ETMc'])
    out.set_cohereModel(cohModelIEC(out))
    out.set_stressModel(stressModelUniform(out,upvp_=tsconfig['PC_UV'],upwp_=tsconfig['PC_UW'],vpwp_=tsconfig['PC_VW']))
    return out

class iecbase(turbModelBase):
    """
    This is a 'base' class for the two IEC models.
    """
    
    def __init__(self,profModel,IECwindtype,IECstandard,IECedition,IECturbc,ETMc=None):
        # !!!ADDDOC
        if ETMc is None:
            ETMc=2.0
        self.IECwindtype=IECwindtype
        self.IECstandard=IECstandard
        self.IECedition=IECedition
        self.IECturbc=IECturbc
        self.ETMc=ETMc
        self._set_IEC_Sigma()
        self.initModel()

    @property
    def Lambda(self,):
        """
        Equation 23 of TurbSim Manual.
        """
        if self.IECedition==2:
            return 0.7*min(30,self.grid.zhub)
        return 0.7*min(60,self.grid.zhub)

    def _set_IEC_Sigma(self,):
        """
        Calculate the default value of the standard deviation of wind speed.
        """
        iecver=self.IECstandard
        if iecver is None:
            self.IEC_Sigma=None
            return
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
                    self.IEC_Sigma=TurbInt15*(( 15.0 + SigmaSlope*self.profModel.uhub)/(SigmaSlope +1))
                    return
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
                        self.IEC_Sigma=TurbInt15*(0.75*self.profModel.uhub+5.6)#/uhub
                        return
                    elif wndtp[0] not in ['1','2','3']:
                        raise InvalidConfig("A wind turbine class (1, 2 or 3) must be specified with the extreme turbulence and extreme wind types (e.g. '1ETM' or '2EWM').")
                    elif wndtp[1:4] in ['etm','ewm']:
                        if wndtp[1:4]=='ewm' and self.grid.time_sec_out!=600.:
                            warnings.warn("The extreme wind model is only valid for 10min (600s) runs.  Setting 'UsableTime' to 600s.",ConfigWarning)
                            self.grid.time_sec_out=600.
                        Vref={'1':50,'2':42.5,'3':37.5}[wndtp[0]]
                        wndtp=wndtp[1:]
                        if wndtp=='etm':
                            vave=0.2*Vref
                            self.IEC_Sigma=self.ETMc*TurbInt15*(0.072*(0.2*Vref/self.ETMc+3.)*(self.profModel.uhub/self.ETMc-4)+10.)
                            return
                        else:
                            self.IEC_Sigma=0.11*self.profModel.uhub
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
    
    def initModel(self,):
        # !!!ADDDOC
        sig2=4*self.IEC_Sigma**2
        fctr=np.array([1,0.64,0.25])
        L_u=self.Lambda/self.profModel.uhub*np.array([8.10,2.70,0.66])
        for comp in self.comp:
            self.Saa[comp]=(sig2*fctr[comp]*L_u[comp]/(1+6*self.f*L_u[comp])**self.pow5_3)[None,None,:]

class iecvkm(iecbase):
    # !!!ADDDOC

    def initModel(self,):
        # !!!ADDDOC
        sig2=4*self.IEC_Sigma**2
        L_u=3.5*self.Lambda/self.profModel.uhub
        dnm=1+71*(self.f*L_u)**2
        self.Saa[0]=(sig2*L_u/(dnm)**0.8333333)[None,None,:]
        self.Saa[1]=(sig2/2*L_u/(dnm)**1.8333333*(1+189*(self.f*L_u)**2))[None,None,:]
        self.Saa[2]=self.Saa[1]
    
