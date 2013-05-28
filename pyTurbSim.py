#!/usr/bin/python
import sys
import pyts

if len(sys.argv)>1:
    pyts.run(sys.argv[1])
else:
    try:
        pyts.run('HydroTurbSim.inp')
    except:
        pass
