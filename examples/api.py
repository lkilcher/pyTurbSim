"""
This script provides an example usage of the TurbGen API.
"""
# Begin by importing the TurbGen API:
import TurbGen.api as tg

# Define some variables for the TurbGen run:
refht = 10.
ustar = 0.03
Uref = 3.

# Initialize a TurbGen run object:
tgr = tg.tgrun()

# And give the run object a grid:
tgr.grid = tg.RectGrid(
    center=refht, ny=5, nz=5, height=5, width=9, time_sec=1000, dt=0.5)

# Now we define a mean 'profile model',
prof_model = tg.profModels.h2l(Uref, refht, ustar)
# and assign it to the run object,
tgr.prof = prof_model
# These two steps can be completed in one as:
#tgr.profModel=tg.profModels.h2l(U,refht,ustar)

# Next we define and assign a 'spectral model' to the run object,
tgr.spec = tg.specModels.tidal(ustar, refht)

# ... and define/assign a 'coherence model',
tgr.cohere = tg.cohereModels.nwtc()

# ... and define/assign a 'stress model',
tgr.stress = tg.stressModels.tidal(ustar, refht)

# Now simply 'call' the run object to generate the output.
out = tgr()

# We can save the output in 'bladed' format,
out.write_bladed('ExampleOutput.bl')
