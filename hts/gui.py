#!/usr/bin/python

# gTurbSim

import wx

class specPanel(wx.Panel):

    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent,id=wx.ID_ANY)
        sizer=wx.BoxSizer(wx.VERTICAL)
        txtOne=wx.TextCtrl(self,wx.ID_ANY,"Test")
        txtTwo=wx.TextCtrl(self,wx.ID_ANY,"Test1")
        
        sizer.Add(txtOne, 0, wx.ALL, 5)
        sizer.Add(txtTwo, 0, wx.ALL, 5)
        
        self.SetSizer(sizer)

class tsTabs(wx.Notebook):

    def __init__(self,parent):
        wx.Notebook.__init__(self,parent,id=wx.ID_ANY,style=wx.BK_DEFAULT)
        self.AddPage(specPanel(self),'Smooth')
        self.AddPage(specPanel(self),'IECKAI')
        self.AddPage(specPanel(self),'IECVKM')

        
class tsgui(wx.Frame):

    def __init__(self,):
        wx.Frame.__init__(self,None,wx.ID_ANY,'TurbSim',size=(500,400))
        
        pnl=wx.Panel(self)
        nbk=tsTabs(pnl)
        
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tsTabs(pnl), 1, wx.ALL|wx.EXPAND, 5)
        pnl.SetSizer(sizer)
        self.Layout()
        self.Show()
        

if __name__=='__main__':
    app=wx.App()
    f=tsgui()
    app.MainLoop()
