"""

"""

# Begin by importing the PyTurbSim API:
import pyts.api as pyts

# In the 'example_usage.py' file we simply set a 'model' for each
# model type. Then when the run-object (tsr) is called, it implicitly
# calculates the statistics for each model. Here we are going to
# explicitly call each model and define the statistics for the run.

# Define some variables:
refht = 10.
ustar = 0.03
U = 3.

##################################
# Section 1) Using models only.
###
# Initialize a 'run' object:
tsr = pyts.tsrun()

# Define the grid,
tsr.grid = pyts.tsGrid(
    center=refht, ny=5, nz=5, height=5, width=9, time_sec=1000, dt=0.5)

# Define a mean 'profile model',
prof_model = pyts.profModels.h2l(U, refht, ustar)

# and assign it to the run object,
tsr.profModel = prof_model
# These two steps can be completed in one as:
#tsr.profModel=pyts.profModels.h2l(U,refht,ustar)

# Next we define and assign a 'spectral model' to the run object,
tsr.specModel = pyts.specModels.tidal(ustar, refht)

# ... and define/assign a 'coherence model',
tsr.cohereModel = pyts.cohereModels.nwtc()

# ... and define/assign a 'stress model',
tsr.stressModel = pyts.stressModels.tidal(ustar, refht)

# Now simply 'call' the run oject to produce the TurbSim output.
turbsim_output = tsr()

##################################
# Section 2) Using models only.

# We can re-initialize the run-object using the 'clear' method.
tsr.reset()
