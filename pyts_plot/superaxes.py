import matplotlib as mpl
import numpy as np
import new
from string import lowercase
import matplotlib.pylab as pylab
transforms=mpl.transforms
Axes=mpl.axes.Axes
rcParams=mpl.rcParams
from basefuncs import *
## try:
##     import pyPdf as pdf
## except:
##     pdf=None



def initFig(*args,**kwargs):
    """
    Return a figure, and do some automatic stuff...
    (e.g. clear it, name it, resize it)
    """

    tmpd={}
    if kwargs.has_key('name'):
        tmpd['name']=kwargs.pop('name')
    
    out=pylab.figure(*args,**kwargs)
    out.clf()

    if tmpd.has_key('name'):
        out.canvas.set_window_title(tmpd['name'])

    if kwargs.has_key('figsize'):
        # Apparently the forward=True option is broken except for GTK* and WX* backends.  see:
        # http://matplotlib.sourceforge.net/api/figure_api.html (most of the way down)
        out.set_size_inches(kwargs['figsize'],forward=True)

    return out
        
def drawnow():
    pylab.show()
    pylab.interactive(False)

def get_transform(ax,trans):
    if trans.__class__ is not str:
        return trans
    if hasattr(ax,trans):
        return getattr(ax,trans)
    return getattr(ax,'trans'+trans)

def shadex(ax,x,y=[0,1],transform='DataXAxesY',label='_nolegend_',zorder=-100,color='k',alpha=0.2,edgecolor='none',**kwargs):
    transform=get_transform(ax,transform)
    ax.fill_between(x,y[0],y[1],label=label,transform=transform,zorder=zorder,color=color,alpha=alpha,edgecolor=edgecolor,**kwargs)

def shadey(ax,y,x=[0,1],transform='AxesXDataY',label='_nolegend_',zorder=-100,color='k',alpha=0.2,edgecolor='none',**kwargs):
    transform=get_transform(ax,transform)
    ax.fill_betweenx(y,x[0],x[1],label=label,transform=transform,zorder=zorder,color=color,alpha=alpha,edgecolor=edgecolor,**kwargs)
    
def _vln(ax,x,y=[0,1],transform='DataXAxesY',label='_nolegend_',color='k',linewidth=rcParams['axes.linewidth'],**kwargs):
    if isinstance(x,(int,long,float,complex)):
        x=[x]
    transform=get_transform(ax,transform)
    for xnow in x:
        ax.plot([xnow,xnow],y,transform=transform,label=label,color=color,linewidth=linewidth,**kwargs)

def _hln(ax,y,x=[0,1],transform='AxesXDataY',**kwargs):
    if not kwargs.has_key('label'):
        kwargs['label']='_nolegend_'
    if not kwargs.has_key('color'):
        kwargs['color']='k'
    if not kwargs.has_key('linewidth') and not kwargs.has_key('lw'):
        kwargs['lw']=rcParams['axes.linewidth']
    if isinstance(y,(int,long,float,complex)):
        y=[y]
    transform=get_transform(ax,transform)
    for ynow in y:
        ax.plot(x,[ynow,ynow],transform=transform,**kwargs)

def _setaxesframe(ax,str):
    str=np.array(list(str))
    if any(str=='t') and any(str=='b'):
        ax.xaxis.set_ticks_position('both')
        ax.spines['top'].set_visible(True)
        ax.spines['bottom'].set_visible(True)
    elif any(str=='t'):
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')
        ax.spines['top'].set_visible(True)
        ax.spines['bottom'].set_visible(False)
    elif any(str=='b'):
        ax.xaxis.set_ticks_position('bottom')
        ax.xaxis.set_label_position('bottom')
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
    else:
        ax.xaxis.set_ticks_position('none')
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.xaxis.set_ticklabels('')

    if any(str=='l') and any(str=='r'):
        ax.yaxis.set_ticks_position('both')
        ax.spines['left'].set_visible(True)
        ax.spines['right'].set_visible(True)
    elif any(str=='l'):
        ax.yaxis.set_ticks_position('left')
        ax.yaxis.set_label_position('left')
        ax.spines['left'].set_visible(True)
        ax.spines['right'].set_visible(False)
    elif any(str=='r'):
        ax.yaxis.set_ticks_position('right')
        ax.yaxis.set_label_position('right')
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(True)
    else:
        ax.yaxis.set_ticks_position('none')
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.set_ticklabels('')
        #for tk in ax.yaxis.get_ticklabels

def offset_text(ax,x,y,s,offset=(0,0),transform=None,**kwargs):
    """
    Add text to an axes offset from a location.
    
    *offset* specifies the offset (in points) from the selected *pos*.
    If *offset* is a two element list or tuple, it specifies a
    different offset in the x and y directions.

    Returns the text object.

    By default the *x*,*y* positions are in data coordinates.  Specify
    a different 'transform' to change this.

    """
    if transform is None:
        transform=ax.transData
    else:
        transform=get_transform(ax,transform)
    if (offset.__class__ is list) or (offset.__class__ is tuple):
        osx=offset[0]/72.
        osy=offset[1]/72.
    else:
        osx=offset/72.
        osy=offset/72.
    trfrm=transform+transforms.ScaledTranslation(osx,osy,ax.figure.dpi_scale_trans)
    return ax.text(x,y,s,transform=trfrm,**kwargs)

def annoteCorner(ax,s,pos='ll',offset=10,**kwargs):
    """
    annotate a corner of an axes with a string.

    Parameters
    ----------
    *ax* : axes
           is the axes into which to place the annotation.
    *s* : str
          is the text to place in the corner.
    *pos* : str {'ll','ul','lr','ur'}, tuple(2)
            The tuple form specifies the text locaiton in axes coordinates.
    
    *offset* : tuple(1 or 2)
               Specifies the offset from the selected *pos* (in points).

    Returns
    -------
    t : text artist.
        Also, it creates a 'corner_label' attribute in the axes, with this text artist.

    Notes
    -----
    If the string form of *pos* is used then the sign of *offset* is
    always such that it shifts the string toward the center.If it is a
    two element tuple or string, it specifies a different offset in
    the x and y directions.
    
    """
    prm={}
    yp=0.0
    xp=0.0
    prm['va']='baseline'
    prm['ha']='left'
    #prm['fontsize']='medium'
    if (offset.__class__ is list) or (offset.__class__ is tuple):
        osx=offset[0]
        osy=offset[1]
    else:
        osx=offset
        osy=offset
    if pos.__class__ is str:
        if pos[0]=='u':
            osy=-osy
            yp=1.
            prm['va']='top'
        if pos[1]=='r':
            osx=-osx
            xp=1.
            prm['ha']='right'
    else:
        xp=pos[0]
        yp=pos[1]
    prm['offset']=(osx,osy)
    prm['transform']=ax.transAxes
    
    for key in prm:
        if not kwargs.has_key(key):
            kwargs[key]=prm[key]
    ax.corner_label=offset_text(ax,xp,yp,s,**kwargs)
    return ax.corner_label

def skip_ticklabels(ax,rep=2,offset=0,axis='x',force=True):
    """
    hide the ticklabels on ticks except for every *rep*'th tick.
    *offset* specifies an offset, of tick to start on.
    *axis* specifies the x (default) or y axis.
    when *force* is True (default) this function turns on every *rep*'th tick.
    """
    if axis=='x':
        tks=ax.get_xticklabels()
    else:
        tks=ax.get_yticklabels()
    for idx,tk in enumerate(tks):
        if np.mod(idx+offset,rep):
            tk.set_visible(False)
        elif force:
            tk.set_visible(True)

#class myAxes(matplotlib.axes.Axes):
class myaxes(mpl.axes.Axes):
    """
    My own axes class.
    """
    cpcolor=cpcolor
    hln=_hln
    vln=_vln
    @property
    def transAxesXDataY(self,):
        return transforms.blended_transform_factory(self.transAxes,self.transData)
    @property
    def transDataXAxesY(self,):
        return transforms.blended_transform_factory(self.transData,self.transAxes)

    def plot(self,*args,**kwargs):
        # This just makes sure that my lines get drawn,
        # otherwise it just calls the axes' plot instance.
        super(myaxes,self).plot(*args,**kwargs)
        pylab.draw_if_interactive()

    skip_ticklabels=skip_ticklabels
    labelax=labelax
    cbar=cbar
    offset_text=offset_text
    annoteCorner=annoteCorner
    setaxesframe=_setaxesframe
    errorshadex=errorshadex

    def __init__(self,fig=None,rect=None,**kwargs):
        if fig is None:
            fig=pylab.gcf()
        if rect is None:
            rect=[.15,.15,.75,.75]
        super(myaxes,self).__init__(fig,rect,**kwargs)
        fig.add_axes(self)
        pylab.draw_if_interactive()
        
        


def axes(*args, **kwargs):
    """
    Add an axes at position rect specified by:

    - ``axes()`` by itself creates a default full ``subplot(111)`` window axis.

    - ``axes(rect, axisbg='w')`` where *rect* = [left, bottom, width,
      height] in normalized (0, 1) units.  *axisbg* is the background
      color for the axis, default white.

    - ``axes(h)`` where *h* is an axes instance makes *h* the current
      axis.  An :class:`~matplotlib.axes.Axes` instance is returned.

    =======   ============   ================================================
    kwarg     Accepts        Desctiption
    =======   ============   ================================================
    axisbg    color          the axes background color
    frameon   [True|False]   display the frame?
    sharex    otherax        current axes shares xaxis attribute with otherax
    sharey    otherax        current axes shares yaxis attribute with otherax
    polar     [True|False]   use a polar axes?
    =======   ============   ================================================

    Examples:

    * :file:`examples/pylab_examples/axes_demo.py` places custom axes.
    * :file:`examples/pylab_examples/shared_axis_demo.py` uses
      *sharex* and *sharey*.
      
      This was copied from the pyplot axes function

    """

    nargs = len(args)
    if nargs==0:
        args=[[.1,.1,.8,.8]]
    if nargs>1:
        raise TypeError('Only one non keyword arg to axes allowed')
    arg = args[0]

    axd={}
    newd={}
    newd['lw']=rcParams['axes.linewidth']
    if kwargs.has_key('axisbg'):
        axd['axisbg']=kwargs.pop('axisbg')
    if kwargs.has_key('frameon'):
        axd['frameon']=kwargs.pop('frameon')
    if kwargs.has_key('sharex'):
        axd['sharex']=kwargs.pop('sharex')
    if kwargs.has_key('sharey'):
        axd['sharey']=kwargs.pop('sharey')
    if kwargs.has_key('polar'):
        axd['polar']=kwargs.pop('polar')
    if kwargs.has_key('linewidth'):
        newd['lw']=kwargs.pop('linewidth')
    if kwargs.has_key('lw'):
        newd['lw']=kwargs.pop('lw')
    if kwargs.has_key('ticksize'):
        newd['xticksize']=kwargs.get('ticksize')
        newd['yticksize']=kwargs.pop('ticksize')
    if kwargs.has_key('xticksize'):
        newd['xticksize']=kwargs.pop('xticksize')
    if kwargs.has_key('yticksize'):
        newd['yticksize']=kwargs.pop('yticksize')
    if kwargs.has_key('fs'):
        newd['fontsize']=kwargs.pop('fs')
    if kwargs.has_key('fontsize'):
        newd['fontsize']=kwargs.pop('fontsize')
    if kwargs.has_key('xlocation'):
        newd['xlocation']=kwargs.pop('xlocation')
    if kwargs.has_key('ylocation'):
        newd['ylocation']=kwargs.pop('ylocation')
    if (not kwargs.has_key('fig')) and (not kwargs.has_key('figure')):
        fig=pylab.gcf()
    elif kwargs.has_key('figure'):
        fig=kwargs.pop('figure')
    else:
        fig=kwargs.pop('fig')

    if isinstance(arg, mpl.axes.Axes):
        a = fig.sca(arg)
    else:
        rect = arg
        a = fig.add_axes(rect, **axd)
        a.set(**kwargs)
        
        if newd.has_key('xlocation'):
            a.xaxis.set_ticks_position(newd['xlocation'])
            if newd['xlocation']=='top':
                a.spines['bottom'].set_visible(False)
            elif newd['xlocation']=='bottom':
                a.spines['top'].set_visible(False)
        if newd.has_key('ylocation'):
            a.yaxis.set_ticks_position(newd['ylocation'])
            if newd['ylocation']=='right':
                a.spines['left'].set_visible(False)
            elif newd['ylocation']=='left':
                a.spines['right'].set_visible(False)
        if newd.has_key('lw'):
            for sp in a.spines:
                a.spines[sp].set_linewidth(newd['lw'])
            for tck in a.xaxis.get_ticklines():
                tck.set_mew(newd['lw'])
            for tck in a.yaxis.get_ticklines():
                tck.set_mew(newd['lw'])
        if newd.has_key('xticksize'):
            for tck in a.xaxis.get_ticklines():
                tck.set_ms(newd['xticksize'])
        if newd.has_key('yticksize'):
            for tck in a.yaxis.get_ticklines():
                tck.set_ms(newd['yticksize'])
        if newd.has_key('fontsize'):
            for tklbl in a.xaxis.get_ticklabels():
                tklbl.set_fontsize(newd['fontsize'])
            for tklbl in a.yaxis.get_ticklabels():
                tklbl.set_fontsize(newd['fontsize'])

    a.transAxesXDataY=transforms.blended_transform_factory(a.transAxes,a.transData)
    a.transDataXAxesY=transforms.blended_transform_factory(a.transData,a.transAxes)

    a.hln=new.instancemethod(_hln,a,Axes)
    a.vln=new.instancemethod(_vln,a,Axes)
    a.shadex=new.instancemethod(shadex,a,Axes)
    a.shadey=new.instancemethod(shadey,a,Axes)
    a.setaxesframe=new.instancemethod(_setaxesframe,a,Axes)
    a.annoteCorner=new.instancemethod(annoteCorner,a,Axes)
    a.offset_text=new.instancemethod(offset_text,a,Axes)
    a.cpcolor=new.instancemethod(cpcolor,a,Axes)
    a.cbar=new.instancemethod(cbar,a,Axes)
    a.labelax=new.instancemethod(labelax,a,Axes)
    a.skip_ticklabels=new.instancemethod(skip_ticklabels,a,Axes)
    a.errorshadex=new.instancemethod(errorshadex,a,Axes)
    #a.plot_specobj=new.instancemethod(plot_specobj,a,Axes)
    
    pylab.draw_if_interactive()
    return a


    
def alphNumAxes(self,vals=lowercase,prefix=None,suffix=None,**kwargs):
    """
    Label the axes with alphanumeric characters.

    *axs* are the axes over which to add labels to.
    *vals* should be a string or list of strings to annotate
    the axes with.  It defaults to string.lowercase
    *prefix* and *suffix* are strings that can be placed before
    and after each val. e.g.: prefix='(' and suffix=')' will wrap
    the annotations in parenthesis.

    By default, this function calls annoteCorner on
    itss axes.ax.flatten(), and uses 

    See also: annoteCorner, string
    """
    if suffix is None:
        suffix=plot_number_suffix
    if prefix is None:
        prefix=plot_number_prefix
    corner_labels=np.empty(self.size,'O')
    for idx,ax in enumerate(self):
        corner_labels[idx]=ax.annoteCorner(prefix+vals[idx]+suffix,**kwargs)

class axgroup(object):
    alphNumAxes=alphNumAxes
    @property
    def size(self,):
        return self.axes.size

    @property
    def ax(self,):
        """
        A shortcut to 'self.axes'
        """
        return self.axes
    
    def __len__(self,):
        return len(self.axes)

    def __iter__(self,):
        for ax in self.axes.flatten():
            yield ax

    def annotate(self,*args,**kwargs):
        for ax in self:
            ax.annotate(*args,**kwargs)

    def __getitem__(self,val):
        if hasattr(val,'__len__'):
            for v in val:
                if v.__class__ is slice:
                    return axgroup(self.axes[val])
        elif val.__class__ is slice:
            return axgroup(self.axes[val])
        return self.axes[val]

    def xgrid(self,b=None,**kwargs):
        for ax in self:
            ax.xaxis.grid(b,**kwargs)
    def ygrid(self,b=None,**kwargs):
        for ax in self:
            ax.yaxis.grid(b,**kwargs)

    def shadex(self,*args,**kwargs):
        for ax in self:
            ax.shadex(*args,**kwargs)
    def shadey(self,*args,**kwargs):
        for ax in self:
            ax.shadey(*args,**kwargs)

    def hln(self,y=0,*args,**kwargs):
        for ax in self:
            ax.hln(y,*args,**kwargs)
    def vln(self,x=0,*args,**kwargs):
        for ax in self:
            ax.vln(x,*args,**kwargs)

    def fill_between(self,*args,**kwargs):
        """
        Iterates a fill_between call over all axes in the group.
        See fill_between
        """
        for ax in self:
            ax.fill_between(*args,**kwargs)
    
    def fill_betweenx(self,*args,**kwargs):
        """
        Iterates a fill_betweenx call over all axes in the group.
        See fill_betweenx
        """
        for ax in self:
            ax.fill_betweenx(*args,**kwargs)

    def set_xscale(self,val):
        for ax in self:
            ax.set_xscale(val)
    def set_yscale(self,val):
        for ax in self:
            ax.set_yscale(val)
    
    def set_xlim(self,*args,**kwargs):
        for ax in self:
            ax.set_xlim(*args,**kwargs)
    def set_ylim(self,*args,**kwargs):
        for ax in self:
            ax.set_ylim(*args,**kwargs)

    def set_xticks(self,*args,**kwargs):
        for ax in self:
            ax.set_xticks(*args,**kwargs)
    def set_yticks(self,*args,**kwargs):
        for ax in self:
            ax.set_yticks(*args,**kwargs)

    def set_ylabel(self,lbls,*args,**kwargs):
        if lbls.__class__ is not list:
            lbls=list(lbls)
        if len(lbls)==1:
            lbls=lbls*len(self)
        for ax,lbl in zip(self,lbls):
            ax.set_ylabel(lbl,*args,**kwargs)
    def set_xlabel(self,lbls,*args,**kwargs):
        if lbls.__class__ is not list:
            lbls=list(lbls)
        if len(lbls)==1:
            lbls=lbls*len(self)
        for ax,lbl in zip(self,lbls):
            ax.set_xlabel(lbl,*args,**kwargs)

    def __init__(self,axes):
        self.axes=axes

    def iterplot(self,iter,*args,**kwargs):
        for ax,(dat) in zip(self,iter):
            tmp=list(dat)+list(args)
            ax.plot(*tmp,**kwargs)

    def plot(self,*args,**kwargs):
        for ax in self:
            ax.plot(*args,**kwargs)

    def offset_text(self,x,y,s,offset=(0,0),*args,**kwargs):
        for ax in self:
            ax.offset_text(x,y,s,offset=offset,*args,**kwargs)

    def hide(self,objs='xticklabels',ax=None):
        """
        Hide `objs` on all axes of this group *except* for those specified in `ax`.

        Parameters
        ----------
        objs : str {'xticklabels', 'yticklabels', 'minorxticks', 'minoryticks'}, or list of.
        ax   : axes, optional (default: hide all)
               The axes (or list of axes) on which these items should **not** be hidden.

        Examples
        --------
        Hide the xticklabels on all axes except ax0::
            hide('xticklabels',self.ax0)
            
        To hide all xticklabels, simply do:
           hide('xticklabels')
        
        See also
        --------
        antiset

        """
        if objs.__class__ is str:
            objs=[objs]
        types={'x':['xticklabels','minorxticks'],'y':['yticklabels','minoryticks']}
        for obj in objs:
            if ax.__class__ is str and ax=='all':
                axs=self.ax.flatten()
            else:
                if ax is None:
                    if obj in types['x'] and hasattr(self,'_xlabel_ax'):
                        ax=self._xlabel_ax
                    elif obj in types['y'] and hasattr(self,'_ylabel_ax'):
                        ax=self._ylabel_ax
                    else: # This gives default behavior?
                        ax=[]
                if not hasattr(ax,'__len__'):
                    ax=[ax]
                axs=list(set(self.ax.flatten())-set(ax))
            for axn in axs:
                if obj=='xticklabels':
                    pylab.setp(axn.get_xticklabels(),visible=False)
                elif obj=='yticklabels':
                    pylab.setp(axn.get_yticklabels(),visible=False)
                elif obj=='minorxticks':
                    pylab.setp(axn.xaxis.get_minorticklines(),visible=False)
                elif obj=='minoryticks':
                    pylab.setp(axn.yaxis.get_minorticklines(),visible=False)
                else:
                    error

    def set(self,**kwargs):
        pylab.setp(self.ax.flatten(),**kwargs)

    def antiset(self,ax,**kwargs):
        # Some backwards compatability stuff:
        if kwargs.has_key('xticklabels') and kwargs['xticklabels']=='':
            kwargs.pop('xticklabels')
            self.hide('xticklabels',ax)
        if kwargs.has_key('yticklabels') and kwargs['yticklabels']=='':
            kwargs.pop('yticklabels')
            self.hide('yticklabels',ax)
        if kwargs.has_key('minorxticks') and not kwargs['minorxticks']:
            kwargs.pop('minorxticks')
            self.hide('minorxticks',ax)
        if kwargs.has_key('minoryticks') and not kwargs['minoryticks']:
            kwargs.pop('minoryticks',ax)
            self.hide('minoryticks',ax)
            
        if len(kwargs)==0:
            return
        # The meat:
        if not hasattr(ax,'__len__'):
            ax=[ax]
        pylab.setp(list(set(self.ax.flatten())-set(ax)),**kwargs)

class saxes(axgroup):
    """
    Create an axes object using S(uper)AXES.

    Use keyword argument fig=<figure object> to specify the figure in
    which to create the axes.

    Notes
    -----
    n=(3,4) to set up a 3x4 array of axes.
    
    n=(3,[1,1,1,.5]) to set up a 3x4 array of axes with the last column half the width of the others.
    
    n=([1,1,1.5],[1,1,1,.5]) to set up a 3x4 array of axes with the last row 1.5 times as large and the last column half as wide.

    h=(.1,.9,.05) to create the horizontal frame box at .1 and .9, with
    gaps of .05 between each axes.
    
    v=(.1,.9,.05) similarly for the vertical frame/gap.

    drawax=L, where L is a logical array of the axes you actually want to
    draw (default is all of them).
    
    sharex=True, chooses whether the axes share an xaxis.
    sharey=True, chooses whether the axes share a yaxis.
    
    """
    def __init__(self,n=(1,1),h=[.1,.9,.05],v=[.1,.9,.05],**kwargs):
        self.linewidth=rcParams['axes.linewidth']
        nax=[1,1]
        if hasattr(n[0],'__iter__'):
            nax[0]=len(n[0])
            self.vrel=np.array(n[0],dtype='float32')
        else:
            nax[0]=n[0]
            self.vrel=np.ones(n[0],dtype='float32')
        if hasattr(n[1],'__iter__'):
            nax[1]=len(n[1])
            self.hrel=np.array(n[1],dtype='float32')
        else:
            nax[1]=n[1]
            self.hrel=np.ones(n[1],dtype='float32')
        self.n=nax
        self.h=h
        self.v=v
        self.sharex=np.ones(nax,dtype='int8')
        self.sharey=np.ones(nax,dtype='int8')
        self._sharex_ax=np.empty(16,dtype='object')
        self._sharey_ax=np.empty(16,dtype='object')
        self.axes=np.empty(self.n,dtype='object')
        for key in kwargs:
            if key=='sharey' and kwargs[key].__class__ is bool:
                self.sharey[:]=kwargs[key]
            elif key=='sharex' and kwargs[key].__class__ is bool:
                self.sharex[:]=kwargs[key]
            else:
                setattr(self,key,kwargs[key])
        self.drawax=np.ones(nax,dtype='bool')

    def set_ylabel_pos(self,pos,axs=None,):
        if axs is None:
            axs=self.ax.flatten()
        for ax in axs:
            ax.yaxis.set_label_coords(pos,0.5)
    
    def xlabel(self,*args,**kwargs):
        """
        This is different than 'set_xlabel' because it sets the xlabel only for the 'self._xlabel_ax'.
        """
        self._xlabel_ax.set_xlabel(*args,**kwargs)

    def ylabel(self,*args,**kwargs):
        """
        This is different than 'set_ylabel' because it sets the ylabel only for the 'self._ylabel_ax'.
        """
        self._ylabel_ax.set_ylabel(*args,**kwargs)

    def axgrid(self):
        axg=np.ones((self.n[0],self.n[1],4))
        axg[:,:,0],axg[:,:,2]=axvec2axpos(self.n[1],self.h,rel=self.hrel)
        axg[:,:,1],axg[:,:,3]=axvec2axpos(self.n[0],self.v,True,rel=self.vrel)
        return axg

    def drawall(self,**kwargs):
        if not self.n==self.drawax.shape:
            self.drawax=np.ones(self.n,dtype='bool')
        if not self.n[1]==self.hrel.shape[0]:
            self.hrel=np.ones(self.n[1],dtype='float32')
        if not self.n[0]==self.vrel.shape[0]:
            self.vrel=np.ones(self.n[0],dtype='float32')
        if kwargs.has_key('lw'):
            kwargs['linewidth']=kwargs.pop('lw')
        if not kwargs.has_key('linewidth'):
            kwargs['linewidth']=self.linewidth
        else:
            self.linewidth=kwargs['linewidth']

        forcesharex=False
        forcesharey=False
        if kwargs.has_key('sharex'):
            forcesharex=True
        if kwargs.has_key('sharey'):
            forcesharey=True
        inter=pylab.isinteractive()
        pylab.interactive(False)# wait to draw the axes, until they've all been created.
        axg=self.axgrid()
        for iv in range(self.n[0]):
            for ih in range(self.n[1]):
                if forcesharex: # I should put this functionality into a func.
                    pass
                elif self.sharex[iv,ih] and self._sharex_ax[self.sharex[iv,ih]]:
                    kwargs['sharex']=self._sharex_ax[self.sharex[iv,ih]]
                elif kwargs.has_key('sharex'):
                    kwargs.pop('sharex')
                if forcesharey:
                    pass
                elif self.sharey[iv,ih] and self._sharey_ax[self.sharey[iv,ih]]:
                    kwargs['sharey']=self._sharey_ax[self.sharey[iv,ih]]
                elif kwargs.has_key('sharey'):
                    kwargs.pop('sharey')
                if self.drawax[iv,ih]:
                    #self.ax[iv,ih]=myaxes(axg[iv,ih,:],**kwargs)
                    self.ax[iv,ih]=axes(axg[iv,ih,:],**kwargs)
                    self.ax[iv,ih].hold(True)
                    if self.sharex[iv,ih] and not self._sharex_ax[self.sharex[iv,ih]]:
                        self._sharex_ax[self.sharex[iv,ih]]=self.ax[iv,ih]
                    if self.sharey[iv,ih] and not self._sharey_ax[self.sharey[iv,ih]]:
                        self._sharey_ax[self.sharey[iv,ih]]=self.ax[iv,ih]
                    
                flag=True
        
        self._xlabel_ax=self.ax[-1,0]
        self._ylabel_ax=self._xlabel_ax
        pylab.interactive(inter)
        pylab.draw_if_interactive()
        return self.ax


class fig_meta(object):
    title=None
    author=u'Levi Kilcher'
    script=None
    producer=u'matplotlib '+mpl.__version__+', http://matplotlib.sf.net'
    description=None
    keywords=None
    _fields=['title','author','script','producer','description','keywords']
             
    def __repr__(self,):
        ostring='<ptools.fig_meta object>\n'
        for fld in self._fields:
            ostring+='%16s' % (fld)+' : '+str(getattr(self,fld))+'\n'
        return ostring

    def write_pdf(self,fname):
        pass
    
    ## def write_pdf(self,fname):
    ##     pdf_map=[('title','/Title'),('author','/Author'),('description','/Subject'),('keywords','/Keywords'),('producer','/Producer')]
    ##     ostrm=pdf.PdfFileWriter()
    ##     infoDict = ostrm._info.getObject()
    ##     for nm,pnm in pdf_map:
    ##         val=getattr(self,nm)
    ##         if val is not None:
    ##             if nm == 'author' and self.script is not None:
    ##                 infoDict[pdf.generic.NameObject(pnm)]=pdf.generic.createStringObject(val+' ('+self.script+')')
    ##             else:
    ##                 infoDict[pdf.generic.NameObject(pnm)]=pdf.generic.createStringObject(val)
    ##     with file(fname,'rb') as ifile:
    ##         istrm=pdf.PdfFileReader(ifile)
    ##         for page in range(istrm.getNumPages()):
    ##             ostrm.addPage(istrm.getPage(page))
    ##         with tempfile.NamedTemporaryFile(delete=False) as ofile:
    ##             ostrm.write(ofile)
    ##     shutil.copyfile(ofile.name,fname)
    ##     os.remove(ofile.name)
    ##     #os.rename(ofile.name,fname)

    def write(self,fname):
        if fname.endswith('.pdf'):
            self.write_pdf(fname)
        elif fname.endswith('.svg'):
            pass
            #self.write_svg(fname)
        else:
            pass

class figobj(axgroup):
    """
    A base class for my figure objects.
    """
    nax=(1,1)

    def savefig(self,*args,**kwargs):
        self.fig.savefig(*args,**kwargs)
        self.meta.write(args[0])

    def sax_params(self,**kwargs):
        return kwargs
    
    def saxes(self,nax=None,**kwargs):
        if nax is None:
            nax=self.nax
        self.sax=saxes(nax,**self.sax_params(**kwargs))
        self.sax.drawall()
        self.axes=self.sax.ax.flatten()
        
    def initFig(self,fignum,nax=None,**kwargs):
        figkws={}
        figkws['figsize']=kwargs.pop('figsize',None)
        self.fig=pylab.figure(fignum,**figkws)
        self.clf=self.fig.clf
        self.clf()
        if kwargs.has_key('title'):
            self.fig.canvas.set_window_title('Fg%d: ' % (self.fig.number) + kwargs['title'])

    def __init__(self,fignum,nax=None,axsize=None,frame=[.6,.3,1,.3],gap=.4,**kwargs):
        """
        *fignum*   : Figure number
        *nax*      : Shape of axes.

        Other keyword arguments:
        *saxparams*  : input arguments to saxes.
        
        *axsize*     : specifies the size of the axes [vertical,horizontal] in inches.
        
        When *axsize* is not None (default):
        *frame*      : specifies the frame around the axes [bottom,top,left,right], 
                       in inches (default: [.6,.3,1,.3]).
        *gap*        : specifies the gap between axes [vertical,horizontal], 
                       in inches (default: [.2,.2]).
        *hrel*       : specifies the relative horizontal size of each axes.
        *vrel*       : specifies the relative vertical size of each axes.
        """
        saxparams={}
        if nax is None:
            nax=[1,1]
        if kwargs.has_key('vrel'):
            nax[0]=saxparams['vrel']=kwargs['vrel']
        self.meta=fig_meta()
        if axsize is not None:
            axsize=pair(axsize)
            gap=pair(gap)
            kwargs['figsize']=np.zeros(2)
            kwargs['figsize'][0],saxparams['h']=calcFigSize(nax[1],ax=[axsize[1],gap[1]],frm=frame[2:])
            kwargs['figsize'][1],saxparams['v']=calcFigSize(nax[0],ax=[axsize[0],gap[0]],frm=frame[:2])
        saxparams['sharex']=kwargs.pop('sharex',True)
        saxparams['sharey']=kwargs.pop('sharey',False)
        if kwargs.has_key('saxparams'):
            saxparams.update(**kwargs.pop('saxparams'))
        self.initFig(fignum,**kwargs)
        self.saxes(nax=nax,**saxparams)
        
    def __enter__(self,):
        return self
    
    def __exit__(self,type,value,trace):
        pass


