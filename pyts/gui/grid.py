from base import *

n_grid_max=10000 # Maximum number of grid points (ny*nz).

class deltaTextCtrl(object):
    @property
    def x(self,):
        return float(self.xCtrl.GetValue())
    @x.setter
    def x(self,val):
        if val is None:
            self.xCtrl.ChangeValue(str(self.dx*(self.n-self.one)))
        else:            
            self.xCtrl.SetValue(str(val))

    @property
    def dx(self,):
        return float(self.dxCtrl.GetValue())
    @dx.setter
    def dx(self,val):
        if val is None:
            self.dxCtrl.ChangeValue('%0.3f' % (self.x/(self.n-self.one)))
        else:
            self.dxCtrl.SetValue(str(val))
            
    @property
    def n(self,):
        return int(self.nCtrl.GetValue())
    @n.setter
    def n(self,val):
        if val is None:
            self.nCtrl.ChangeValue(str(int(self.x/self.dx)+self.one))
            self.x=None
        else:
            self.nCtrl.SetValue(str(int(val)))

    def on_x(self,event):
        try:
            if self.x<0:
                return
            self.dx=None
            self.parent.refresh(None)
        except:
            pass
    def on_n(self,event):
        try:
            if self.n<1:
                return
            self.dx=None
            self.parent.refresh(None)
        except:
            pass
    def on_dx(self,event):
        try:
            if bool(self.mode):
                self.x=None
                self.parent.refresh(None)
            else:
                self.n=None
        except:
            pass

    def __init__(self,parent,xCtrl,dxCtrl,nCtrl,x_dflt=1.0,dx_dflt=None,n_dflt=None,x_depends_on_dx=True,plus_one=True):
        """

        """
        self.xCtrl=xCtrl
        self.dxCtrl=dxCtrl
        self.nCtrl=nCtrl
        self.mode=x_depends_on_dx
        self.one=plus_one
        self.parent=parent
        
        self.xCtrl.ChangeValue(str(x_dflt))
        
        self.xCtrl.Bind(wx.EVT_TEXT,self.on_x)
        self.dxCtrl.Bind(wx.EVT_TEXT,self.on_dx)
        self.nCtrl.Bind(wx.EVT_TEXT,self.on_n)

        if dx_dflt is not None:
            self.dx=dx_dflt
        elif n_dflt is not None:
            self.n=n_dflt


class gridFigure(object):

    def __init__(self,panel,dpi):
        self.dpi=dpi
        self.fig=Figure((1,2),dpi=self.dpi)
        self.canvas=FigCanvas(panel,-1,self.fig)
        self.fig.set_facecolor([0.8,0.8,1])
        self.axes=self.fig.add_axes([0.0,0.1,1.0,0.9])
        self.axbot=self.fig.add_axes([0.0,0.0,1.1,0.1])
        self.axbot.fill([0,1,1,0],[0,0,1,1],facecolor=[.58,.29,0],edgecolor='none',transform=self.axbot.transAxes)
        self.axbot.set_axis_off()
        self.axes.set_aspect('equal')
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas,0,wx.EXPAND | wx.ALL)
        panel.SetSizer(self.sizer)
        panel.Fit()
        
    def draw(self,parent):
        p=parent
        try:
            zhub=float(p.inp_hubheight.GetValue())
        except:
            # Don't do anything if we can't interpret the hubht box.
            return
        h=p.zCtrl.x;w=p.yCtrl.x;ny=p.yCtrl.n;nz=p.zCtrl.n;
        ax=self.axes
        ax.cla()
        self.axes.set_axis_off()
        y=np.arange(ny)*w/(ny-1)-w/2
        z=np.arange(nz)*h/(nz-1)-h/2+zhub
        y,z=np.meshgrid(y,z)
        ax.plot(0,zhub,'ro',ms=7,mec='none')
        ax.plot(y.flatten(),z.flatten(),'kx')
        ylm=[0,(zhub+h/2)*1.1]
        ax.set_ylim(ylm)
        xlm=[-1.05*w/2,w/2*1.05]
        ax.set_xlim(xlm)
        self.canvas.draw()
        
class gridConfigFrame(ConfigFrame):

    save_vars={
        'inp_ny':'NumGrid_Y',
        'inp_nz':'NumGrid_Z',
        'inp_height':'GridHeight',
        'inp_width':'GridWidth',
        'inp_dt':'TimeStep',
        'inp_time':'UsableTime',
        'inp_hubheight':'HubHt',
        }

    def __init__(self, parent, id, title,
        pos = wx.DefaultPosition, size = wx.DefaultSize,
        style = wx.CLOSE_BOX | wx.CAPTION ):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.config=parent.config
        #szr=wx.BoxSizer(wx.VERTICAL | wx.NO_BORDER)
        self.panel=wx.Panel(self)#,-1,style=wx.NO_BORDER)
        gts_wdr.GridSetup(self.panel) # This function was created using wxDesigner.
        for obj in self.panel.Children: #wxDesigner does not allow defining variables, but it does allow names, so we use this as a hack.
            if obj.GetName().startswith('inp_') or obj.GetName().startswith('btn_') or obj.GetName().startswith('pnl_'):
                setattr(self,obj.GetName(),obj)
                
        dpi=wx.ScreenDC().GetPPI()
        self.fig=gridFigure(self.pnl_grid,dpi[0])
        self.fig.draw(self)

        # Set bindings:
        wx.EVT_CLOSE(self, self.OnCloseWindow)
        self.btn_cancel.Bind(wx.EVT_BUTTON,self.OnCloseWindow)
        self.btn_ok.Bind(wx.EVT_BUTTON,self.OnOk)
        self.inp_hubheight.Bind(wx.EVT_TEXT,self.refresh)

        # Initialize the field values and set bindings:
        self.zCtrl=deltaTextCtrl(self,self.inp_height,self.inp_dz,self.inp_nz,x_dflt=self.config['GridHeight'],n_dflt=self.config['NumGrid_Z'])
        self.yCtrl=deltaTextCtrl(self,self.inp_width,self.inp_dy,self.inp_ny,x_dflt=self.config['GridWidth'],n_dflt=self.config['NumGrid_Y'])
        self.tCtrl=deltaTextCtrl(self,self.inp_time,self.inp_dt,self.inp_nt,x_dflt=self.config['UsableTime'],dx_dflt=self.config['TimeStep'],x_depends_on_dx=False,plus_one=0)
        self.inp_hubheight.SetValue('%0.2g' % (self.config['HubHt'],))
        
        self.Fit()
