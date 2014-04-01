import matplotlib as mpl
import superaxes as supax
import numpy as np

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
    
    
