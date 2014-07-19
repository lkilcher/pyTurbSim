import wx
import numpy as np

import gTurbSim_wdr as gts_wdr
import io as tsio

import matplotlib as mpl
mpl.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas, NavigationToolbar2WxAgg as NavigationToolbar
mpl.rc('font',size=10)

class ConfigFrame(wx.Frame):

    def __init__(self, parent, id, title,
        pos = wx.DefaultPosition, size = wx.DefaultSize,
        style = wx.CLOSE_BOX | wx.CAPTION ):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        self.config=parent.config
        self.parent=parent

        self.init_layout()

        # Assign inputs.
        self.init_inputs()

        if hasattr(self,'init_fig'):
            # Draw the figure
            self.init_fig()

        self.update(wx.EVT_CHOICE)
            
        # Assign the gui bindings.
        self.init_bindings()

        self.Fit()

    def update(self,event):
        if hasattr(self,'fig'):
            self.fig.draw(self)
        if hasattr(self,'exclude_vars'):
            for vr in self.save_vars:
                attr=getattr(self,vr)
                if vr in self.exclude_vars[self.model]:
                    attr.Disable()
                else:
                    attr.Enable()
        
    def config2inputs(self,):
        for nm,vr in self.save_vars.iteritems():
            getattr(self,nm).value=self.config[vr]

    def inputs2config(self,):
        for nm,vr in self.save_vars.iteritems():
            vl=getattr(self,nm).value
            self.config[vr]=vl
            
    def init_inputs(self,):
        """
        Assign the input fields to names on this object.
        """
        for obj in self.panel.Children: #wxDesigner does not allow defining variables, but it does allow names, so we use this as a hack.
            if obj.GetName().startswith('inp_') or obj.GetName().startswith('btn_') or obj.GetName().startswith('pnl_') or obj.GetName().startswith('cho_'):
                setattr(self,obj.GetName(),obj)
        if hasattr(self,'set_aliases'):
            self.set_aliases()
        self.config2inputs()
        
    def OnOk(self,event):
        self.inputs2config()
        self.close()

    def close(self,):
        self.Destroy()
    
    def OnCloseWindow(self, event):
        self.close()

    def refresh(self,event):
        """
        Refresh the drawing.
        """
        if hasattr(self,'fig'):
            self.fig.draw(self)

class ConfigSettings(ConfigFrame):
    
    save_vars={
        'inp_randseed':'RandSeed',
        'inp_wrbhhtp':'WrBHHTP',
        'inp_wrfhhtp':'WrFHHTP',
        'inp_wradhh':'WrADHH',
        'inp_wradff':'WrADFF',
        'inp_wrblff':'WrBLFF',
        'inp_wradtwr':'WrADTWR',
        'inp_wrfmtff':'WrFMTFF',
        'inp_clockwise':'Clockwise',
        'cho_scaleiec':'ScaleIEC',
        'inp_turbsim_exec':'TurbSim_exec',
        }
    
    def init_layout(self,):
        self.panel=wx.Panel(self)#,-1,style=wx.NO_BORDER)
        gts_wdr.dlg_settings(self.panel)

    def set_aliases(self,):
        self.cho_scaleiec.aliases=[0,1,2]
        self.inp_turbsim_exec.default_value='Not found.'

    def init_bindings(self,):
        wx.EVT_CLOSE(self, self.OnCloseWindow)
        self.btn_cancel.Bind(wx.EVT_BUTTON,self.OnCloseWindow)
        self.btn_ok.Bind(wx.EVT_BUTTON,self.OnOk)

    def close(self,):
        self.Destroy()
        self.parent.set_turbsim_exec(self.config['TurbSim_exec'])

