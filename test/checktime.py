import sys

sys.path.append('../')

import TurbGen as tg
import time

refht = 10.
ustar = 0.03
U = 3.

nvals = np.array([15])
tms = {}
tms['seq'] = np.empty(nvals.shape, dtype='float')
tms['seq-Veers'] = np.empty(nvals.shape, dtype='float')
tms['seq-Coh'] = np.empty(nvals.shape, dtype='float')
tms['par'] = np.empty(nvals.shape, dtype='float')
tms['par-Veers'] = np.empty(nvals.shape, dtype='float')
tms['par-Coh'] = np.empty(nvals.shape, dtype='float')

pm = tg.profModels.h2l(U, refht, ustar)
sm = tg.specModels.tidal(ustar, refht)
cm = tg.cohereModels.nwtc()
rm = tg.stressModels.tidal(refht)

## seq=tg.TGrun(ncore=1)
## for idx,n in enumerate(nvals):
##     tm0=time.time()
##     seq.timer.total=0
##     cm.timer.total=0
##     seq.grid=tg.RectGrid(center=refht,ny=n,nz=n,height=5,width=9,time_sec=6000,dt=0.5)
##     seq.profModel=pm
##     seq.specModel=sm
##     seq.cohereModel=cm
##     seq.stressModel=rm
##     output=seq.run()
##     print seq.timer
##     print seq.cohereModel.timer
##     tms['seq'][idx]=time.time()-tm0
##     tms['seq-Veers'][idx]=seq.timer.total
##     tms['seq-Coh'][idx]=cm.timer.total
##     print '%d-point non-Parallel TurbGen run took %0.2f seconds.' % (n**2,tms['seq'][idx])
##     del output
##     seq.clear()

par = tg.TGrun(ncore=1)
for idx, n in enumerate(nvals):
    tm0 = time.time()
    par.timer.total = 0
    cm.timer.total = 0
    par.grid = tg.RectGrid(
        center=refht, ny=n, nz=n, height=5, width=9, time_sec=6000, dt=0.5)
    par.profModel = pm
    par.specModel = sm
    par.cohereModel = cm
    par.stressModel = rm
    par.prof = par.profModel(par)
    par.spec = par.specModel(par)
    par.stress = par.stressModel(par)
    ## cohi=par.cohere=par.cohereModel(par)
    ## phr=par.stress.calcPhases()
    ## comp=0
    ## tmr=tg.dbg.timer()
    ## tmr.start()
    ## ft=tg.tslib.tslib.nonieccoh(par.spec.flat[comp],phr[comp],par.grid.f,par.grid.y,par.grid.z,par.grid.flatten(par.prof.u),par.cohere.a[comp],par.cohere.b[comp],cm.CohExp,cohi.ncore,cohi.n_f,cohi.n_y,cohi.n_z)
    ## tmr.stop()
    ## print tmr
    output = par.run()
    tms['par'][idx] = time.time() - tm0
    tms['par-Veers'][idx] = par.timer.total
    tms['par-Coh'][idx] = cm.timer.total
    print '%d-point Parallel TurbGen run took %0.2f seconds.' % (n ** 2, tms['par'][idx])
    del output
    par.clear()
