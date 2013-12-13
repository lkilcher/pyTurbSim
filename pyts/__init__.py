### This file defines the 'run' functions of the hts package.
from main import run_main
import tsio as io
from tsio import writeOut,readConfig

def run_out(fname):
    """
    Read the input file, run TurbSim, and return the tsdata object.

    *** This function does not write files to disk. ***
    """
    
    config=readConfig(fname)
    
    return run_main(config)

def run(fname):
    """
    Read the input file, run TurbSim, and write data in the tsdata object
    to the files specified in the input file.
    """
    
    tsdata=run_out(fname)

    writeOut(fname,tsdata)

    return tsdata
        
# If this module is executed explicitly, run TurbSim...
if __name__=='__main__':
    run('TurbSim.inp')
