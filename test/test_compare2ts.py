from TurbGen.runInput import main as tg
from os import path, mkdir
import TurbGen.io.main as tsio
import TurbGen.plot.api as pt

thisdir = path.dirname(path.abspath(__file__))
ts_file_type = '.wnd'

datdir = thisdir + '/data/'


def test_tidal(make_data=False, figdir=None):

    cfg = tg.readInput(thisdir + '/inp_files/Tidal.inp')
    tgr = tg.cfg2tgrun(cfg)
    dat = tgr()

    if make_data:
        dat.write_hdf5(thisdir + '/data/Tidal.h5')

    cdat = tsio.read.hdf5(thisdir + '/data/Tidal.h5')

    assert cdat == dat

    if figdir is not None:
        tsdat = tsio.readModel(thisdir + '/data/ts/Tidal' + ts_file_type)
        fg = show_comparison(tgr, dat, tsdat, name='Tidal', fignum=1001)
        fg.fig.savefig(figdir + 'Tidal.png', res=300)


def test_smooth(make_data=False, figdir=None):

    cfg = tg.readInput(thisdir + '/inp_files/Smooth.inp')
    tgr = tg.cfg2tgrun(cfg)
    dat = tgr()

    if make_data:
        dat.write_hdf5(thisdir + '/data/Smooth.h5')

    cdat = tsio.read.hdf5(thisdir + '/data/Smooth.h5')

    assert cdat == dat

    if figdir is not None:
        tsdat = tsio.readModel(thisdir + '/data/ts/Smooth' + ts_file_type)
        fg = show_comparison(tgr, dat, tsdat, name='Smooth', fignum=1002)
        fg.fig.savefig(figdir + 'Smooth.png', res=300)


def test_IecKai(make_data=False, figdir=None):

    cfg = tg.readInput(thisdir + '/inp_files/IecKai.inp')
    tgr = tg.cfg2tgrun(cfg)
    dat = tgr()

    if make_data:
        dat.write_hdf5(thisdir + '/data/IecKai.h5')

    cdat = tsio.read.hdf5(thisdir + '/data/IecKai.h5')

    assert cdat == dat

    if figdir is not None:
        tsdat = tsio.readModel(thisdir + '/data/ts/IecKai' + ts_file_type)
        fg = show_comparison(tgr, dat, tsdat, name='IEC-KAIMAL', fignum=1003)
        fg.fig.savefig(figdir + 'IECKAI.png', res=300)


def test_IecVkm(make_data=False, figdir=None):

    cfg = tg.readInput(thisdir + '/inp_files/IecVkm.inp')
    tgr = tg.cfg2tgrun(cfg)
    dat = tgr()

    if make_data:
        dat.write_hdf5(thisdir + '/data/IecVkm.h5')

    cdat = tsio.read.hdf5(thisdir + '/data/IecVkm.h5')

    assert cdat == dat

    if figdir is not None:
        tsdat = tsio.readModel(thisdir + '/data/ts/IecVkm' + ts_file_type)
        fg = show_comparison(tgr, dat, tsdat, name='IEC-VonKarman', fignum=1004)
        fg.fig.savefig(figdir + 'IECVKM.png', res=300)


def show_comparison(tgrun, tgdat, tsdat, name='???', fignum=None):
    """Compare TurbGen data/run to TurbSim data."""

    # This creates a 'figure object'
    fg = pt.FigAxForm(fignum,  # fignum
                      nfft=1024,  # specify the nfft for spectral plots.
                      # Here you can specify which variables to compare:
                      # (see options in the pt.axform module)
                      axforms=[pt.axform.velprof(),
                               # Specify some axes parameters here:
                               pt.axform.tkeprof(xlim=[0, 10]),
                               pt.axform.spec(ylim=[1e-4, 1e4]),
                               ],
                      # Retitle the figure:
                      title=name.upper().replace('_', '-') + ' spectral model',
                      # This specifies the border space around
                      # the axes [bot, top, left, right] (in
                      # inches). Note that I've made space for the
                      # legend on the right:
                      frame=[.7, .5, 1.1, 1.5],
                      )
    # Now comes the true power of these 'axforms':
    # We can simply plot tsdat objects in one line:
    fg.plot(tsdat, color='r', label='TS')
    # After supplying the data object these plot calls can take
    # all of the arguments as defined in matplotlib.pyplot.plot
    fg.plot(tgdat, color='b', linestyle='-', marker='.', label='TG')
    # When calling fg.plot on a tgrun object, these axform
    # objects plot the theoretical line:
    fg.plot(tgrun, color='g', label='TG Target')
    # Add a legend to the upper-right axes:
    # (Note here that indexing the 'figure object' gives axes in
    # the grid)
    fg[0, -1].legend(loc='upper left',
                     bbox_to_anchor=(1.02, 1),
                     prop=dict(size='medium'),
                     )
    # This does some 'tidying up' of the figure:
    fg.finalize()
    return fg
