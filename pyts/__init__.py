"""
pyTurbSim is a python-implementation of the National Wind Technology Center's (NWTC) 'TurbSim' program.  pyTurbSim is the official water-turbulence simulation tool for hydrokinetic turbine device simulation (a.k.a. HydroTurbSim), and is also designed to be a valuable development and testing platform for NREL's 'TurbSim' tool.

The NWTC is a center at the Department of Energy's (DOE) National Renewable Energy Lab (NREL).  The DOE provided funding for development of these tools.  

-- Nomenclature --
Throughout the documentation, the term 'TurbSim' is used to refer to both pyTurbSim and the original TurbSim tool ('o-TurbSim') unless specified specifically.

-- Background --
TurbSim is a program for producing simulations of turbulent velocity time-series for input to wind- and water-turbine device simulation tools (e.g. the NWTC's FAST).  TurbSim outputs 2-D planes (i.e. y-z) of 3-component velocity (u,v,w) time-series [1].

-- Notes --
 [1] TurbSim implicitly makes the 'frozen flow hypothesis', and so the time-dimension can also be considered the x-dimension.

"""
from main import tsrun
from base import tsGrid
import profModels
import specModels
import cohereModels
import stressModels
import io
from _version import __version__,__version_date__,__prog_name__

# Some shortcuts to the models:
pm=profModels
sm=specModels
cm=cohereModels
rm=stressModels


