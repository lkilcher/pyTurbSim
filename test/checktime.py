import sys

sys.path.append('../')

import pyts
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

pm = pyts.profModels.h2l(U, refht, ustar)
sm = pyts.specModels.tidal(ustar, refht)
cm = pyts.cohereModels.nwtc()
rm = pyts.stressModels.tidal(refht)

## seq=pyts.tsrun(ncore=1)
## for idx,n in enumerate(nvals):
##     tm0=time.time()
##     seq.timer.total=0
##     cm.timer.total=0
##     seq.grid=pyts.tsGrid(center=refht,ny=n,nz=n,height=5,width=9,time_sec=6000,dt=0.5)
##     seq.profModel=pm
##     seq.specModel=sm
##     seq.cohereModel=cm
##     seq.stressModel=rm
##     turbsim_output=seq.run()
##     print seq.timer
##     print seq.cohereModel.timer
##     tms['seq'][idx]=time.time()-tm0
##     tms['seq-Veers'][idx]=seq.timer.total
##     tms['seq-Coh'][idx]=cm.timer.total
##     print '%d-point non-Parallel TurbSim run took %0.2f seconds.' % (n**2,tms['seq'][idx])
##     del turbsim_output
##     seq.clear()

par = pyts.tsrun(ncore=1)
for idx, n in enumerate(nvals):
    tm0 = time.time()
    par.timer.total = 0
    cm.timer.total = 0
    par.grid = pyts.tsGrid(
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
    ## tmr=pyts.dbg.timer()
    ## tmr.start()
    ## ft=pyts.tslib.tslib.nonieccoh(par.spec.flat[comp],phr[comp],par.grid.f,par.grid.y,par.grid.z,par.grid.flatten(par.prof.u),par.cohere.a[comp],par.cohere.b[comp],cm.CohExp,cohi.ncore,cohi.n_f,cohi.n_y,cohi.n_z)
    ## tmr.stop()
    ## print tmr
    turbsim_output = par.run()
    tms['par'][idx] = time.time() - tm0
    tms['par-Veers'][idx] = par.timer.total
    tms['par-Coh'][idx] = cm.timer.total
    print '%d-point Parallel TurbSim run took %0.2f seconds.' % (n ** 2, tms['par'][idx])
    del turbsim_output
    par.clear()
