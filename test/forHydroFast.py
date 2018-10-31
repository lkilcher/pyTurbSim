import sys

sys.path.append('../')

import TurbGen.api as tg
import TurbGen.plot.api as pt

ustar = .1
U = 1.5
ny = 15
nz = 15
center = 10
# ny=17;nz=17

tsr = tg.TGrun()
tsr.grid = tg.RectGrid(center=center, ny=ny, nz=nz,
                       height=10, width=10, time_sec=60, dt=0.003)

tsr.profModel = tg.profModels.pl(U, center)
tsr.specModel = tg.specModels.smooth(ustar, 0.5)
tsr.cohereModel = tg.cohereModels.nwtc()
tsr.stressModel = tg.stressModels.uniform(0., 0.0, 0)
# tsr.stressModel=tg.stressModels.uniform(0,-.0001,0)

# tsr.stress=np.zeros(tsr.grid.shape,dtype='float32')

tsdat = tsr()

fg = pt.summfig(axforms=[pt.axform.velprof(),
                         pt.axform.Tiprof(),
                         pt.axform.tkeprof(),
                         pt.axform.stressprof(),
                         pt.axform.spec(window_time_sec=60)])
fg.plot(tsdat)
fg.plot(tsr, color='r', linestyle='--')
fg.finalize()

# fg.savefig('pub/fig/TurbGen_SummFig.png')
