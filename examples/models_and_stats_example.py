"""

"""

# Begin by importing the TurbGen API:
import TurbGen.api as tg

# In the 'example_usage.py' file we simply set a 'model' for each
# model type. Then when the run-object (tgr) is called, it implicitly
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
tgr = tg.tgrun()

# Define the grid,
tgr.grid = tg.tsGrid(
    center=refht, ny=5, nz=5, height=5, width=9, time_sec=1000, dt=0.5)

# Define a mean 'profile model',
prof_model = tg.profModels.h2l(U, refht, ustar)

# and assign it to the run object,
tgr.profModel = prof_model
# These two steps can be completed in one as:
#tgr.profModel=tg.profModels.h2l(U,refht,ustar)

# Next we define and assign a 'spectral model' to the run object,
tgr.specModel = tg.specModels.tidal(ustar, refht)

# ... and define/assign a 'coherence model',
tgr.cohereModel = tg.cohereModels.nwtc()

# ... and define/assign a 'stress model',
tgr.stressModel = tg.stressModels.tidal(ustar, refht)

# Now simply 'call' the run oject to produce the output.
out = tgr()

##################################
# Section 2) Using models only.

# We can re-initialize the run-object using the 'clear' method.
tgr.reset()
