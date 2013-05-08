from mBase import *

class main(profModelBase):
    """
    The power-law mean wind profile.
    """

    def initModel(self,):
        self._u[0]=self.model(self.grid.z,self.URef,self.RefHt)[:,None]

    def model(self,z,uref,zref):
        """
        The function for calculating the mean velocity profile.
        """
        return uref*(z/zref)**self.PLExp

    @property
    def PLExp(self,):
        """
        The default Wind Profile power law exponent.
        """
        if self.config['PLExp'] is not None:
            return self.config['PLExp']
        tm=self.config['TurbModel'].lower()
        Ri=self.config['RICH_NO']
        if tm in ['ieckai','iecvkm']:
            if self.config['IECstandard']==1 and self.config['IEC_WindType'].lower()=='ewm':
                plexp=0.11
            elif self.config['IECstandard']==3:
                plexp=0.14
            plexp={'ewm':0.11,'ntm':0.14}.get(self.config['WindProfileType'],0.2)
        elif tm in ['wf_upw','nwtcup']:
            if self.config['IECturbc'].lower()=='khtest' and self.config['TurbModel'].lower()=='nwtcup':
                plexp=0.3
            if Ri>0:
                plexp=0.14733
            else:
                plexp=0.087688+0.059641*np.exp(Ri/0.04717783)
        elif tm in ['wf_07d','wf_14d']:
            if Ri>0.04:
                plexp=0.17903
            else:
                plexp=0.1277+0.031229*np.exp(Ri/0.0805173)
        else: #['smooth','gp_llj','tidal','river']:
            plexp=0.143
        self.config['PLExp']=plexp
        return plexp
