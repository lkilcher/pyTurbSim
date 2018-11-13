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

tgr = tg.TGrun()
tgr.grid = tg.RectGrid(center=center, ny=ny, nz=nz,
                       height=10, width=10, time_sec=60, dt=0.003)

tgr.profModel = tg.profModels.pl(U, center)
tgr.specModel = tg.specModels.smooth(ustar, 0.5)
tgr.cohereModel = tg.cohereModels.nwtc()
tgr.stressModel = tg.stressModels.uniform(0., 0.0, 0)
# tgr.stressModel=tg.stressModels.uniform(0,-.0001,0)

# tgr.stress=np.zeros(tgr.grid.shape,dtype='float32')

tsdat = tgr()

fg = pt.summfig(axforms=[pt.axform.velprof(),
                         pt.axform.Tiprof(),
                         pt.axform.tkeprof(),
                         pt.axform.stressprof(),
                         pt.axform.spec(window_time_sec=60)])
fg.plot(tsdat)
fg.plot(tgr, color='r', linestyle='--')
fg.finalize()

# fg.savefig('pub/fig/TurbGen_SummFig.png')
