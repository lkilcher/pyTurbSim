"""
PyTurbSim is primarily designed to produce output that matches four
statistics for each component of velocity (u,v,w):
1) The mean velocity profile (prof),
2) The turbulence energy spectrum (spec),
3) The spatial coherence (cohere), and
4) The Reynold's stresses (stress).

Within PyTurbSim each of these statistics may be defined in two
distinct ways. They may be defined using 'models' or using
'stat-objects' (essentially array wrappers). Models define a statistic
in terms of input parameters to a model and other variables of other
models.  For more information on specifying a statistic, see the four
statistic properties (prof, spec, cohere, and stress) of a tsrun
object.

-- Models --
Models define the functional form of a statistic and can depend on the
spatial grid or other stat-objects defined before it. When models are
used to compute statistics they are computed the order above
(1-4). This means that a turbulence energy spectrum model can depend
on the mean velocity profile, but not the coherence or
stress. Likewise the coherence can depend on the mean velocity and
turbulence spectrum, but not the stress, and so on.  (Even though
models cannot depend on the values of an array defined later, they can
depend on 'parameters' of that model.)

-- Stat-objects/arrays --
Stat-objects, on the other hand, contain the values of the statistic
(an array) that will be reproduced in the PyTurbSim output. However,
because stat-objects are essentially wrappers for an array of the
values of the statistic, they do not have the flexibility to depend on
the values of other statistics.

---------
This script demonstrates the use of models vs. stat-objects.

"""

# Begin by importing the PyTurbSim API:
import pyts.api as pyts

# In the 'example_usage.py' file we simply set a 'model' for each
# model type. Then when the run-object (tsr) is called, it implicitly
# calculates the statistics for each model. Here we are going to
# explicitly call each model and define the statistics for the run.

# Define some variables:
refht=10.
ustar=0.03
Uref=3.

##################################
# Section 1) Using models only.
###
# Initialize a 'run' object:
tsr=pyts.tsrun()

# Define the grid,
tsr.grid=pyts.tsGrid(center=refht,ny=5,nz=5,height=5,width=9,time_sec=1000,dt=0.5)

# Define a mean 'profile model',
prof_model=pyts.profModels.h2l(U,refht,ustar)

# and assign it to the run object,
tsr.profModel=prof_model
# These two steps can be completed in one as:
#tsr.profModel=pyts.profModels.h2l(U,refht,ustar)

# Next we define and assign a 'spectral model' to the run object,
tsr.specModel=pyts.specModels.tidal(ustar,refht)

# ... and define/assign a 'coherence model',
tsr.cohereModel=pyts.cohereModels.nwtc()

# ... and define/assign a 'stress model',
tsr.stressModel=pyts.stressModels.tidal(refht)

# Now simply 'call' the run oject to produce the TurbSim output.
turbsim_output=tsr()

##################################
# Section 2) Using models only.

# We can re-initialize the run-object using the 'clear' method.
tsr.reset() #

