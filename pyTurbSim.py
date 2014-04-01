#!/usr/bin/python
import sys
from pyts.runConfig.main import readConfig,run,write
import time



if len(sys.argv)>1:
    fname=sys.argv[1]
else:
    fname='HydroTurbSim.inp'

config=readConfig(fname)

tm0=time.time()
tsdat=run(config)
write(tsdat,config,fname)
print 'TurbSim exited normally, runtime was %g seconds' % (time.time()-tm0)
