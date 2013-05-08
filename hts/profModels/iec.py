from mBase import *
from log import main as logmain
from power import main as powmain

class main(profModelBase,logmain,powmain):
    """
    The iec wind profile.
    """
    def initModel(self,):
        zrange=self.HubHt+np.array([-0.5,0.5])*min(self.grid.width,self.grid.height)
        yrange=np.array([-0.5,0.5])*min(self.grid.width,self.grid.height)
        # First calculate the logarithmic velocity profile:
        self._u[0]=logmain.model(tsconfig,self.grid.z)[:,None]
        zinds=zrange[0]<=self.grid.z & self.grid.z<=zrange[1]
        yinds=yrange[0]<=self.grid.y & self.grid.y<=yrange[1]
        # Now calculate the power-law profile for the indices on the rotor disk:
        self._u[0][zinds][:,yinds]=powmain.model(self.grid.z[zinds],self.uhub,self.grid.zhub)[:,None]

    
