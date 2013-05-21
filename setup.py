# The setup script for creating a stand-alone HydroTurbSim windows (.exe) file.
from distutils.core import setup
import py2exe, sys

sys.argv.append('py2exe')

setup(console=['pyTurbSim.py'],
      options={'py2exe':{'bundle_files':1,'compressed':'True'}},
      zipfile = None,
      )
