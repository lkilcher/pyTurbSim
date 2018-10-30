import numpy as np
from .base import ConfigFrame
import wx
from . import gTurbSim_wdr as gts_wdr


class cho_windtype_turbclass(object):

    def __init__(self, cho_type, cho_class):
        self.windtype = cho_type
        self.turbclass = cho_class

    def Disable(self,):
        self.windtype.Disable()
        self.turbclass.Disable()

    def Enable(self,):
        self.windtype.Enable()
        self.turbclass.Enable()

    @property
    def value(self,):
        if self.windtype.value in ['NTM', 'ETM']:
            return self.windtype.value
        else:
            return '%d%s' % (self.turbclass.value, self.windtype.value)

    @value.setter
    def value(self, val):
        if val in ['NTM', 'ETM']:
            self.turbclass.value = '--'
            self.windtype.value = val
        else:
            self.turbclass.value = val[0]
            self.windtype.value = val[1:]


class cohParam(object):

    def __init__(self, inp_a, inp_b):
        self.a = inp_a
        self.b = inp_b
        self.data = np.empty(2, dtype=np.float32)

    def Disable(self, ):
        self.a.Disable()
        self.b.Disable()

    def Enable(self, ):
        self.a.Enable()
        self.b.Enable()

    @property
    def value(self,):
        if self.a.value is None:
            return None
        elif self.b.value == '--':
            self.b.value = 0
        self.data[:] = (self.a.value, self.b.value)
        return self.data

    @value.setter
    def value(self, val):
        if val is None:
            self.a.value = 'default'
            self.b.value = '--'
        else:
            self.data[:] = val
            self.a.value = self.data[0]
            self.b.value = self.data[1]


class turbConfigFrame(ConfigFrame):

    save_vars = {
        'cho_turbmodel': 'TurbModel',
        'inp_ustar': 'UStar',
        'inp_Ri': 'RICH_NO',
        'inp_z0': 'Z0',
        'inp_zi': 'ZI',
        'inp_upwp': 'PC_UW',
        'inp_vpwp': 'PC_VW',
        'inp_upvp': 'PC_UV',
        'cho_iec_turbclass_windtype': 'IEC_WindType',
        'inp_iecturbc': 'IECturbc',
        'inp_etmc': 'ETMc',
        'cho_iecstandard': 'IECstandard',
        'inp_cohexp': 'CohExp',
        'inp_cohU': 'IncDec1',
        'inp_cohV': 'IncDec2',
        'inp_cohW': 'IncDec3',
        'inp_addkh': 'WrACT',
    }

    exclude_vars = {
        'IECKAI': ['inp_Ri', 'inp_zi', 'inp_ustar',
                   'inp_cohexp', 'inp_cohexp',
                   'inp_cohU', 'inp_cohV', 'inp_cohW',
                   'inp_upwp', 'inp_upvp', 'inp_vpwp', ],
        'IECVKM': ['inp_Ri', 'inp_zi', 'inp_ustar', 'inp_cohexp',
                   'inp_cohU', 'inp_cohV', 'inp_cohW',
                   'inp_upwp', 'inp_upvp', 'inp_vpwp', ],
        'SMOOTH': ['cho_iec_turbclass_windtype', 'inp_iecturbc',
                   'cho_iecstandard', 'inp_etmc', ],
        'TIDAL': ['cho_iec_turbclass_windtype', 'inp_iecturbc',
                  'cho_iecstandard', 'inp_etmc',
                  'inp_Ri', 'inp_z0', 'inp_zi'],
        'RIVER': ['cho_iec_turbclass_windtype', 'inp_iecturbc',
                  'cho_iecstandard', 'inp_etmc',
                  'inp_Ri', 'inp_z0', 'inp_zi'],
        'GP_LLJ': ['cho_iec_turbclass_windtype', 'inp_iecturbc',
                   'cho_iecstandard', 'inp_etmc', ],
        'WF_UPW': ['cho_iec_turbclass_windtype', 'inp_iecturbc',
                   'cho_iecstandard', 'inp_etmc', ],
        'WF_07D': ['cho_iec_turbclass_windtype', 'inp_iecturbc',
                   'cho_iecstandard', 'inp_etmc', ],
        'WF_14D': ['cho_iec_turbclass_windtype', 'inp_iecturbc',
                   'cho_iecstandard', 'inp_etmc', ],
        'NWTCUP': ['cho_iec_turbclass_windtype', 'inp_iecturbc',
                   'cho_iecstandard', 'inp_etmc', ],
    }

    @property
    def model(self,):
        return self.cho_turbmodel.value

    def set_aliases(self,):
        #self.cho_turbmodel={}
        self.cho_iec_turbclass_windtype = cho_windtype_turbclass(
            self.cho_iecwindtype, self.cho_iecclass)
        self.inp_cohU = cohParam(self.inp_cohUa, self.inp_cohUb)
        self.inp_cohV = cohParam(self.inp_cohVa, self.inp_cohVb)
        self.inp_cohW = cohParam(self.inp_cohWa, self.inp_cohWb)

    def onKHCheckBox(self, event):
        self.btn_khconfig.Enable(self.inp_addkh.value)

    def init_layout(self,):
        self.panel = wx.Panel(self)  # ,-1,style=wx.NO_BORDER)
        gts_wdr.turbSetup(self.panel)

    def init_bindings(self,):
        # Set the bindings:
        self.btn_khconfig.Enable(self.inp_addkh.value)
        wx.EVT_CLOSE(self, self.OnCloseWindow)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.OnCloseWindow)
        self.btn_ok.Bind(wx.EVT_BUTTON, self.OnOk)
        self.cho_turbmodel.Bind(wx.EVT_CHOICE, self.update)
        self.inp_addkh.Bind(wx.EVT_CHECKBOX, self.onKHCheckBox)
        self.btn_khconfig.Bind(wx.EVT_BUTTON, self.onKHConfig)

    def onKHConfig(self, event):
        try:
            self.frm_ConfigProf.Raise()
        except:
            self.frm_ConfigProf = KHBillowsConfigFrame(
                self, wx.ID_ANY, 'Kelvin-Helmholtz Billows - Settings')
            self.frm_ConfigProf.Show(True)


class KHBillowsConfigFrame(ConfigFrame):

    save_vars = {
        'inp_eventpath': 'CTEventPath',
        'cho_eventfile': 'CTEventFile',
        'inp_randomize': 'Randomize',
        'inp_distscl': 'DistScl',
        'inp_ctlz': 'CTLz',
        'inp_ctly': 'CTLy',
        'inp_ctt': 'CTStartTime',
    }

    exclude_vars = {
        True: ['inp_distscl', 'inp_ctlz', 'inp_ctly'],
        False: []
    }

    @property
    def model(self,):
        return self.inp_randomize.value

    def init_layout(self,):
        self.panel = wx.Panel(self)  # ,-1,style=wx.NO_BORDER)
        gts_wdr.kh_billows(self.panel)

    def init_bindings(self,):
        # Set the bindings:
        wx.EVT_CLOSE(self, self.OnCloseWindow)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.OnCloseWindow)
        self.btn_ok.Bind(wx.EVT_BUTTON, self.OnOk)
        self.inp_randomize.Bind(wx.EVT_CHECKBOX, self.update)
