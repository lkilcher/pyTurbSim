.. _install:

Download and Install
====================

|pyts| is built primarily in Python, makes heavy use of the NumPy Python package, and has a small set of Fortran libraries. Therefore, prior to installing |pyts| you will first need to install,

1. A functioning Python 2.7 installation (with pip),
2. A Fortran compiler,
3. `Numpy <http://www.numpy.org>`_ >=1.6.

If you have not already installed these tools, doing so may be the difficult part of installing |pyts|. Most Linux/Unix/posix distributions provide binary packages that make it relatively easy to installing these tools. For Microsoft windows I recommend installing a Python package that includes all three of these tools (e.g. `Python(X,Y) <http://code.google.com/p/pythonxy/>`_) because they will *hopefully* be configured to function together seamlessly. On OSX (Mavericks) I have successfully installed these tools using `Homebrew <http://brew.sh>`_.

Once these tools have been successfully installed, |pyts| can be installed from a command line using pip::

    $ pip install PyTurbSim

That should do it!  For information on how to use |pyts| consult the :doc:`usage` page.

Installing without pip
----------------------

If the above-mentioned one-liner does not work (e.g. because your version of Python does not include pip), you can also simply download and install |pyts| from the source repository (http://github.com/lkilcher/pyTurbSim\ ). For example, if git is installed, you can::

   $ git clone http://github.com/lkilcher/pyTurbSim <download_location>

If `<download_location>` is not specified, the repository will be created in the current directory in a new `pyTurbSim` folder. Once you have downloaded |pyts|, you may either:

a) install it into your Python packages repository by executing the setup.py script::

     $ cd <download_location>
     $ python setup.py install

b) use it out of `<download_location>`.
