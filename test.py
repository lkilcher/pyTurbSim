from pyts import api as pyts
from pyts.plot import api as pt
import pyts.io.write as write
reload(write)


ustar = .8
U = 17.
ny = 5
nz = 5
# ny=17;nz=17

tsr = pyts.tsrun()
tsr.grid = pyts.tsGrid(center=10, ny=ny, nz=nz,
                       height=10, width=10, time_sec=600, dt=0.1)

tsr.prof = pyts.profModels.pl(U, 90)
tsr.spec = pyts.specModels.tidal(ustar, 10)
tsr.cohere = pyts.cohereModels.nwtc()
tsr.stress = pyts.stressModels.uniform(0.0, 0.0, 0.0)

tsdat = tsr()

write.formatted('tmp/testfile', tsdat)

tsdat.write_sum('tmp/testfile.sum')

fg = pt.summfig()
fg.plot(tsdat)
fg.plot(tsr, color='r')
fg.finalize()
fg.ax[-1, -1].set_ylim([1e-4, 10])
fg.ax[0, 0].set_xlim([-1, 15])

fg.savefig('pub/fig/PyTurbSim_SummFig.png')
