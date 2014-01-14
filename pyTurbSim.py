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
print 'TurbSim exited normally, runtime was %g seconds' % (tm0-time.time())
#write(tsdat,tsconfig,fname)
