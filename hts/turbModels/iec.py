from .mBase import *

class iecbase(turbModelCohIEC):

    @property
    def ETMc(self,):
        if self.config['ETMc'] is None:
            self.config['ETMc']=2.0
        return self.config['ETMc']

    @property
    def Lambda(self,):
        """
        TurbSim Manual equation (23).
        """
        if self.config['IECedition']==2:
            return 0.7*min(30,self.HubHt)
        return 0.7*min(60,self.HubHt)

    def calcAutoSpec(self,):
        """
        Override the default autoSpec routine because the spectrum does not vary in space.
        """
        for comp in self.comp:
            self._autoSpec[comp][:,:]=self._data[comp][None,:]

    def set_IEC_standard(self,):
        iecstd=self.config['IECstandard'].lower()
        if iecstd.__class__ is str:
            self.config['IECstandard']=int(iecstd[0])
            self.config['IECedition']=int(iecstd[-1])
        elif iecstd==1 or iecstd is None:
            self.config['IECstandard']=1
            if self.config['TurbModel'].lower()=='ieckai':
                self.config['IECedition']=3
            else:
                self.config['IECedition']=2
        else:
            self.config['IECedition']=None # There are no editions to the -2 and -3 standards.
        if self.config['IECedition']==3 and self.config['TurbModel'].lower()=='iecvkm':
            raise InvalidConfig("The von-Karman spectral model (IECVKM) is not valid for IEC standard 61400-1's 3rd edition. Either change TurbModel to IECKAI, or change the IECstandard to '1-ed2' or simply '1'.")
        elif self.config['IECedition']!=1 and self.config['IEC_WindType'].lower()!='ntm':
            raise InvalidConfig("If the IECedition is not 1, than the must WindType must be 'NTM'.")

    def set_IEC_Sigma(self,):
        """
        This is not an input/config option, but it is a variable that we need for the IEC turbulence models.
        """
        iecver=self.config['IECstandard']
        if iecver is None:
            self.IEC_Sigma=None
            return
        if self.config['IECturbc'].__class__ is str:
            # !!!VERSION_INCONSISTENCY: add 'khtest' functionality.
            val=self.config['IECturbc'].lower()
            wndtp=self.config['IEC_WindType'].lower()
            edi=self.config['IECedition']
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
                    self.IEC_Sigma=TurbInt15*(( 15.0 + SigmaSlope*self.uhub)/(SigmaSlope +1))
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
                        self.IEC_Sigma=TurbInt15*(0.75*self.uhub+5.6)#/uhub
                        return
                    elif wndtp[0] not in ['1','2','3']:
                        raise InvalidConfig("A wind turbine class (1, 2 or 3) must be specified with the extreme turbulence and extreme wind types (e.g. '1ETM' or '2EWM').")
                    elif wndtp[1:4] in ['etm','ewm']:
                        if wndtp[1:4]=='ewm' and self.config['UsableTime']!=600.:
                            warnings.warn("The extreme wind model is only valid for 10min (600s) runs.  Setting 'UsableTime' to 600s.",ConfigWarning)
                            self.config['UsableTime']=600.
                        Vref={'1':50,'2':42.5,'3':37.5}[wndtp[0]]
                        wndtp=wndtp[1:]
                        if wndtp=='etm':
                            vave=0.2*Vref
                            self.IEC_Sigma=self.ETMc*TurbInt15*(0.072*(0.2*Vref/self.ETMc+3.)*(self.uhub/self.ETMc-4)+10.)
                            return
                        else:
                            self.IEC_Sigma=0.11*self.uhub
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

    def initModel(self,):
        self.set_IEC_standard()
        self.set_IEC_Sigma()
        sig2=4*self.IEC_Sigma**2
        fctr=np.array([1,0.64,0.25])
        L_u=self.Lambda/self.profModel.uhub*np.array([8.10,2.70,0.66])
        self._data=np.empty((3,self.n_f))
        for comp in self.comp:
            self._data[comp]=sig2*fctr[comp]*L_u[comp]/(1+6*self.f*L_u[comp])**self.pow5_3
        
class iecvkm(iecbase):

    def initModel(self,):
        self.set_IEC_standard()
        self.set_IEC_Sigma()
        sig2=4*self.IEC_Sigma**2
        L_u=3.5*self.Lambda/self.profModel.uhub
        dnm=1+71*(self.f*L_u)**2
        self._data={}
        self._data[0]=sig2*L_u/(dnm)**0.8333333
        self._data[1]=sig2/2*L_u/(dnm)**1.8333333*(1+189*(self.f*L_u)**2)
        self._data[2]=self._data[1].copy()
        
