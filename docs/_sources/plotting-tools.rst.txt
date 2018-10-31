Plotting Tools
==============

|pyts| is equipped with a flexible set of plotting tools for plotting
|pyts| output and comparing it to target (input) statistics. For
example, the following code performs a |pyts| run and compares the
mean profile and spectrum with the targets.

Begin by importing |pyts| and its :mod:`.plot` package::

  import TurbGen.api as pyts
  import TurbGen.plot.api as plt

Generate some |pyts| data
-------------------------

Before we plot anything we need to create something to plot. To do
this we begin by defining some parameters, and initialize the
:class:`.TGrun` object, including creating the :func:`.RectGrid`::

  refht = 4
  ustar = 0.03
  Uref = 3.
  
  # This creates a PyTurbSim 'run object':
  tgr = TurbGen.TGrun()
  
  tgr.grid = TurbGen.RectGrid(center=refht,
                         ny=3,
                         nz=5,
                         height=5,
                         width=5,
                         time_sec=3000,
                         dt=0.5,)

Now specify the profile, spectral, stress and coherence models that
you wish to simulate, and run PyTurbSim (by calling ``tgr``)::

  tgr.prof = TurbGen.profModels.h2l(Uref, refht, ustar)
  tgr.spec = TurbGen.specModels.tidal(ustar, refht)
  tgr.cohere = TurbGen.cohereModels.nwtc()
  tgr.stress = TurbGen.stressModels.tidal(ustar, refht)

  # Run PyTurbSim:
  out = tgr()

``out`` now contains a :class:`.tsdata` object which holds
the output of the PyTurbSim run ``tgr``.

Basic plotting
--------------

Now that we have something to plot, we are ready to create a
'PyTurbSim summary plotting figure'::

  fig = plt.summfig()

Here :func:`summfig` is a wrapper function that returns a
:class:`.FigAxForm` object. These :class:`.FigAxForm` objects are
toolboxes for plotting several statistics of PyTurbSim and TurbSim
output.  To plot our PyTurbSim output, ``out``, we simply::

  fig.plot(out, color='k')

When the :func:`plot <TurbGen.plot.axform.FigAxForm.plot>` method receives a
|pyts| 'run' object it plots the target values::
  
  fig.plot(tgr, color='r', linestyle='--')

Note that this plot method accepts all of the normal
:func:`matplotlib.pyplot.plot` ``**kwargs``.  We now clean-up
(``finalize``) and save the figure::

  fig.finalize()
  fig.savefig('BasicExample.png')

.. plot:: examples/plotting.py


Advanced Usage
--------------

But what if you want to plot more than just the mean velocity profile and the spectrum?  :mod:`TurbGen.plot` can do that too. You simply set-up your figure to plot whichever types of plots you want::

  fig = plt.summfig(axforms=[plt.axform.velprof([0, 3.5]),
                             plt.axform.tkeprof(),
                             plt.axform.stressprof(),
                             plt.axform.spec(),
                             plt.axform.cohere(), ], 
                             nfft=1024,
                             )

Here we are selecting different 'axes forms' types from the :mod:`TurbGen.plot.axform` module.  Each of these :class:`.axesForm` objects can be customized to control various properties of the axes.

In this case, we are seeking to plot the mean velocity profile, the turbulent energy profiles, the stress profiles, the spectra and the coherence. That's a lot of information! Fortunately, all of these statistics can be computed for our PyTurbSim output, and run. You may also notice that we have also specified ``nfft=1024``, which tells the plotter to use that number of points when computing ``spec`` and ``cohere``.

To plot all of these statistics, we simply follow the same steps above::

  fig.plot(out, color='k')
  fig.plot(tgr, color='r', linestyle='--')
  fig.finalize()
  fig.savefig('AdvancedExample.png')

This gives a comparison of PyTurbSim output to targets for this list of variables, with just a few lines of code!

.. plot:: examples/plotting2.py

