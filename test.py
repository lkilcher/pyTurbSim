from pyts import api as pyts
from pyts import plot as pt

ustar = .8
U = 17.
ny = 5
nz = 5
# ny=17;nz=17

tsr = pyts.tsrun()
tsr.grid = pyts.tsGrid(center=10, ny=ny, nz=nz,
                       height=10, width=10, time_sec=60, dt=0.003)

tsr.profModel = pyts.profModels.pl(U, 90)
tsr.specModel = pyts.specModels.tidal(5 * ustar, 10)
#tsr.specModel = pyts.specModels.smooth(ustar, 0.5)
tsr.cohereModel = pyts.cohereModels.nwtc()
tsr.stressModel = pyts.stressModels.uniform(0., .8, 0)
# tsr.stressModel=pyts.stressModels.uniform(0,-.0001,0)

# tsr.stress=np.zeros(tsr.grid.shape,dtype='float32')

tsdat = tsr()
tsdat.writeSum('tmp/testfile.sum')

# fg = pt.summfig()
# fg.plot(tsdat)
# fg.plot_theory(tsr, 'r--')
# fg.finish()

# fg.savefig('pub/fig/PyTurbSim_SummFig.png')
