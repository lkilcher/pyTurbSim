# The setup script for creating a stand-alone HydroTurbSim windows (.exe) file.
from distutils.core import setup
import py2exe, sys

sys.argv.append('py2exe')

setup(console=['pyTurbSim.py'],
      #data_files=[(r'c:\Python\lib\site-packages\numpy\fft',['fftpack_lite.pyd']),],
      #options={'py2exe':{'bundle_files':1,'compressed':'True','includes':r'numpy\fft\fftpack_lite.pyd'}},
      #options={'py2exe':{'bundle_files':1,'compressed':'True','packages':'numpy.fft'}},
      options={'py2exe':{'bundle_files':1,'compressed':True,}},
      zipfile = None,
      )
