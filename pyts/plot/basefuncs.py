import numpy as np
from scipy.stats import nanmean
import matplotlib as mpl


def pair(val):
    """
    Return the input as a list of two values if it is a scalar.
    """
    if np.isscalar(val):
        return [val]*2
    if len(val)==1:
        return [val[0],val[0]]
    return val

def cpcolor(*args,**kwargs):
    """
    cpcolor(x,y,c)

    makes a pseudocolor plot of the data in c

    Optional keyword arguments:
    fixgaps=True
    threshx=inf
    threshy=inf
    
    """
    threshx=np.inf
    threshy=np.inf
    fixgaps=True
    argind=0
    if isinstance(args[0], mpl.axes.Axes):
        argind+=1 # Data is the second (1) element of args... (see below)
        ax = args[0]
    elif kwargs.has_key('ax') or kwargs.has_key('axes') or kwargs.has_key('parent'):
        if kwargs.has_key('parent'):
            ax=kwargs.pop('parent')
        elif kwargs.has_key('ax'):
            ax=kwargs.pop('ax')
        else:
            ax=kwargs.pop('axes')
    else:
        ax=mpl.pylab.gca()

    if kwargs.has_key('fixgaps'):
        fixgaps=kwargs.pop('fixgaps')
    if kwargs.has_key('threshx'):
        threshx=kwargs.pop('threshx')
    if kwargs.has_key('threshy'):
        threshy=kwargs.pop('threshy')
    if kwargs.has_key('clim'):
        clm=kwargs.pop('clim')
        kwargs['vmin']=clm[0]
        kwargs['vmax']=clm[1]
    

    if len(args)-argind==1:
        dat=args[0+argind]
        x=np.arange(dat.shape[1])
        y=np.arange(dat.shape[0])
    else:
        x=args[0+argind]
        y=args[1+argind]
        dat=args[2+argind]
    
    dfx=np.diff(x,1,0).astype('double')
    dx=dfx
    gd=abs(dx)<=3*nanmean(abs(dx))
    while not gd.all():
        dx=dx[gd]
        gd=abs(dx)<=3*nanmean(abs(dx))
        
    dx=nanmean(dx).astype('double')


    dfy=np.diff(y,1,0).astype('double')
    dy=dfy
    gd=abs(dy)<=3*nanmean(abs(dy))
    while not gd.all():
        dy=dy[gd]
        gd=abs(dy)<=3*nanmean(abs(dy))

    dy=nanmean(dy).astype('double')

    N=dat.shape[1]+sum(abs(dfx)>3*abs(dx))*fixgaps
    datn=np.NaN*np.ones([dat.shape[0],N+1])
    xn=np.NaN*np.ones([N+1,1])
    if fixgaps:
        if abs(dfx[0])<3*abs(dx) or abs(dfx[0])<=threshx:
            xn[0]=x[0]-dfx[0]/2
        else:
            xn[0]=x[0]-dx
        datn[:,0]=dat[:,0]
        c=0
        for i0 in range(0,len(dfx)):
            c=c+1
            if abs(dfx[i0])<=(3*abs(dx)) or np.isnan(dfx[i0]) or abs(dfx[i0])<=threshx:
                xn[c]=x[i0]+dfx[i0]/2
                datn[:,c]=dat[:,i0+1]
            else:
                xn[c]=x[i0]+dx
                datn[:,c]=np.NaN*dat[:,0]
                c=c+1
                xn[c]=x[i0]+dfx[i0]-dx
                datn[:,c]=dat[:,i0]
    else:
        datn[:,1:N]=dat
        xn[2:N]=x[2:N]-dfx/2

    xn[0]=x[0]-dx/2
    xn[-1]=x[-1]+dx/2

    N=datn.shape[0]+sum(abs(dfy)>3*abs(dy))*fixgaps
    datn2=np.NaN*np.ones([N+1,datn.shape[1]])
    yn=np.NaN*np.ones([N+1,1])
    if fixgaps:
        if abs(dfy[0])<3*abs(dy) or abs(dfy[0])<=threshy:
            yn[0]=y[0]-dfy[0]/2
        else:
            yn[0]=y[0]-dy
        datn2[0,:]=datn[0,:]
        c=0
        for i0 in range(0,len(dfy)):
            c=c+1
            if abs(dfy[i0])<=(3*abs(dy)) or np.isnan(dfy[i0]) or abs(dfy[i0])<=threshy:
                yn[c]=y[i0]+dfy[i0]/2
                datn2[c,:]=datn[i0+1,:]
            else:
                yn[c]=y[i0]+dy
                datn2[c,:]=np.NaN*datn[0,:]
                c=c+1
                yn[c]=y[i0]+dfy[i0]-dy
                datn2[c,:]=datn[i0,:]
    else:
        datn2[1:N,:]=datn
        yn[2:N]=y[2:N]-dfy/2

    yn[0]=y[0]-dy/2
    yn[-1]=y[-1]+dy/2

    datm=np.ma.array(datn2,mask = np.isnan(datn2))
        
    [mx,my]=np.meshgrid(xn,yn)

    mx=np.ma.array(mx, mask = np.isnan(mx))
    my=np.ma.array(my, mask = np.isnan(my))

    #mx=xn
    #my=yn
    
    hndl=ax.pcolormesh(mx,my,datm,shading = 'flat',**kwargs)
    hndl.set_rasterized(True)
    mpl.pylab.draw_if_interactive()
    return hndl


def cbar(peer,mappable=None,place='right',axsize=.023,axgap=.02,lims=None,**kwargs):
    xtkdir=mpl.rcParams['xtick.direction']
    mpl.rcParams['xtick.direction']='in'
    ytkdir=mpl.rcParams['ytick.direction']
    mpl.rcParams['ytick.direction']='in'
    bx=mpl.pylab.getp(peer,'position')
    ext=bx.extents
    axp=np.zeros(4)
    orient='vertical'
    if place=='right':
        axp[0]=ext[2]+axgap
        axp[1]=ext[1]
        axp[2]=axsize
        axp[3]=bx.height/2
    elif place=='over':
        axp[0]=ext[0]+bx.width/2
        axp[1]=ext[3]+axgap
        axp[2]=bx.width/2
        axp[3]=axsize
        orient='horizontal'
        lblpos='top'
    elif hasattr(place,'__iter__'):
        axp=place
        if axp[3]<axp[2]:
            orient='horizontal'
    
    if kwargs.has_key('orient'):
        orient=kwargs.pop('orient')
        
    if kwargs.has_key('axdict'):
        axd=kwargs.pop('axdict')
    else:
        axd={}
    ax2={}
    if kwargs.has_key('linewidth'):
        axd['linewidth']=kwargs.pop('linewidth')
    if kwargs.has_key('ticklabels'):
        ax2['yticklabels']=kwargs.pop('ticklabels')

    if kwargs.has_key('fontsize'):
        ax2['fontsize']=kwargs.pop('fontsize')
    
    tmp=axes(axp,**axd)
    if mappable is None:
        hndl=mpl.pylab.colorbar(cax=tmp,orientation=orient,**kwargs)
    else:
        hndl=mpl.pylab.colorbar(mappable,cax=tmp,orientation=orient,**kwargs)

    if ax2.has_key('fontsize'):
        if orient=='vertical':
            mpl.pylab.setp(tmp.get_yticklabels(),fontsize=ax2.pop('fontsize'))
        else:
            mpl.pylab.setp(tmp.get_xticklabels(),fontsize=ax2.pop('fontsize'))
    
    tmp.set(**ax2)
    mpl.rcParams['xtick.direction']=xtkdir
    mpl.rcParams['ytick.direction']=ytkdir


    if place=='right':
        pass
    elif place=='over':
        tmp.xaxis.set_label_position('top')
        tmp.xaxis.set_ticks_position('top')
    return hndl

def labelax(peer,str,place='right',**kwargs):
    if place=='right':
        place=(1.025,.6)
    elif place=='over':
        place=(.48,1.1)
        if not kwargs.has_key('horizontalalignment'):
            kwargs['horizontalalignment']='right'
    
    hndl=peer.text(place[0],place[1],str,transform = peer.transAxes,**kwargs)
        
    return hndl

def errorshadex(peer,x,y,xerr,ecolor=None,ealpha=.5,color='b',zorder=0,**kwargs):
    """
    Plot a line with a shaded region for error.
    """
    if ecolor is None:
        ecolor=color
    peer.plot(x,y,color=color,zorder=zorder,**kwargs)
    peer.fill_betweenx(y,x-xerr,x+xerr,alpha=ealpha,color=ecolor,zorder=zorder-1)


def vecs2fillvec(y1,y2,meanstd=False,x=None,axis=0):
    """
    *y1* and *y2* should be the ranges.
    This function will then flip y2 and tack it onto y1.

    For meanstd=True
    *y1* should be the mean, and *y2* the std.
    This function will add and subtract y2 from y1.
    """

    if meanstd:
        y1,y2=y1+y2,y1-y2

    if x is None:
        return np.concatenate((y1,y2[::-1],y1[[0]]),axis)
    else:
        return (np.concatenate((y1,y2[::-1],y1[[0]]),axis),np.concatenate((x,x[::-1],x[[0]]),axis))
        

def calcFigSize(n,ax=np.array([1,0]),frm=np.array([.5,.5]),norm=False):
    """
    sz,vec = calcFigSize(n,ax,frame) calculates the width (or height) of a figure with
    *n* subplots.  Specify the width (height) of each subplot with *ax[0]*, the space
    between subplots with *ax[1]*, and the left/right (bottom/top) spacing with
    *frame[0]*/*frame[1]*.

    calcFigSize returns *sz*, a scalar, which is the width (or height) the figure should,
    and *vec*, which is the three element vector for input to saxes.

    See also: saxes, axes, calcAxesSize
    """
    if hasattr(n,'__iter__'):
        n=np.sum(n)
    sz=n*ax[0]+(n-1)*ax[1]+frm[0]+frm[1]
    frm=np.array(frm)
    ax=np.array(ax)
    if not (norm.__class__==False.__class__ and not norm): # This checks that it is not the default.
        frm=frm/sz*norm
        ax=ax/sz*norm
        sz=norm
    v=np.array([frm[0],(sz-frm[1]),ax[1]])/sz
    return sz,v

def calcAxesSize(n,totsize,gap,frame):
    """
    Calculate the width of each axes, based on the total figure width
    (height) *totsize*, the desired frame size, *frame*, the desired
    spacing between axes *gap* and the number of axes *n*.

    calcAxesSize returns the size each axes should be, along with the
    three element vector for input to saxes.

    See also: saxes, axes, calcFigSize
    """
    if hasattr(gap,'__len__'):
        gtot=np.sum(gap[:n])
    else:
        gtot=gap*(n-1)
    axsz=(totsize-frame[0]-frame[1]-gtot)/n
    sz,v=calcFigSize(n,[axsz,gap],frame,False)
    return axsz,v


def calcAxesSpacer(n,totsize,gap,frame):
    """
    Calculate the width of each axes, based on the total figure width
    (height) *totsize*, the desired frame size, *frame*, the desired
    spacing between axes *gap* and the number of axes *n*.

    calcAxesSize returns the size each axes should be, along with the
    three element vector for input to saxes.

    See also: saxes, axes, calcFigSize
    """
    if hasattr(gap,'__len__'):
        gtot=np.sum(gap[:n])
    else:
        gtot=gap*(n-1)
    axsz=(totsize-frame[0]-frame[1]-gtot)/n
    sz,v=calcFigSize(n,[axsz,gap],frame,False)
    return axsz,v

def axvec2axSpacer(n,vec,vertflag,rel=False):
    """
    Returns an :class:`axSpacer` corresponding to the `n` axes based
    on the axes vector `vec`.

    Parameters
    ----------
    n : int
        The number of axes.
    vec : iterable(3)
          The (left/bottom,right/top,gap) surrounding and between
          the axes.
    vertflag : bool, optional (default: False)
               Specifies this is for vertical (True) or horizontal
               spacing.
    rel : iterable(`n`), optional
          This specifies the relative width of each of the axes. By
          default all axes are the same width.

    Returns
    -------
    axSpacer : :class:`axSpacer`
               The axes spacer object corresponding to the specified
               inputs.

    Notes
    -----

    The units of the returned axSpacer match that of the input `vec`.

    """
    if rel.__class__==False.__class__ and not rel: # This checks for the default value.
        rel=np.ones(n)
    wd=(((vec[1]-vec[0])+vec[2])/n-vec[2])*rel/rel.mean()
    gap=np.empty((len(wd)+1),dtype=wd.dtype)
    gap[0]=vec[0]
    gap[1:-1]=vec[2]
    gap[-1]=vec[1]
    return axSpacer(wd,gap,vertflag)
    

def axvec2axpos(n,vec,vertflag=False,rel=False):
    """
    calculates the positions for the `n` axes, based on the axes
    vector `vec`.

    Parameters
    ----------
    n : int
        The number of frames to make.
    vec : iterable(3)
          The (left/bottom,right/top,gap) surrounding and between
          the axes.
    vertflag : bool, optional (default: False)
               Specifies this is for vertical (True) or horizontal
               spacing.
    rel : iterable(`n`), optional
          This specifies the relative width of each of the axes. By
          default all axes are the same width.

    Returns
    -------
    pos : iterable(`n`)
          specifies the position of each axes.
    wd : iterable(`n`)
         Specifies the width of each axes. Each entry will be the same
         unless `rel` is specified.

    Notes
    -----

    The units of the returned variables match that of the input `vec`.

    """

    if rel.__class__==False.__class__ and not rel: # This checks for the default value.
        rel=np.ones(n)
    wd=(((vec[1]-vec[0])+vec[2])/n-vec[2])*rel/rel.mean()
    if vertflag:
        pos=vec[1]-(wd+vec[2]).cumsum().reshape((n,1))+vec[2]
        wd=wd.reshape((n,1))
    else:
        pos=vec[0]+(wd+vec[2]).cumsum().reshape((1,n))-wd-vec[2]
        wd=wd.reshape((1,n))
    return pos,wd

