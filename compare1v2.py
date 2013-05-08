import ts2.plot
import ts2.tsio

fnames=['Tidal','Smooth','IecKai','IecVkm','GPllj','NWTCup','wfup','wf07d','wf14d',]
#fnames=['Smooth','IecKai','IecVkm','GPllj','NWTCup','wfup','wf07d','wf14d',]
fnames=['IecVkm'] #CHECKED 4/26/2013
fnames=['IecKai'] #CHECKED 4/26/2013
fnames=['Smooth'] #CHECKED 4/26/2013
#fnames=['Tidal'] #CHECKED 4/26/2013
#fnames=['GPllj']
#fnames=['River'] #CHECKED 4/26/2013
#fnames=['NWTCup'] #CHECKED 4/26/2013

c=0
ftp='.bts'
ftp='.wnd'

for nm in fnames:
    c+=1
    od=ts2.tsio.readModel('../../nwtc/turbsim_mod/'+nm+ftp)
    od.tm=ts2.buildModel(od.config)
    nw=ts2.tsio.readModel(nm+ftp)
    nw.tm=ts2.buildModel(nw.config)
    
    fg=ts2.plot.summfig(3000+c,nfft=1024,title=nm.upper()+' spectral model')
    fg.setinds(nw,igrid=None,)
    #fg.setinds(nw,igrid=(0,1),)
    fg.plot(od,color='r',label='TSv1')
    fg.plot(nw,color='b',theory_line=True,label='TSv2')
    fg.finish()

