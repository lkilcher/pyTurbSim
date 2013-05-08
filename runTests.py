import ts2
from subprocess import call
import os

fnames=['Tidal','Smooth','IecKai','IecVkm','GPllj','NWTCup','wfup','wf07d','wf14d',]
#fnames=['Smooth','IecKai','IecVkm','GPllj','NWTCup','wfup','wf07d','wf14d',]
fnames=['Tidal']
fnames=['IecVkm']
fnames=['IecKai']
fnames=['NWTCup']
#fnames=['River']


if __name__=='__main__':

    for fnm in fnames:
        ts2.run(fnm+'.inp')
        os.chdir('../../nwtc/turbsim_mod')
        call(['./TurbSim',fnm+'.inp'])
        os.chdir('../../mhk/turbsim2/')

