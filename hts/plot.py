import matplotlib as mpl
import ptools.superaxes as sax
import ptools as pt
import numpy as np

class specfig(sax.figobj):

    def __init__(self,fignum=661,ncol=1,axsize=3):
        nax=(3,ncol)
        sax.figobj.__init__(self,fignum,nax=nax,axsize=axsize,sharex=True,sharey=True)
        self.uax={'u':self.sax.ax[0],'v':self.sax.ax[1],'w':self.sax.ax[2]}
        self.sax.hide(['xticklabels','yticklabels'])

def plot_spectra(tsdata,fignum=1001,nfft=1024,igrid=None):
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

    def __init__(self,fignum=662,axsize=[3,3],spacing=[.4,.8],frame=[1,.7,1,.3],nfft=1024,title=None):
        n=(3,[.8,1,1,.8,.8])
        figh,v=pt.calcFigSize(n[0],[axsize[0],spacing[0]],frame[:2])
        figw,h=pt.calcFigSize(n[1],[axsize[1],spacing[1]],frame[2:])
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
        self.axgrid=sax.saxes(n=n,h=h,v=v,sharex=sharex,sharey=sharey)
        self.axgrid.drawall()
        self.pax=self.axgrid[:,0]
        self.sax=self.axgrid[:,1]
        self.cax=self.axgrid[:,2]
        self.tax=self.axgrid[:,3]
        self.rsax=self.axgrid[:,4]
        self.pax[0].set_title('Velocity Profile')
        self.cax[0].set_title('Coherence')
        self.sax[0].set_title('Spectrum')
        self.rsax[0].set_title('Stresses')
        self.tax[0].set_title('Energy')
        self.axgrid.hide(['xticklabels','yticklabels'],self.axgrid.ax[-1,:])
        self.pax[0].annoteCorner('$u$','ul',fontsize='x-large')
        self.pax[1].annoteCorner('$v$','ul',fontsize='x-large')
        self.pax[2].annoteCorner('$w$','ul',fontsize='x-large')
        self.rsax[0].annoteCorner(r"$\langle{u'w'}\rangle$",'ul',fontsize='x-large')
        self.rsax[1].annoteCorner(r"$\langle{v'w'}\rangle$",'ul',fontsize='x-large')
        self.rsax[2].annoteCorner(r"$\langle{u'v'}\rangle$",'ul',fontsize='x-large')
        self.pax.vln(0,color='k',ls='--')
        self.rsax.vln(0,color='k',ls='--')

    def set_title(self,title):
        if title is not None:
            self.fig.canvas.set_window_title('Figure %d: %s' % (self.fig.number,title))
            self.fig.text(.5,.99,title,ha='center',va='top',fontsize='x-large')

    def reshape(self,arr):
        shp=arr.shape
        npt=shp[-1]/self.nfft
        return arr[...,self.nfft*npt].reshape(list(shp[:-1])+[self.nfft,npt])

    @property
    def iy(self,):
        return self.igrid[1]
    @property
    def iz(self,):
        return self.igrid[0]

    def plot_prof(self,tsdata,**kwargs):
        prf=tsdata.uprof
        for ind in range(3):
            self.pax[ind].plot(tsdata.uprof[ind][:,self.iy],tsdata.z,**kwargs)

    def plot_tke(self,tsdata,**kwargs):
        prf=tsdata.uprof
        for ind in range(3):
            self.tax[ind].plot((tsdata.uturb[ind][:,self.iy]**2).mean(-1),tsdata.z,**kwargs)

    def plot_rs(self,tsdata,factor=1e4,**kwargs):
        prf=tsdata.uprof
        self.rs_factor=factor
        self.rsax[0].plot(factor*(tsdata.uturb[0][:,self.iy]*tsdata.uturb[2][:,self.iy]).mean(-1),tsdata.z,**kwargs)
        self.rsax[1].plot(factor*(tsdata.uturb[1][:,self.iy]*tsdata.uturb[2][:,self.iy]).mean(-1),tsdata.z,**kwargs)
        self.rsax[2].plot(factor*(tsdata.uturb[0][:,self.iy]*tsdata.uturb[1][:,self.iy]).mean(-1),tsdata.z,**kwargs)

    def plot_profpt(self,tsdata,**kwargs):
        prf=tsdata.uprof
        for ind in range(3):
            self.pax[ind].plot(tsdata.uprof[ind][self.igrid],tsdata.z[self.iz],'o',**kwargs)

    def setinds(self,tsdata,igrid=None,icoh=None):
        if igrid is None:
            self.igrid=tsdata.ihub
        else:
            self.igrid=igrid
        if icoh is None:
            self.icoh=(0,0)
        else:
            self.icoh=icoh
    
    def plot_spec(self,tsdata,theory_line=False,**kwargs):
        for ind in range(3):
            p,f=mpl.mlab.psd(tsdata.uturb[ind][self.igrid],self.nfft,1./tsdata.dt,detrend=mpl.pylab.detrend_linear,noverlap=self.nfft/2)
            self.sax[ind].loglog(f,p,**kwargs)
            if hasattr(tsdata,'tm') and theory_line:
                self.sax[ind].loglog(tsdata.tm.f,tsdata.tm.Suu[ind][self.igrid],'k--',zorder=10)

    def plot_coh(self,tsdata,**kwargs):
        for ind in range(3):
            p,f=mpl.mlab.cohere(tsdata.uturb[ind][self.igrid],tsdata.uturb[ind][self.icoh],self.nfft,1./tsdata.dt,detrend=mpl.pylab.detrend_linear,noverlap=self.nfft/2,scale_by_freq=False)
            self.cax[ind].semilogx(f,p,**kwargs)
            #if hasattr(tsdata,'tm') and theory_line:
            #    self.sax[ind].loglog(tsdata.tm.f,tsdata.tm.Suu[ind][igrid])

    def finish(self,):
        self.cax[0].set_ylim([0,1])
        self.rsax[0].set_xlim([-1,1])
        xlm=self.pax[0].get_xlim()
        if xlm[0]>=0:
            dxlm=np.diff(xlm)
            if dxlm>10:
                self.pax[0].set_xlim([-10,xlm[1]])
            else:
                self.pax[0].set_xlim([-1,xlm[1]])
        self.pax[-1].set_xlabel('$u,v,w/\mathrm{[m/s]}$')
        self.sax[-1].set_xlabel('$f/\mathrm{[hz]}$')
        self.cax[-1].set_xlabel('$f/\mathrm{[hz]}$')
        self.pax[-1].set_ylabel('$z/\mathrm{[m]}$')
        self.sax[-1].set_ylabel('$S_{xx}/\mathrm{[m^2s^{-2}/hz]}$')
        self.rsax[-1].set_xlabel('$\mathrm{10^{%d}[m^2s^{-2}]}$' % np.log10(self.rs_factor))
        self.sax[0].legend(loc=1)
        self.tax[-1].set_xlim([0,None])
        

    def plot(self,tsdata,theory_line=False,**kwargs):
        kwargs['alpha']=kwargs.get('alpha',0.8)
        self.plot_prof(tsdata,**kwargs)
        self.plot_profpt(tsdata,**kwargs)
        self.plot_spec(tsdata,theory_line=theory_line,**kwargs)
        self.plot_coh(tsdata,**kwargs)
        self.plot_tke(tsdata,**kwargs)
        self.plot_rs(tsdata,**kwargs)
        

def showts(tsdata,fignum=2001,nfft=1024,igrid=None,icoh=None,**kwargs):
    if fignum.__class__ is summfig:
        fg=fignum
    else:
        fg=summfig(fignum)
        fg.setinds(igrid,icoh,tsdata)
    fg.plot_prof(tsdata,**kwargs)
    
    
