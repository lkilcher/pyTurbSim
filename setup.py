# The setup script for installing pyTurbSim.
from numpy.distutils.core import setup, Extension
from numpy.distutils.command.install_data import install_data
from distutils.command.install_lib import install_lib
from distutils import log
from pyts import _version as ver
import os

## from subprocess import call
## class build_exe(Command):
##     def run(self,):
##         call(['pyinstaller','pyTurbSim.py'])


class chmod_install_lib(install_lib):

    """
    This class ensures that scripts and extensions get installed with
    read and execute permissions.
    """

    def run(self):
        install_lib.run(self)
        if os.name in ['posix']:
            for fn in self.get_outputs():
                if not (fn.endswith('.py') or fn.endswith('.pyc')):
                    mode = (((os.stat(fn).st_mode) | 0o555) & 0o7777)
                    log.info(('changing mode of %s to %o' % (fn, mode)))
                    os.chmod(fn, mode)


class chmod_install_data(install_data):

    """
    This class ensures that data files get installed with
    read permissions.
    """

    def run(self):
        install_data.run(self)
        if os.name in ['posix']:
            for fn in self.get_outputs():
                if not (fn.endswith('.py') or fn.endswith('.pyc')):
                    mode = (((os.stat(fn).st_mode) | 0o554) & 0o7777)
                    log.info(('changing mode of %s to %o' % (fn, mode)))
                    os.chmod(fn, mode)

setup(name='PyTurbSim',
      version=ver.__version__,
      description='Python implementation of TurbSim',
      author='Levi Kilcher',
      author_email='levi.kilcher@nrel.gov',
      url='http://lkilcher.github.io/pyTurbSim',
      packages=[ver.pkg_name,
                ver.pkg_name + 'io',
                ver.pkg_name + 'gui',
                ver.pkg_name + 'cohereModels',
                ver.pkg_name + 'phaseModels',
                ver.pkg_name + 'profModels',
                ver.pkg_name + 'runConfig',
                ver.pkg_name + 'specModels',
                ver.pkg_name + 'stressModels', ],
      data_files=[
          ('pyts/form', ['pyts/form/input.form', 'pyts/form/sumfile.form'])],
      scripts=['pyTurbSim.py'],
      ext_modules=[Extension(ver.pkg_name + 'tslib',
                             sources=['pyts/tslib/tslib.pyf',
                                      'pyts/tslib/tslib.f95',
                                      'pyts/tslib/lapack/lsame.f',
                                      'pyts/tslib/lapack/sdot.f',
                                      'pyts/tslib/lapack/spptrf.f',
                                      'pyts/tslib/lapack/sscal.f',
                                      'pyts/tslib/lapack/sspr.f',
                                      'pyts/tslib/lapack/stpsv.f',
                                      'pyts/tslib/lapack/xerbla.f', ],
                             extra_link_args=['-lgomp'],)],
      cmdclass={'install_lib': chmod_install_lib,
                'install_data': chmod_install_data, },
      )
