from ..main import tsdata, tsrun  # These are used only to identify object types.
import superaxes as supax
import psd
from base import indx, mpl
import numpy as np


class axesForm(object):
    """A base 'axesForm' class for for quickly plotting TurbSim data.

    Parameters
    ----------
    xlim : iterable(2) (default: [None, None])
           Specify the xlims of the axes of these plots.  The default
           will simply select the limits automatically.
    ylim : iterable(2) (default: [None, None])
           Specify the ylims of the axes of these plots.  The default
           will simply select the limits automatically.
    xscale : ('log' or 'linear')
        specify whether the x-scale should be logarithmic or linear.
    yscale : ('log' or 'linear')
        specify whether the y-scale should be logarithmic or linear.
    """
    method_map = {tsdata: '_calc_tsdata', tsrun: '_calc_tsrun'}
    hide_ylabels = False
    _lin_x_scale = 0

    def __init__(self,
                 xlim=[None, None], ylim=[None, None],
                 xscale='linear', yscale='linear',):
        self.xlim = xlim
        self.ylim = ylim
        self.xscale = xscale
        self.yscale = yscale

    def finalize(self, axes):
        """
        This function 'finishes' the `axes` according to the
        specifications in this axesForm.

        Parameters
        ----------
        axes : A :class:`superaxes.axgroup` instance.
        """
        axes.hide('xticklabels', ax=axes[-1])
        if self.hide_ylabels:
            axes.hide('yticklabels')
        if not self.hide_ylabels and hasattr(self, '_ylabel'):
            for ax in axes:
                ax.set_ylabel(self._ylabel)
        if hasattr(self, '_xlabel'):
            axes[-1].set_xlabel(self._xlabel)
        if hasattr(self, '_title'):
            axes[0].set_title(self._title)
        if hasattr(self, '_grid_x'):
            for ax in axes:
                for val in self._grid_x:
                    ax.axvline(val, linestyle=':', color='k', zorder=-10)
        if hasattr(self, '_labels'):
            for ax in axes:
                ax.annoteCorner(self._labels[ax.comp], pos='ul')
        if hasattr(self, 'xtick_n'):
            for ax in axes:
                ax.xaxis.set_major_locator(
                    mpl.ticker.MaxNLocator(self.xtick_n))
        for ax in axes:
            ax.set_xlim(self.xlim)
        for ax in axes:
            ax.set_ylim(self.ylim)

    def _calc(self, obj, comp):
        """
        Call the appropriate 'calc' method depending on the object
        class.

        Parameters
        ----------
        obj : object
              An object containing data/information to be plotted.
        comp : int,str
               The component (u,v,w or 0,1,2) to compute.

        Returns
        -------
        x : array_like
            The x data to plot.
        y : array_like
            The y data to plot.

        Notes
        -----

        This method is a parser for the individual '_calc_<obj>'
        methods. It utilizes the :attr:`method_map` to determine which
        method should be called for each `obj` object type.

        """
        if comp.__class__ is str:
            comp = indx[comp]
        for cls, meth in self.method_map.iteritems():
            if isinstance(obj, cls):
                if not hasattr(self, meth):
                    return np.NaN, np.NaN
                return getattr(self, meth)(obj, comp)
        raise Exception('Object type %s not recognized for %s axes-type' %
                        (obj.__class__, self.__class__))

    def plot(self, obj, axes, **kwargs):
        """
        Plot the data in `obj` to `axes`.

        Parameters
        ----------
        obj : object
              An object containing data to be plotted.
        axes : :class:`superaxes.axgroup` instance
               The axes into which that data should be plotted.
        """
        for ax in axes:
            x, y = self._calc(obj, ax.comp)
            # print x, y, self._lin_x_scale
            ax.plot(x / (10 ** self._lin_x_scale), y, **kwargs)
            ax.set_xscale(self.xscale)
            ax.set_yscale(self.yscale)

    @property
    def _xlabel(self,):
        if self._lin_x_scale == 0:
            return '$\mathrm{[m^2s^{-2}]}$'
        else:
            return '$\mathrm{[10^{%d}m^2s^{-2}]}$' % self._lin_x_scale


class prof(axesForm):
    "A base axesForm for plotting vertical profiles."
    yax = 'z'
    _ylabel = '$z\,\mathrm{[m]}$'
    hrel = 0.6
    xtick_n = 3


class velprof(prof):
    """A 'mean velocity profile' axesForm format.

    See also
    --------
    :class:`prof`
    :class:`axesForm`
    """
    xax = 'vel'
    _title = 'Mean Velocity'
    _xlabel = '$\mathrm{[m/s]}$'

    def _calc_tsdata(self, tsdat, comp, igrid=None):
        """
        The function that calculates x,y values for plotting
        :class:`.tsdata` objects.
        """
        return tsdat.uprof[comp, :, tsdat.ihub[1]], tsdat.z

    def _calc_tsrun(self, tsr, comp, igrid=None):
        """
        The function that calculates x,y values for plotting
        :class:`.tsrun` objects.
        """
        return tsr.prof[comp, :, tsr.grid.ihub[1]], tsr.grid.z


class tkeprof(prof):
    """A 'tke profile' axesForm.

    See also
    --------
    :class:`prof`
    :class:`axesForm`
    """
    xax = 'tke'
    _title = 'tke'
    #_lin_x_scale = -2  # Units are 10^-2

    def _calc_tsdata(self, tsdat, comp, igrid=None):
        return tsdat.tke[comp, :, tsdat.ihub[1]], tsdat.z

    def _calc_tsrun(self, tsr, comp, igrid=None):
        return tsr.spec.tke[comp, :, tsr.grid.ihub[1]], tsr.grid.z


class Tiprof(prof):
    """A Turbulence intensity axesForm

    See also
    --------
    :class:`prof`
    :class:`axesForm`
    """
    xax = 'Ti'
    _title = 'Ti'
    _lin_x_scale = 0
    _ylabel = '%'

    def _calc_tsdata(self, tsdat, comp, igrid=None):
        tmp = (100 * np.std(tsdat.uturb[comp, :, tsdat.ihub[1]], axis=-1)
               / tsdat.uprof[0, :, tsdat.ihub[1]])
        return tmp, tsdat.z

    def _calc_tsrun(self, tsr, comp, igrid=None):
        return (100 * np.sqrt(tsr.spec.tke[comp, :, tsr.grid.ihub[1]])
                / tsr.prof.u[:, tsr.grid.ihub[1]],
                tsr.grid.z)


class stressprof(tkeprof):
    """A 'Reynold's stress profile' axesForm.

    See also
    --------
    :class:`prof`
    :class:`axesForm`
    """
    xax = 'tke'
    _title = 'stress'
    _lin_x_scale = -2  # Units are 10^-2
    _grid_x = [0]
    _labels = {'u': r"$\overline{u'v'}$",
               'v': r"$\overline{u'w'}$",
               'w': r"$\overline{v'w'}$"}

    def _calc_tsdata(self, tsdat, comp, igrid=None):
        igrid = igrid or tsdat.ihub[1]
        return tsdat.stress[comp, :, igrid], tsdat.z

    def _calc_tsrun(self, tsr, comp, igrid=None):
        igrid = igrid or tsr.grid.ihub[1]
        return tsr.stress.array[comp, :, igrid], tsr.grid.z


class spec(axesForm):
    """A 'spectral' axesForm.

    Parameters
    ----------
    window_time_sec : float
                      the length of the fft window (seconds).
    igrid : tuple,list (2), *optional* (default: i_hub)
            The spatial-index of the grid-point that should be
            plotted.

    Notes
    -----

    This axesForm defaults to have 'log' x- and y-scales.

    See also
    --------
    :class:`axesForm`
    """
    hrel = 1
    _title = 'spectrum'
    yax = 'spec'
    xax = 'freq'
    _xlabel = '$f\,\mathrm{[Hz]}$'
    _ylabel = '$\mathrm{[m^2s^{-2}/Hz]}$'

    def __init__(self, window_time_sec=600, igrid=None,
                 xscale='log', yscale='log',
                 **kwargs):
        axesForm.__init__(self, xscale=xscale, yscale=yscale, **kwargs)
        self.window_time = window_time_sec
        self.igrid = igrid

    def _calc_tsdata(self, tsdat, comp, igrid=None):
        nfft = int(self.window_time / tsdat.dt)
        nfft += np.mod(nfft, 2)
        igrid = igrid or self.igrid or tsdat.ihub
        tmp = psd.psd(tsdat.uturb[comp][igrid],
                      1. / tsdat.dt,
                      nfft)
        # print tmp
        return tmp

    def _calc_tsrun(self, tsr, comp, igrid=None):
        igrid = igrid or self.igrid or tsr.grid.ihub
        return tsr.grid.f, tsr.spec[comp][igrid]


class cohere(axesForm):
    """
    A 'coherence' plotting format for showing coherence between two
    points.

    Parameters
    ----------
    window_time_sec : float
                      the length of the fft window (seconds).
    igrid0 : tuple,list (2), *optional* (default: i_hub)
             The first spatial-index from which to estimate+plot
             coherence.
    igrid1 : tuple,list (2), *optional* (default: (0,0))
             The second spatial-index from which to estimate+plot
             coherence.

    Notes
    -----

    This axesForm defaults to have a 'log' x-scale, and to have a
    linear y-axis with ylim=[0, 1].

    See also
    --------
    :class:`axesForm`
    """
    hrel = 1
    _title = 'coherence'
    xax = 'freq'
    yax = 'coh'
    _xlabel = '$f\,\mathrm{[Hz]}$'

    def __init__(self, window_time_sec=600, igrid0=None, igrid1=None,
                 xscale='log', ylim=[0, 1],
                 **kwargs):
        axesForm.__init__(self, xscale=xscale, ylim=ylim, **kwargs)
        self.window_time = 600
        self.igrid0 = igrid0
        self.igrid1 = igrid1

    def _calc_tsdata(self, tsdat, comp, igrid0=None, igrid1=None):
        nfft = int(self.window_time / tsdat.dt)
        nfft += np.mod(nfft, 2)
        igrid0 = igrid0 or self.igrid0 or tsdat.ihub
        igrid1 = igrid1 or self.igrid1 or (0, 0)
        return psd.coh(tsdat.uturb[comp][igrid0],
                       tsdat.uturb[comp][igrid1],
                       1. / tsdat.dt, nfft)

    def _calc_tsrun(self, tsr, comp, igrid0=None, igrid1=None):
        igrid0 = tsr.grid.sub2ind(igrid0 or self.igrid0 or tsr.grid.ihub)
        igrid1 = tsr.grid.sub2ind(igrid1 or self.igrid1 or (0, 0))
        return tsr.grid.f, tsr.cohere.calcCoh(tsr.grid.f,
                                              comp, igrid0, igrid1) ** 2


class FigAxForm(supax.sfig):
    """The 'figure' class that uses and handles :class:`axesForm`s.

    Parameters
    ----------
    fignum : integer,string
             The figure number, or string, into which the data will be
             plotted.
    axforms : list of axForms (e.g. :class:`velprof`, :class:`tkeprof`)
              These are the axes formats that will be plotted.
    comp : list of velocity components (0,1,2 or 'u','v','w')
    axsize : float, tuple, list (2)
             The size of the axes. If 2 parameters are specified this
             sets they set the horizontal and vertical size of the
             axes.
    frame : tuple(4) ,list(4)
            This specifies the border around the axes (left, right,
            bottom, top)
    gap : tuple(2), list(2)
          This specifies the gap between axes in the horizontal and
          vertical directions.
    tightgap : float
               This specifies the horizontal spacing between axes that
               have the same type of y-axis (specified in the formats
               'yax' attribute).

    Other inputs are passed directly to :meth:`superaxes.sfig.__init__`.

    Notes
    -----
    This will create an NxM axes-grid, where N=len(comp), and
    M=len(axforms).

    The width of each axes is scaled by the 'hrel' attribute of each
    axform.

    """
    def __init__(self,
                 fignum,
                 axforms=[],
                 comp=['u', 'v', 'w'],
                 axsize=2,
                 frame=[.6, .3, 1, .3],
                 gap=[.2, 1],
                 tightgap=.2,
                 **kwargs):

        if len(axforms) == 0:
            raise Exception('At least one axes-type \
            instance must be provided.')

        sharex = np.tile(np.arange(len(axforms), dtype=np.uint8) + 1,
                         (len(comp), 1))
        sharey = np.tile(np.arange(len(axforms), dtype=np.uint8) + 1,
                         (len(comp), 1))

        hspacer = supax.simpleAxSpacer(len(axforms), axsize, gap[1], frame[2:])
        vspacer = supax.simpleAxSpacer(len(comp), axsize, gap[0], frame[:2],
                                       vertical=True)

        last_yax = None
        for idx, axt in enumerate(axforms):
            if axt.yax == last_yax:
                sharey[:, idx] = sharey[:, idx - 1]
                hspacer.gap[idx] = tightgap
                axt.hide_ylabels = True
            last_yax = axt.yax
            if hasattr(axt, 'hrel'):
                hspacer.axsize[idx] *= axt.hrel
        axp = supax.axPlacer(vspacer, hspacer)
        supax.sfig.__init__(self, fignum, axp,
                            sharex=sharex, sharey=sharey, **kwargs)
        self.comp = comp
        for idx, axt in enumerate(axforms):
            for c, ax in zip(comp, self.sax[:, idx]):
                ax.comp = c
        self.axforms = axforms

    def plot(self, obj, **kwargs):
        """
        Plot the data in `obj` to the figure according to the plotting formats.

        Parameters
        ----------
        obj : tsdata, tsrun, turbdata
              A data or turbsim object to plot.
        """
        for idx, axt in enumerate(self.axforms):
            axt.plot(obj, self.sax[:, idx], **kwargs)

    def finalize(self,):
        """
        Finalize the figure according to the plotting formats.
        """
        for idx, axt in enumerate(self.axforms):
            axt.finalize(self.sax[:, idx])
        for c, ax in zip(self.comp, self.ax[:, 0]):
            p = ax.get_position().ymax
            self.fig.text(0.02, p, '$' + c + '$', va='top', ha='left',
                          size='x-large', backgroundcolor='w')


def summfig(fignum=400, axforms=[velprof(), spec(600)], **kwargs):
    return FigAxForm(fignum, axforms=axforms, **kwargs)
