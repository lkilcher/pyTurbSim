#!/usr/bin/python
"""
This is the TurbGen 'executable script', which utilizes the
:mod:`TurbGen.runConfig` package.
"""

import sys
from TurbGen.runInput.main import readInput, run, write
import time


if len(sys.argv) > 1:
    fname = sys.argv[1]
else:
    fname = 'HydroTurbSim.inp'

config = readInput(fname)

tm0 = time.time()
tsdat = run(config)
write(tsdat, config, fname)
print 'TurbGen exited normally, runtime was %g seconds' % (time.time() - tm0)
