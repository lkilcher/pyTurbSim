.. _install:

Download and Install
====================

|pyts| can be installed in several different ways depending on your system.  At the most general level, assuming you have Python and NumPy installed, you should be able to simply download |pyts| from the repository (http://github.com/lkilcher/pyTurbSim\ ). For example, if git is installed, you can::
   $ git clone http://github.com/lkilcher/pyTurbSim <download_location>

If `<download_location>` is not specified, the repository will be created in the current directory in a new `pyTurbSim` folder. Once you have downloaded |pyts|, you may either:

a) install it into your Python packages repository by executing the setup.py script::

     $ cd <download_location>
     $ python setup.py install

b) use it out of `<download_location>`.

For information on how to use |pyts| consult the :doc:`usage` page.
For more specific guidance on installing |pyts|, see below...

Dependencies
------------

- |pyts| is known to work with Python 2.7 and numpy 1.6.
- The gui (gTurbSim) also requires wxPython (2.8).
- gfortran is required to compile tslib (the setup.py file does this). In MS Windows try installing `MinGW <http://www.mingw.org/>`_\ .

