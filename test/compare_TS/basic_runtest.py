from TurbGen import api as tg
from TurbGen.plot import api as pt
import TurbGen.io.write as write
#reload(write)


ustar = .8
U = 17.
ny = 5
nz = 5
# ny=17;nz=17

tgr = tg.TGrun()
tgr.grid = tg.RectGrid(center=10, ny=ny, nz=nz,
                       height=10, width=10, time_sec=600, dt=0.1)

tgr.prof = tg.profModels.pl(U, 90)
tgr.spec = tg.specModels.tidal(ustar, 10)
tgr.cohere = tg.cohereModels.nwtc()
tgr.stress = tg.stressModels.uniform(0.0, 0.0, 0.0)
# Right now only the 'uniform' random phase model works:
tgr.phase = tg.phaseModels.Uniform()
# In the future we should be able to replace the above with something
# like this:
# tgr.phase = tg.phaseModels.Rinker(rho=0.3, mu=np.pi / 2)

dat = tgr()

write.formatted('tmp/testfile', dat)

dat.write_sum('tmp/testfile.sum')

fg = pt.summfig()
fg.plot(dat)
fg.plot(tgr, color='r')
fg.finalize()
fg.ax[-1, -1].set_ylim([1e-4, 10])
fg.ax[0, 0].set_xlim([-1, 15])

fg.fig.savefig('./tmp/TurbGen_SummFig.png')
