import sys
import os
if '../' not in sys.path:
    sys.path.append('../')
import pyts
import pyts_plot
import pyts.tsio
from subprocess import call

# This is the file type that the .inp files (in inp_files directory) are configured to output.
# It can be changed, but if it is the input files should be configured to output different files also.
ts_file_type='.wnd'

# Run TurbSim and HydroTurbSim?
flag_run=False# or True
# Plot the results and compare?
flag_plot=False or True

########################################################################################
## These are the name of the input files (in ./inp_files/) that are run and compared. ##
fnames=['Tidal','Smooth','IecKai','IecVkm','GPllj','NWTCup','wfup','wf07d','wf14d',]
#fnames=['Smooth','IecKai','IecVkm','GPllj','NWTCup','wfup','wf07d','wf14d',]
fnames=['IecVkm'] #CHECKED 4/26/2013
fnames=['IecKai'] #CHECKED 4/26/2013
fnames=['Smooth'] #CHECKED 4/26/2013
#fnames=['Tidal'] #CHECKED 4/26/2013
#fnames=['GPllj']
#fnames=['River'] #CHECKED 4/26/2013
#fnames=['NWTCup'] #CHECKED 4/26/2013

# Make sure the output-file directories exist:
try:
    os.mkdir('./ts/')
except:
    pass
try:
    os.mkdir('./pyts/')
except:
    pass

#############################
#############################
# Run the turbsim programs ##
#############################
if flag_run:
    # Check to see that a TurbSim executable exists:
    if sys.platform.startswith('win'):
        if os.path.isfile('TurbSim.exe'):
            ts_exec_file='TurbSim.exe'
        elif os.path.isfile('TurbSim64.exe'):
            ts_exec_file='TurbSim.exe'
        else:
            raise Exception('TurbSim (original) is not present in the working directory.  Download the TurbSim program from:\n http://wind.nrel.gov/designcodes/preprocessors/turbsim/\n and copy one of the executables to this directory.')
    else:
        if os.path.isfile('TurbSim'):
            ts_exec_file='TurbSim'
        else:
            raise Exception('TurbSim (original) is not present in the working directory.  Download the TurbSim program from:\n http://wind.nrel.gov/designcodes/preprocessors/turbsim/\n and build an executable from source, then copy it to this directory.')

    # Now run TurbSim and HydroTurbSim on the input files specified above.
    for fnm in fnames:
        # Run HydroTurbSim:
        tsdat=pyts.run_out('./inp_files/'+fnm+'.inp')
        pyts.writeOut('./pyts/'+fnm+'.inp',tsdat) # Write out the data.
        # Run TurbSim:
        call(['./'+ts_exec_file,'./inp_files/'+fnm+'.inp'])
        dst='./ts/'+fnm+ts_file_type
        try:
            os.remove(dst) # This is for windows compatability.
        except:
            pass
        os.rename('./inp_files/'+fnm+ts_file_type,dst)

########################################
########################################
# Plot the results of the two versions #
########################################
if flag_plot:
    c=0
    for nm in fnames:
        c+=1
        tsdat=pyts.tsio.readModel('./ts/'+nm+ts_file_type,'./inp_files/'+nm+'.inp')
        tsdat.tm=pyts.buildModel(tsdat.config)
        tsdat=pyts.tsio.readModel('./pyts/'+nm+ts_file_type,'./inp_files/'+nm+'.inp')
        tsdat.tm=pyts.buildModel(tsdat.config)

        fg=pyts_plot.summfig(3000+c,nfft=1024,title=nm.upper()+' spectral model')
        fg.setinds(tsdat,igrid=None,)
        #fg.setinds(tsdat,igrid=(0,1),)
        fg.plot(tsdat,color='r',label='TSv1')
        fg.plot(tsdat,color='b',theory_line=True,label='TSv2')
        fg.finish()

