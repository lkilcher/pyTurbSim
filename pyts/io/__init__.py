"""
This is the PyTurbSim input/output package. It contains modules for
reading/writing PyTurbSim input/data from/to disk.

The modules contained in this package are:
  bladed.py  - For reading/writing 'bladed' format binary files.
  aerodyn.py - For reading/writing 'Aerodyn/TurbSim' format binary files.
  config.py  - For reading/writing TurbSim input files (.inp).
  base.py    - This describes a few base functions/variables used by
               other modules in this package.
  main.py    - This contains a somewhat deprecated function
               'readModel' for collecting data from TurbSim
               input/output files.

"""
