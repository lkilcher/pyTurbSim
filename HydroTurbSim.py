#!/usr/bin/python
import sys
import hts

if len(sys.argv)>1:
    hts.run(sys.argv[1])
else:
    try:
        hts.run('HydroTurbSim.inp')
    except:
        pass
