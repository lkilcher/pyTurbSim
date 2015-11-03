.. _usage:

Usage
=====

|pyts| was designed to meet the needs of several different user
groups. To meet that objective it has three primary operational
modes/interfaces. Those modes are described below.  Once |pyts| is
properly :doc:`installed <install>`, all of these modes should work.

1) Input files
--------------

This mode is designed to mimic the |ots| interface. It is
designed for use by device developers and other users familiar with
the |ots| program who want output that is consistent with
predifined models built into TurbSim. In this mode pyTurbSim reads
|ots| input files and writes out binary data in the same format
as |ots|. This mode can be run from a standard (i.e. DOS, UNIX)
command line and is well suited for interfacing with FAST and other
device simulation tools in the same way that |ots| does.  For
more information on this mode, see the docstring in the
:mod:`.pyts.runInput` docstring.

To run |pyts| in this mode on the file 'TurbSim.inp' from the
command line do::

  $ pyTurbSim.py TurbSim.inp

Alternatively, this mode can be used from an interactive python shell
by doing::

  >>> from pyts.runInput.main import readConfig, run, write
  >>> config = readConfig('TurbSim.inp')
  >>> tsdat = run(config)
  >>> write(tsdat, config, 'TurbSim')

These two approaches produce the same output. The first allows the
user to run |pyts| without ever entering an interactive python
shell, the latter provides the user with an opportunity to view the
output data, ``tsdat``, without reloading it from a file.

The source code for this mode is contained in the :mod:`pyts.runInput` package.

2) Advanced programming interface (API)
---------------------------------------

This interface was designed for researchers who wish to develop new
methods and models for simulating turbulence, and/or want to control
the statistics of |pyts| output explicitly. This api is the core
interface of |pyts| (the other two are wrappers).  As a starting point
for using this interface checkout the :doc:`API documentation <api/pyts>`. Or start
navigating the api interactively by importing it::
   import pyts.api as pyts

More specifically, the :file:`examples/api.py` file includes an
overview of how to begin using |pyts|. The contents of that file is:

.. literalinclude:: ../../examples/api.py

3) Graphical user interface (GUI)
---------------------------------

The GUI was developed for reading and writing TurbSim input files.
The gui was designed to help new users of TurbSim in understanding
and writing input files. The gui can be used to run |pyts| or
|ots| (if an |ots| executable can be found in path).
'gTurbSim' can be run from a command line in the |pyts|
directory::

   $ python gTurbSim.py TurbSim.inp

The source code for this mode is contained in the :mod:`.pyts.gui` package.


Reading output files
--------------------

pyTurbSim comes with the ability to read (and write) TurbSim '.wnd', '.bl' (Bladed format) and '.bts' (AeroDyn/TurbSim format) files.  To read these files:
1) 'import pyts.tsio'
2) You can either use:

   a) :mod:`pyts.io.bladed` or :mod:`pyts.io.aerodyn` to return an
      array of the turbulence timeseries, or

   b) :func:`pyts.tsio.readModel` to read the appropriate data file, and
      also load information from the config (.inp) file to create a
      'tsdata' object that includes both the array and also the
      config and turbModel objects.
