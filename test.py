import pyts
import pyts_plot as pt

ustar=.8
U=17.
ny=5;nz=5
#ny=17;nz=17

tsr=pyts.tsrun()
tsr.grid=pyts.tsGrid(center=90,ny=ny,nz=nz,height=80,width=80,time_sec=10000,dt=0.5)

tsr.profModel=pyts.profModels.pl(U,90)
tsr.specModel=pyts.specModels.smooth(ustar,0.5)
#tsr.cohereModel=pyts.cohereModels.none()
tsr.cohereModel=pyts.cohereModels.nwtc()
tsr.stressModel=pyts.stressModels.uniform(0.,.8,0)
#tsr.stressModel=pyts.stressModels.uniform(0,-.0001,0)

## tsr.stress=np.zeros(tsr.grid.shape,dtype='float32')

tsdat=tsr()

fg=pt.summfig()
fg.plot(tsdat)
fg.plot_theory(tsr,'r--')
fg.finish()

## fg.savefig('pub/fig/PyTurbSim_SummFig.png')

