"""
This script provides an example usage of the PyTurbSim API.
"""

# Begin by importing the PyTurbSim API and plotting tools
### BLOCK1
import pyts.api as pyts
import pyts.plot.api as plt
from matplotlib.pylab import show
### BLOCK1.END

# Define some variables for the PyTurbSim run:
refht = 4
ustar = 0.03
Uref = 3.

# Now create the PyTurbSim run, and specify input statistics.
tsr = pyts.tsrun()
tsr.grid = pyts.tsGrid(center=refht,
                       ny=3,
                       nz=5,
                       height=5,
                       width=5,
                       time_sec=30000,
                       dt=0.5)
tsr.prof = pyts.profModels.h2l(Uref, refht, ustar)
tsr.spec = pyts.specModels.tidal(ustar, refht)
tsr.cohere = pyts.cohereModels.nwtc()
tsr.stress = pyts.stressModels.tidal(ustar, refht)

# Run PyTurbSim:
out = tsr()

# Create a 'PyTurbSim plotting figure' (plotting object):
fig = plt.summfig(axforms=[plt.axform.velprof([0, 3.5]),
                           plt.axform.tkeprof(),
                           plt.axform.stressprof(),
                           plt.axform.spec(),
                           plt.axform.cohere(), ],
                  nfft=1024,
                  )

# Now just call this plotting object's 'plot' method with the
# PyTurbSim output as input:
fig.plot(out, color='k')

# These plotting objects are smart; when the same 'plot' method
# is given a PyTurbSim 'run' object it plots the target values:
fig.plot(tsr, color='r', linestyle='--')

fig.finalize()

show()
