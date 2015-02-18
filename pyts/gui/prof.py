from .base import ConfigFrame, wx, np, mpl, FigCanvas, Figure, gts_wdr
#from pyts.main import buildModel
import copy


class profFigure(object):

    def __init__(self, panel, dpi):
        self.dpi = dpi
        self.fig = Figure((1.9, 3.4), dpi=self.dpi)
        self.canvas = FigCanvas(panel, -1, self.fig)
        self.fig.set_facecolor('w')
        ax = self.axes = self.fig.add_axes([0.24, 0.24, .7, 0.7])
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 0, wx.EXPAND | wx.ALL)
        panel.SetSizer(self.sizer)
        panel.Fit()

    def draw(self, parent):
        parent.inputs2config()
        ax = self.axes
        ax.cla()
        try:
            mdl = buildModel(copy.deepcopy(parent.config))
            ax.plot(
                mdl.profModel.u[:, mdl.grid.ihub[1]], mdl.grid.z, 'ro', ms=7, mec='none')
            zmx = np.max(mdl.grid.z)
            ztmp = np.arange(zmx / 40, zmx * 1.1, zmx / 40)
            ax.plot(mdl.profModel.model(ztmp), ztmp, 'k-', zorder=-5)
            ax.set_xlim([0, None])
            ax.set_ylim([0, None])
            ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(5))
        except:
            pass
        self.axes.set_xlabel('u [m/s]')
        self.axes.set_ylabel('z [m]')
        self.canvas.draw()


class profConfigFrame(ConfigFrame):
    # The keys in this list must match the input file option.

    # The keys in this dict should match the keys in the model_aliases dict.
    exclude_vars = {
        'H2L': ['inp_plexp', 'inp_zjet'],
        'LOG': ['inp_plexp', 'inp_zjet'],
        'PL': ['inp_zjet', 'inp_ustar'],
        'IEC': ['inp_zjet'],
        'JET': ['inp_plexp', 'inp_ustar'],
    }

    save_vars = {
        'cho_profmodel': 'WindProfileType',
        'inp_refheight': 'RefHt',
        'inp_refvel': 'URef',
        'inp_ustar': 'UStar',
        'inp_plexp': 'PLExp',
        'inp_zjet': 'ZJetMax',
        'inp_hflowang': 'HFlowAng',
        'inp_vflowang': 'VFlowAng',
    }

    def init_layout(self,):
        self.panel = wx.Panel(self)  # ,-1,style=wx.NO_BORDER)
        gts_wdr.profSetup(self.panel)

    @property
    def model(self,):
        return self.cho_profmodel.value

    def init_fig(self,):
        dpi = wx.ScreenDC().GetPPI()
        self.fig = profFigure(self.pnl_profile, dpi[0])

    def set_aliases(self,):
        self.cho_profmodel.aliases = {
            'H2L': ['H2O Log'],
            'PL': ['POWER'],
        }

    def init_bindings(self,):
        wx.EVT_CLOSE(self, self.OnCloseWindow)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.OnCloseWindow)
        self.btn_ok.Bind(wx.EVT_BUTTON, self.OnOk)
        self.inp_zjet.Bind(wx.EVT_TEXT, self.refresh)
        self.inp_refheight.Bind(wx.EVT_TEXT, self.refresh)
        self.inp_refvel.Bind(wx.EVT_TEXT, self.refresh)
        self.inp_plexp.Bind(wx.EVT_TEXT, self.refresh)
        self.inp_hflowang.Bind(wx.EVT_TEXT, self.refresh)
        self.inp_vflowang.Bind(wx.EVT_TEXT, self.refresh)
        self.cho_profmodel.Bind(wx.EVT_CHOICE, self.update)
