"""
This script provides an example usage of the PyTurbSim API.
"""
# Begin by importing the PyTurbSim API:
import pyts.api as pyts

# Define some variables for the PyTurbSim run:
refht = 10.
ustar = 0.03
Uref = 3.

# First we initialize a PyTurbSim 'run' object:
tsr = pyts.tsrun()

# Next we give this run object a grid:
tsr.grid = pyts.tsGrid(
    center=refht, ny=5, nz=5, height=5, width=9, time_sec=1000, dt=0.5)

# Now we define a mean 'profile model',
prof_model = pyts.profModels.h2l(Uref, refht, ustar)
# and assign it to the run object,
tsr.prof = prof_model
# These two steps can be completed in one as:
#tsr.profModel=pyts.profModels.h2l(U,refht,ustar)

# Next we define and assign a 'spectral model' to the run object,
tsr.spec = pyts.specModels.tidal(ustar, refht)

# ... and define/assign a 'coherence model',
tsr.cohere = pyts.cohereModels.nwtc()

# ... and define/assign a 'stress model',
tsr.stress = pyts.stressModels.tidal(ustar, refht)

# Now simply 'call' the run oject to produce the TurbSim output.
turbsim_output = tsr()

# We can save the output in 'bladed' format,
turbsim_output.writeBladed('ExampleOutput.bl')
