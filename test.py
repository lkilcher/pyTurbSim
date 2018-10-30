from TurbGen import api as tg
from TurbGen.plot import api as pt
import TurbGen.io.write as write
reload(write)


ustar = .8
U = 17.
ny = 5
nz = 5
# ny=17;nz=17

tsr = tg.tsrun()
tsr.grid = tg.tsGrid(center=10, ny=ny, nz=nz,
                       height=10, width=10, time_sec=600, dt=0.1)

tsr.prof = tg.profModels.pl(U, 90)
tsr.spec = tg.specModels.tidal(ustar, 10)
tsr.cohere = tg.cohereModels.nwtc()
tsr.stress = tg.stressModels.uniform(0.0, 0.0, 0.0)
# Right now only the 'uniform' random phase model works:
tsr.phase = tg.phaseModels.Uniform()
# In the future we should be able to replace the above with something
# like this:
# tsr.phase = tg.phaseModels.Rinker(rho=0.3, mu=np.pi / 2)

tsdat = tsr()

write.formatted('tmp/testfile', tsdat)

tsdat.write_sum('tmp/testfile.sum')

fg = pt.summfig()
fg.plot(tsdat)
fg.plot(tsr, color='r')
fg.finalize()
fg.ax[-1, -1].set_ylim([1e-4, 10])
fg.ax[0, 0].set_xlim([-1, 15])

fg.savefig('pub/fig/TurbGen_SummFig.png')
