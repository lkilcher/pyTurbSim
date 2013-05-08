#!/usr/bin/python
import sys
import ts2

if len(sys.argv)>1:
    ts2.run(sys.argv[1])
else:
    try:
        ts2.run('TurbSim.inp')
    except:
        pass
