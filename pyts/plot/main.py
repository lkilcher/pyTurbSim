import matplotlib as mpl
import superaxes as supax
import numpy as np
from ..main import tsdata,tsrun

indx={'u':0,'v':1,'w':2}

def psd(u,sr,nfft):
    """
    Helper function to compute the power spectral density (PSD) of a signal.

    Parameters
    ----------
    u : array_like
        The signal to compute the PSD of.
    sr : float
         The sample rate of `u`.
    nfft : The number of points to use in computing the fft.

    Returns
    -------
    p : array_like
        The power in the signal `u` as a function of frequency (units of u squared/units of sr)
    f : array_like
        Frequency (same units as sr).
    """
    p,f=mpl.mlab.psd(u,nfft,sr,detrend=mpl.pylab.detrend_linear,noverlap=nfft/2)
    return f[...,1:],p[...,1:]

def coh(u1,u2,sr,nfft):
    """
    Helper function to compute the coherence between two signals.

    Parameters
    ----------
    u1 : array_like
        Signal 1.
    u2 : array_like
        Signal 2.
    sr : float
         The sample rate of `u`.
    nfft : The number of points to use in computing the fft.

    Returns
    -------
    p : array_like
        The coherence between the two signal (no units) as a function of frequency.
    f : array_like
        Frequency (same units as sr).
    """
    p,f=mpl.mlab.cohere(u1,u2,nfft,sr,detrend=mpl.pylab.detrend_linear,noverlap=nfft/2,scale_by_freq=False)
    return f[...,1:],p[...,1:]

class base_axForm(object):
    """
    A base class for 'plotting formats' for quick plotting of TurbSim
    data.
    """
    method_map={tsdata:'_calc_tsdata',tsrun:'_calc_tsrun'}
    hide_ylabels=False
    _lin_x_scale=0
    _xscale='linear'
    _yscale='linear'
    
    def finalize(self,axes):
        """
        This function 'finishes' the `axes` according to the
        specifications in this axesType.

        Parameters
        ----------
        axes : A :class:`superaxes.axgroup` instance.
        """
        axes.hide('xticklabels',ax=axes[-1])
        if self.hide_ylabels:
            axes.hide('yticklabels')
        if not self.hide_ylabels and hasattr(self,'_ylabel'):
            for ax in axes:
                ax.set_ylabel(self._ylabel)
        if hasattr(self,'_xlabel'):
            axes[-1].set_xlabel(self._xlabel)
        if hasattr(self,'_title'):
            axes[0].set_title(self._title)
        if hasattr(self,'_grid_x'):
            for ax in axes:
                for val in self._grid_x:
                    ax.vln(val,linestyle=':',color='k',zorder=-10)
        if hasattr(self,'_labels'):
            for ax in axes:
                ax.annoteCorner(self._labels[ax.comp],pos='ul')

    def _calc(self,obj,comp):
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
            comp=indx[comp]
        for cls,meth in self.method_map.iteritems():
            if cls in obj.__class__.__mro__:
                if not hasattr(self,meth):
                    return np.NaN,np.NaN
                return getattr(self,meth)(obj,comp)
        raise Exception('Object type %s not recognized for %s axes-type' % (obj.__class__,self.__class__))

    def plot(self,obj,axes,**kwargs):
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
            x,y=self._calc(obj,ax.comp)
            ax.plot(x/(10**self._lin_x_scale),y,**kwargs)
            ax.set_xscale(self._xscale)
            ax.set_yscale(self._yscale)
        
    @property
    def _xlabel(self,):
        if self._lin_x_scale==0:
            return '$\mathrm{[m^2s^{-2}]}$'
        else:
            return '$\mathrm{[10^{%d}m^2s^{-2}]}$' % self._lin_x_scale

class prof_axForm(base_axForm):
    """
    A base class for plotting formats that show vertical profiles.
    """
    yax='z'
    _ylabel='$z\,\mathrm{[m]}$'
    hrel=0.6

class velprof_axForm(prof_axForm):
    """
    A 'mean velocity profile' plotting format.

    Parameters
    ----------
    xlim : tuple_like(2)
           The limits of the x-axis (velocity axis).
    """
    xax='vel'
    _title='Mean Velocity'
    _xlabel='$\mathrm{[m/s]}$'
    
    def __init__(self,xlim=[0,2]):
        self._xlim_dat=xlim

    def _calc_tsdata(self,tsdata,comp,igrid=None):
        """
        The function that calculates x,y values for plotting
        :class:`tsdata <..main.tsdata>` objects.
        """
        return tsdata.uprof[comp,:,tsdata.ihub[1]],tsdata.z
    
    def _calc_tsrun(self,tsrun,comp,igrid=None):
        """
        The function that calculates x,y values for plotting
        :class:`tsdata <..main.tsdata>` objects.
        """
        return tsrun.prof[comp,:,tsrun.grid.ihub[1]],tsrun.grid.z

class tkeprof_axForm(prof_axForm):
    """
    A 'tke profile' plotting formatter.

    Parameters
    ----------
    xlim : tuple,list (2)
           The limits of the x-axis (tke axis).
    """
    xax='tke'
    _title='tke'
    _lin_x_scale=-2 # Units are 10^-2
    
    def __init__(self,xlim=[0,None]):
        self._xlim_dat=xlim

    def _calc_tsdata(self,tsdata,comp,igrid=None):
        return tsdata.tke[comp,:,tsdata.ihub[1]],tsdata.z

    def _calc_tsrun(self,tsrun,comp,igrid=None):
        return tsrun.spec.tke[comp,:,tsrun.grid.ihub[1]],tsrun.grid.z


class stressprof_axForm(tkeprof_axForm):
    """
    A 'Reynold's stress profile' plotting format.

    Parameters
    ----------
    xlim : tuple, list (2)
           The limits of the x-axis (stress axis).
    """
    xax='tke'
    _title='stress'
    _lin_x_scale=-2 # Units are 10^-2
    _grid_x=[0]
    _labels={'u':r"$\overline{u'v'}$",'v':r"$\overline{u'w'}$",'w':r"$\overline{v'w'}$"}
    
    def __init__(self,xlim=[0,None]):
        self._xlim_dat=xlim

    def _calc_tsdata(self,tsdata,comp,igrid=None):
        igrid=igrid or tsdata.ihub[1]
        return tsdata.stress[comp,:,igrid],tsdata.z

    def _calc_tsrun(self,tsrun,comp,igrid=None):
        igrid=igrid or tsrun.grid.ihub[1]
        return tsrun.stress.array[comp,:,igrid],tsrun.grid.z
        

class spec_axForm(base_axForm):
    """
    A 'spectral' plotting format.

    Parameters
    ----------
    window_time_sec : float
                      the length of the fft window (seconds).
    igrid : tuple,list (2), *optional* (default: i_hub)
            The spatial-index of the grid-point that should be
            plotted.
    """
    hrel=1
    _title='spectrum'
    yax='spec'
    xax='freq'
    _xlabel='$f\,\mathrm{[Hz]}$'
    _ylabel='$\mathrm{[m^2s^{-2}/Hz]}$'
    _xscale='log'
    _yscale='log'
    
    def __init__(self,window_time_sec=600,igrid=None):
        self.window_time=600
        self.igrid=igrid

    def _calc_tsdata(self,tsdata,comp,igrid=None):
        nfft=int(self.window_time/tsdata.dt)
        nfft+=np.mod(nfft,2)
        igrid = igrid or self.igrid or tsdata.ihub
        return psd(tsdata.uturb[comp][igrid],1./tsdata.dt,nfft)

    def _calc_tsrun(self,tsrun,comp,igrid=None):
        igrid = igrid or self.igrid or tsrun.grid.ihub
        return tsrun.grid.f,tsrun.spec[comp][igrid]

    
class cohere_axForm(base_axForm):
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
    """
    hrel=1
    _title='coherence'
    xax='freq'
    yax='coh'
    _xlim_dat=[0,1]
    _xlabel='$f\,\mathrm{[Hz]}$'
    _xscale='log'
    
    def __init__(self,window_time_sec=600,igrid0=None,igrid1=None):
        self.window_time=600
        self.igrid0=igrid0
        self.igrid1=igrid1
    
    def _calc_tsdata(self,tsdata,comp,igrid0=None,igrid1=None):
        nfft=int(self.window_time/tsdata.dt)
        nfft+=np.mod(nfft,2)
        igrid0=igrid0 or self.igrid0 or tsdata.ihub
        igrid1=igrid1 or self.igrid1 or (0,0)
        return coh(tsdata.uturb[comp][igrid0],tsdata.uturb[comp][igrid1],1./tsdata.dt,nfft)

    def _calc_tsrun(self,tsrun,comp,igrid0=None,igrid1=None):
        igrid0=tsrun.grid.sub2ind(igrid0 or self.igrid0 or tsrun.grid.ihub)
        igrid1=tsrun.grid.sub2ind(igrid1 or self.igrid1 or (0,0))
        return tsrun.grid.f,tsrun.cohere.calcCoh(tsrun.grid.f,comp,igrid0,igrid1)**2

class fig_axForms(supax.sfig):
    """
    The 'figure' class that uses and handles 'plotting formats'
    (e.g. :class:`velprof_axForm`).

    Parameters
    ----------
    fignum : integer,string
             The figure number, or string, into which the data will be
             plotted.
    axforms : list of axForms (e.g. :class:`velprof_axForm`, :class:`tkeprof_axForm`)
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
    def __init__(self,fignum,axforms=[],comp=['u','v','w'],axsize=2,frame=[.6,.3,1,.3],gap=[.2,1],tightgap=.2,**kwargs):
        
        if len(axforms)==0:
            raise Exception('At least one axes-type instance must be provided.')
        
        sharex=np.tile(np.arange(len(axforms),dtype=np.uint8)+1,(len(comp),1))
        sharey=np.tile(np.arange(len(axforms),dtype=np.uint8)+1,(len(comp),1))
        hspacer=supax.simpleAxSpacer(len(axforms),axsize,gap[1],frame[2:])
        vspacer=supax.simpleAxSpacer(len(comp),axsize,gap[0],frame[:2],vertical=True)
        last_yax=None
        for idx,axt in enumerate(axforms):
            if axt.yax==last_yax:
                sharey[:,idx]=sharey[:,idx-1]
                hspacer.gap[idx]=tightgap
                axt.hide_ylabels=True
            last_yax=axt.yax
            if hasattr(axt,'hrel'):
                hspacer.axsize[idx]*=axt.hrel
        axp=supax.axPlacer(vspacer,hspacer)
        supax.sfig.__init__(self,fignum,axp,sharex=sharex,sharey=sharey,**kwargs)
        self.comp=comp
        for idx,axt in enumerate(axforms):
            for c,ax in zip(comp,self.sax[:,idx]):
                ax.comp=c
        self.axforms=axforms

    def plot(self,obj,**kwargs):
        """
        Plot the data in `obj` to the figure according to the plotting formats.

        Parameters
        ----------
        obj : tsdata, tsrun, turbdata
              A data or turbsim object to plot.
        """
        for idx,axt in enumerate(self.axforms):
            axt.plot(obj,self.sax[:,idx],**kwargs)
            

    def finalize(self,):
        """
        Finalize the figure according to the plotting formats.
        """
        for idx,axt in enumerate(self.axforms):
            axt.finalize(self.sax[:,idx])
        for c,ax in zip(self.comp,self.ax[:,0]):
            p=ax.get_position().ymax
            self.fig.text(0.02,p,'$'+c+'$',va='top',ha='left',size='x-large',backgroundcolor='w')

def new_summ_fig(fignum=400,axforms=[velprof_axForm(),spec_axForm(600)],**kwargs):
    return fig_axForms(fignum,axforms=axforms,**kwargs)

        
class specfig(supax.figobj):
    """
    A base class for plotting spectra.
    """
    def __init__(self,fignum=661,ncol=1,axsize=3):
        nax=(3,ncol)
        supax.figobj.__init__(self,fignum,nax=nax,axsize=axsize,sharex=True,sharey=True)
        self.uax={'u':self.sax.ax[0],'v':self.sax.ax[1],'w':self.sax.ax[2]}
        self.sax.hide(['xticklabels','yticklabels'])

def plot_spectra(tsdata,fignum=1001,nfft=1024,igrid=None):
    """
    Plots the spectra of TurbSim output.
    """
    if fignum.__class__ is specfig:
        fg=fignum
    else:
        fg=specfig(fignum)
    if igrid is None:
        igrid=tsdata.ihub
    for ind in range(3):
        p,f=mpl.mlab.psd(tsdata.uturb[ind][igrid],nfft,1./tsdata.dt,detrend=mpl.pylab.detrend_linear,noverlap=nfft/2)
        fg.sax.ax[ind,0].loglog(f,p)
        if hasattr(tsdata,'tm'):
            fg.sax.ax[ind,0].loglog(tsdata.tm.f,tsdata.tm.Suu[ind][igrid])
    return fg

class summfig(object):
    """
    A figure object for plotting TurbSim output statistics (mean velocity profile, spectra, coherence, tke profile and the Reynolds Stress profile.
    """
    def __init__(self,fignum=662,axsize=[3,3],spacing=[.4,.8],frame=[1,.7,1,.3],nfft=1024,title=None):
        """
        Set up the figure.
        """
        n=(3,[.8,1,1,.8,.8])
        figh,v=supax.calcFigSize(n[0],[axsize[0],spacing[0]],frame[:2])
        figw,h=supax.calcFigSize(n[1],[axsize[1],spacing[1]],frame[2:])
        self.nfft=nfft
        self.fig=mpl.pylab.figure(fignum,figsize=(figw,figh))
        self.fig.clf()
        self.set_title(title)
        sharex=np.ones((n[0],len(n[1])),dtype=np.int16)
        sharey=np.ones((n[0],len(n[1])),dtype=np.int16)
        sharex[:,0]=2
        sharey[:,0]=2
        sharex[:,1:]=3
        sharey[:,1]=4
        sharey[:,2]=5
        sharex[:,3]=4
        sharex[:,4]=5
        self.axgrid=supax.saxes(n=n,h=h,v=v,sharex=sharex,sharey=sharey)
        self.axgrid.drawall()
        self.ax_prof=self.axgrid[:,0]
        self.ax_spec=self.axgrid[:,1]
        self.ax_cohr=self.axgrid[:,2]
        self.ax_tke=self.axgrid[:,3]
        self.ax_rstr=self.axgrid[:,4]
        self.ax_prof[0].set_title('Velocity Profile')
        self.ax_cohr[0].set_title('Coherence')
        self.ax_spec[0].set_title('Spectrum')
        self.ax_rstr[0].set_title('Stresses')
        self.ax_tke[0].set_title('Energy')
        self.axgrid.hide(['xticklabels','yticklabels'],self.axgrid.ax[-1,:])
        self.ax_prof[0].annoteCorner('$u$','ul',fontsize='x-large')
        self.ax_prof[1].annoteCorner('$v$','ul',fontsize='x-large')
        self.ax_prof[2].annoteCorner('$w$','ul',fontsize='x-large')
        self.ax_rstr[0].annoteCorner(r"$\langle{u'v'}\rangle$",'ul',fontsize='x-large')
        self.ax_rstr[1].annoteCorner(r"$\langle{u'w'}\rangle$",'ul',fontsize='x-large')
        self.ax_rstr[2].annoteCorner(r"$\langle{v'w'}\rangle$",'ul',fontsize='x-large')
        self.ax_prof.vln(0,color='k',ls='--')
        self.ax_rstr.vln(0,color='k',ls='--')

    def set_title(self,title):
        """
        Set the title of the figure.
        """
        if title is not None:
            self.fig.canvas.set_window_title('Figure %d: %s' % (self.fig.number,title))
            self.fig.text(.5,.99,title,ha='center',va='top',fontsize='x-large')

    ## def reshape(self,arr):
    ##     shp=arr.shape
    ##     npt=shp[-1]/self.nfft
    ##     return arr[...,self.nfft*npt].reshape(list(shp[:-1])+[self.nfft,npt])

    def plot_prof(self,tsdata,**kwargs):
        """
        Plot the mean velocity profile of the input *tsdata* object (at the 'iy' grid index of this summfig object).

        *kwargs* are passed to the 'plot' function.
        
        """
        prf=tsdata.uprof
        for ind in range(3):
            self.ax_prof[ind].plot(tsdata.uprof[ind][:,self.igrid[1]],tsdata.z,**kwargs)

    def plot_tke(self,tsdata,factor=1e4,**kwargs):
        """
        Plot the tke profile of the input *tsdata* object (at the 'iy' grid index of this summfig instance).

        *kwargs* are passed to the 'plot' function.
        
        """
        prf=tsdata.uprof
        self.tke_factor=factor
        for ind in range(3):
            self.ax_tke[ind].plot((tsdata.uturb[ind][:,self.igrid[1]]**2).mean(-1)*factor,tsdata.z,**kwargs)

    def plot_rs(self,tsdata,factor=1e4,*args,**kwargs):
        """
        Plot the Reynolds stress profile of the input *tsdata* object (at the 'iy' grid index of this summfig instance).

        *kwargs* are passed to the 'plot' function.
        
        """
        prf=tsdata.uprof
        self.rs_factor=factor
        self.ax_rstr[0].plot(factor*(tsdata.uturb[0][:,self.igrid[1]]*tsdata.uturb[1][:,self.igrid[1]]).mean(-1),tsdata.z,*args,**kwargs)
        self.ax_rstr[1].plot(factor*(tsdata.uturb[0][:,self.igrid[1]]*tsdata.uturb[2][:,self.igrid[1]]).mean(-1),tsdata.z,*args,**kwargs)
        self.ax_rstr[2].plot(factor*(tsdata.uturb[1][:,self.igrid[1]]*tsdata.uturb[2][:,self.igrid[1]]).mean(-1),tsdata.z,*args,**kwargs)

    def plot_profpt(self,tsdata,**kwargs):
        """
        Plot a circle on the velocity profile at the point where the spectra are taken from for this summfig instance (iz,iy).
        """
        prf=tsdata.uprof
        kw1=dict(kwargs)
        kw2=dict(kwargs)
        kw1.setdefault('ms',6)
        kw1.setdefault('mec','none')
        kw1.setdefault('mfc','b')
        kw2.setdefault('ms',10)
        kw2.setdefault('mec','b')
        kw2.setdefault('mfc','none')
        if not (hasattr(kw1,'markersize') or hasattr(kw1,'ms')):
            kw1['ms']=6
        if not (hasattr(kw1,'markersize') or hasattr(kw1,'ms')):
            kw1['ms']=6
        for ind in range(3):
            self.ax_prof[ind].plot(tsdata.uprof[ind][self.igrid],tsdata.z[self.igrid[0]],'o',**kw1)
            self.ax_prof[ind].plot(tsdata.uprof[ind][self.icoh],tsdata.z[self.icoh[0]],'o',**kw2)
    
    @property
    def igrid(self,):
        if not hasattr(self,'_igrid'):
            self._igrid=(0,0)
        return self._igrid
    @igrid.setter
    def igrid(self,val):
        self._igrid=val
    @property
    def icoh(self,):
        if not hasattr(self,'_icoh'):
            self._icoh=(-1,-1)
        return self._icoh
    @icoh.setter
    def icoh(self,val):
        self._icoh=val
    
    def setinds(self,tsdata,igrid=None,icoh=None):
        """
        Set the (iz,iy) indices for this summfig instance.
        """
        if igrid is None:
            self.igrid=tsdata.ihub
        else:
            self.igrid=igrid
        if icoh is None:
            self.icoh=(0,0)
        else:
            self.icoh=icoh
    
    def plot_spec(self,tsdata,theory_line=False,*args,**kwargs):
        """
        Plot the spectrum (point iz,iy) of the input *tsdata* TurbSim data object.
        """
        for ind in range(3):
            p,f=mpl.mlab.psd(tsdata.uturb[ind][self.igrid],self.nfft,1./tsdata.dt,detrend=mpl.pylab.detrend_linear,noverlap=self.nfft/2)
            self.ax_spec[ind].loglog(f,p,**kwargs)
            if hasattr(tsdata,'tm') and theory_line:
                self.ax_spec[ind].loglog(tsdata.tm.f,tsdata.tm.Suu[ind][self.igrid],'k--',zorder=10)

    def plot_theory(self,tsrun,*args,**kwargs):
        for ind in range(3):
            self.ax_prof[ind].plot(tsrun.prof.array[ind].mean(-1),tsrun.grid.z,*args,**kwargs)
            self.ax_spec[ind].loglog(tsrun.grid.f,tsrun.spec.array[ind][self.igrid],*args,**kwargs)
            #print tsrun.grid.sub2ind(self.icoh),tsrun.grid.sub2ind(self.igrid)
            self.ax_cohr[ind].semilogx(tsrun.grid.f,tsrun.cohere.calcCoh(tsrun.grid.f,ind,tsrun.grid.sub2ind(self.igrid),tsrun.grid.sub2ind(self.icoh))**2,*args,**kwargs)
            self.ax_tke[ind].plot(tsrun.spec.tke[ind].mean(-1)*self.tke_factor,tsrun.grid.z,*args,**kwargs)
            self.ax_rstr[ind].plot(tsrun.stress.array[ind].mean(-1)*self.rs_factor,tsrun.grid.z,*args,**kwargs)
        

    def plot_coh(self,tsdata,*args,**kwargs):
        """
        Plot the coherence of the input *tsdata* TurbSim data object (between points iz,iy and icohz,icohy).
        """
        for ind in range(3):
            p,f=mpl.mlab.cohere(tsdata.uturb[ind][self.igrid],tsdata.uturb[ind][self.icoh],self.nfft,1./tsdata.dt,detrend=mpl.pylab.detrend_linear,noverlap=self.nfft/2,scale_by_freq=False)
            self.ax_cohr[ind].semilogx(f,p,*args,**kwargs)
            #if hasattr(tsdata,'tm') and theory_line:
            #    self.ax_spec[ind].loglog(tsdata.tm.f,tsdata.tm.Suu[ind][igrid])

    def finish(self,):
        """
        Finalize the figure.
        """
        self.ax_cohr[0].set_ylim([0,1])
        #self.ax_rstr[0].set_xlim([-1,1])
        xlm=self.ax_prof[0].get_xlim()
        if xlm[0]>=0:
            dxlm=np.diff(xlm)
            if dxlm>10:
                self.ax_prof[0].set_xlim([-10,xlm[1]])
            else:
                self.ax_prof[0].set_xlim([-1,xlm[1]])
        self.ax_prof[-1].set_xlabel('$u,v,w/\mathrm{[m/s]}$')
        self.ax_spec[-1].set_xlabel('$f/\mathrm{[hz]}$')
        self.ax_cohr[-1].set_xlabel('$f/\mathrm{[hz]}$')
        self.ax_prof[-1].set_ylabel('$z/\mathrm{[m]}$')
        self.ax_spec[-1].set_ylabel('$S_{xx}/\mathrm{[m^2s^{-2}/hz]}$')
        self.ax_rstr[-1].set_xlabel('$\mathrm{10^{%d}[m^2s^{-2}]}$' % np.log10(self.rs_factor))
        self.ax_tke[-1].set_xlabel('$\mathrm{10^{%d}[m^2s^{-2}]}$' % np.log10(self.tke_factor))
        self.ax_spec[0].legend(loc=1)
        self.ax_tke[-1].set_xlim([0,None])
        

    def plot(self,tsdata,theory_line=False,**kwargs):
        """
        Plot all of the variables (mean profile, spectrum, coherence, tke, stress) for this summfig object
        """
        kwargs['alpha']=kwargs.get('alpha',0.8)
        self.plot_prof(tsdata,**kwargs)
        self.plot_profpt(tsdata,**kwargs)
        self.plot_spec(tsdata,theory_line=theory_line,**kwargs)
        self.plot_coh(tsdata,**kwargs)
        self.plot_tke(tsdata,**kwargs)
        self.plot_rs(tsdata,**kwargs)

    def savefig(self,*args,**kwargs):
        kwargs.setdefault('dpi',300)
        return self.fig.savefig(*args,**kwargs)

def showts(tsdata,fignum=2001,nfft=1024,igrid=None,icoh=None,**kwargs):
    if fignum.__class__ is summfig:
        fg=fignum
    else:
        fg=summfig(fignum)
        fg.setinds(igrid,icoh,tsdata)
    fg.plot_prof(tsdata,**kwargs)
    
    
