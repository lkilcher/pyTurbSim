from .base import wx, gts_wdr, ConfigSettings
from ..io import input as io
from . import grid, prof, turb
from subprocess import call
import os
import glob
import sys
from ..base import tsroot, userroot

# TODO:
#  - Summarize the configuration on the main window.
#  - Add tooltips
#    .. 'disabled' tooltips
#    .. More documentation than tooltips can provide?
#  - 'Load data' panels
#    .. ADCP
#    .. ADV
#    .. FIT spectrum/profile to data!


class gTurbFrame(wx.Frame):

    _default_files = {'-- Default Wind Config --': 'WIND.inp',
                      '-- Default IEC (Wind) Config --': 'WIND_IEC.inp',
                      '-- Default Tidal (Hydro) Config --': 'TIDAL.inp',
                      '-- Default River (Hydro) Config --': 'RIVER.inp',
                      }

    @property
    def currentfile(self,):
        return self._currentfile

    @currentfile.setter
    def currentfile(self, fl):
        if hasattr(self, 'inp_inputfile'):
            self.inp_inputfile.value = fl
        self._currentfile = fl

    def loadDefault(self, strng):
        self.inp_inputfile.value = strng
        self.config = io.read(tsroot + '/gui/default_inputs/' + self._default_files[strng])

    def __init__(self, parent, id, title,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.currentfile = None

        self.CreateMyMenuBar()

        self.CreateMyToolBar()

        self.CreateStatusBar(1)
        self.SetStatusText("Welcome!")

        # Layout the panel:
        self.panel = wx.Panel(self)
        gts_wdr.main(self.panel)

        # Define the inputs:
        self.init_inputs()

        self.loadDefault('-- Default Wind Config --')

        self.bind_menu()
        self.bind_dialog()

        self.set_turbsim_exec(self.find_turbsim_exec())

        # WDR: handler declarations for gTurbFrame
        self.Fit()

    def find_turbsim_exec(self,):
        if sys.platform.startswith('win'):
            fname = 'TurbSim.exe'
        else:
            fname = 'TurbSim'
        name = os.getcwd() + fname
        if os.path.isfile(name):
            return name
        else:
            return

    def set_turbsim_exec(self, name=None):
        """
        Function to set or find the TurbSim (original) executable.
        """
        if name is None:
            pass
        elif os.path.isfile(name):
            self.config['TurbSim_exec'] = name
        else:
            wrn01 = wx.MessageDialog(
                self, 'TurbSim executable not found. ', 'Warning!', wx.ICON_HAND)
            wrn01.ShowModal()
            self.config['TurbSim_exec'] = None
        self.rdo_turbsim.Enable(not name is None)

    def init_inputs(self,):
        # wxDesigner does not allow defining variables, but it does
        # allow names, so we use this as a hack.
        for obj in self.panel.Children:
            if  (obj.GetName().startswith('inp_')
                 or obj.GetName().startswith('btn_')
                 or obj.GetName().startswith('pnl_')
                 or obj.GetName().startswith('cho_')
                 or obj.GetName().startswith('rdo_')):
                setattr(self, obj.GetName(), obj)

    def bind_dialog(self,):
        self.inp_inputfile.Bind(wx.EVT_TEXT, self.onSetFile)
        self.btn_inputfile.Bind(wx.EVT_BUTTON, self.onLoad)
        self.btn_run.Bind(wx.EVT_BUTTON, self.onRun)

    def bind_menu(self,):
        wx.EVT_MENU(self, wx.ID_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, wx.ID_EXIT, self.OnQuit)
        wx.EVT_MENU(self, 20101, self.onConfigSettings)
        wx.EVT_MENU(self, 20102, self.onConfigGrid)
        wx.EVT_MENU(self, 20103, self.onConfigProf)
        wx.EVT_MENU(self, 20104, self.onConfigTurb)
        wx.EVT_MENU(self, 20003, self.onLoad)
        wx.EVT_MENU(self, 20004, self.onSaveAs)
        wx.EVT_MENU(self, 20005, self.onSave)
        wx.EVT_CLOSE(self, self.OnCloseWindow)

    def readConfig(self,):
        try:
            self.config = io.read(self.currentfile)
        except:
            pass

    def writeConfig(self,):
        io.write(self.currentfile, self.config)

    def onRun(self, event):
        if self.currentfile is None:
            self.onSave(event)
        n_iter = int(self.inp_iterations.GetValue())
        if n_iter > 1 and (self.config['RandSeed'] is not None):
            wrn01 = wx.MessageDialog(
                self, ('Multiple iterations with a fixed Random Seed will '
                       'result in identical results.  Change the "RandSeed" '
                       'variable in the "Settings" dialog to "default" so '
                       'that TurbSim will use different random seeds. For '
                       'now a single iteration will run.'),
                'Warning!', wx.ICON_HAND)
            wrn01.ShowModal()
            n_iter = 1
        nd = len('%d' % n_iter)
        dtxt = '%0' + str(nd) + 'd'
        if self.rdo_pyturbsim.GetValue():
            cmd_list = ["python", "pyTurbSim.py", self.currentfile]
        else:
            cmd_list = [self.config['TurbSim_exec'], self.currentfile]
        for itr in range(n_iter):
            self.SetStatusText(
                ("Running " + dtxt + "/%d...") % (itr + 1, n_iter))
            retcode = call(cmd_list)
            self.movefiles(itr, dtxt,)
        self.SetStatusText("Done.")

    def movefiles(self, itr, dtxt):
        """
        Move the output files to an 'iteration' name.
        """
        for nm in glob.iglob(self.currentfile[:-3] + '*'):
            if nm != self.currentfile:
                base, ext = nm.rsplit('.', 1)
                os.rename(nm, ((base + dtxt + '.' + ext) % (itr + 1)))

    def onSave(self, event):
        if self.currentfile is None:
            self.onSaveAs(event)
        else:
            self.writeConfig()

    def onSaveAs(self, event):
        openFileDialog = wx.FileDialog(
            self,
            'Select TurbSim filename for save...',
            userroot,
            'TurbSim.inp',
            '(*.inp,*.*)|*.inp',
            wx.FD_SAVE)
        openFileDialog.ShowModal()
        self.currentfile = openFileDialog.GetPath()  # If
        openFileDialog.Destroy()
        self.writeConfig()

    def onSetFile(self, event):
        if self.inp_inputfile.value in self._default_files.keys():
            self.loadDefault(self.inp_inputfile.value)
        else:
            self.currentfile = self.inp_inputfile.value
        self.readConfig()

    def onLoad(self, event):
        openFileDialog = wx.FileDialog(
            self, 'Open TurbSim input file', userroot,
            'TurbSim.inp', '(*.inp,*.*)|*.inp', wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        self.currentfile = openFileDialog.GetPath()
        openFileDialog.Destroy()
        self.readConfig()

    # WDR: methods for gTurbFrame

    def onConfigSettings(self, event):
        try:
            self.frm_ConfigSettings.Raise()
        except:
            self.frm_ConfigSettings = ConfigSettings(
                self, wx.ID_ANY, 'General Settings')
            self.frm_ConfigSettings.Show(True)

    def onConfigGrid(self, event):
        try:
            self.frm_ConfigGrid.Raise()
        except:
            self.frm_ConfigGrid = grid.gridConfigFrame(
                self, wx.ID_ANY, 'Grid Configuration')
            self.frm_ConfigGrid.Show(True)

    def onConfigProf(self, event):
        try:
            self.frm_ConfigProf.Raise()
        except:
            self.frm_ConfigProf = prof.profConfigFrame(
                self, wx.ID_ANY, 'Profile Model Configuration')
            self.frm_ConfigProf.Show(True)

    def onConfigTurb(self, event):
        try:
            self.frm_ConfigTurb.Raise()
        except:
            self.frm_ConfigTurb = turb.turbConfigFrame(
                self, wx.ID_ANY, 'Turbulence Model Configuration')
            self.frm_ConfigTurb.Show(True)

    def CreateMyMenuBar(self):
        self.SetMenuBar(gts_wdr.MyMenuBarFunc())

    def CreateMyToolBar(self):
        tb = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER)
        gts_wdr.MyToolBarFunc(tb)

    # WDR: handler implementations for gTurbFrame

    def OnAbout(self, event):
        dialog = wx.MessageDialog(
            self,
            ("Welcome to the TurbSim GUI! Written by L. Kilcher "
             "(National Renewable Energy Laboratory)"),
            "About TurbSim",
            wx.OK | wx.ICON_INFORMATION)
        dialog.CentreOnParent()
        dialog.ShowModal()
        dialog.Destroy()

    def OnQuit(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()


#----------------------------------------------------------------------------

class gTurbApp(wx.App):

    def OnInit(self):
        wx.InitAllImageHandlers()
        self.frm = frame = gTurbFrame(
            None, -1, "gTurbSim", [20, 20], [500, 340])
        frame.Show(True)
        return True

    def setfile(self, fname):
        self.frm.currentfile = fname
        self.frm.readConfig()
