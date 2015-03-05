import sys
import os
if '../' not in sys.path:
    sys.path = ['../'] + sys.path
from pyts.runInput import main as pyts
#import pyts
import pyts.plot.api as pt
import pyts.io.main as tsio
from subprocess import call

## This is the file type that the .inp files (in inp_files directory) are configured to output.
## It can be changed, but if it is the input files should be configured to
## output different files also.
ts_file_type = '.wnd'

## Run TurbSim and PyTurbSim?
## Comment or uncomment these lines to run the corresponding code block (below)
flag = dict(
    #run_ts=True,
    run_pyts=True,
    plot=True,
)

########################################################################################
## These are the name of the input files (in ./inp_files/) that are run and
## compared.
## Comment+uncomment+add as desired.
fnames = ['Tidal', 'Smooth', 'IecKai', 'IecVkm',
          'GPllj', 'NWTCup', 'wfup', 'wf07d', 'wf14d', ]
#fnames=['Smooth','IecKai','IecVkm','GPllj','NWTCup','wfup','wf07d','wf14d',]
fnames = ['IecVkm']  # CHECKED 4/26/2013
fnames = ['IecVkm_short']  # CHECKED 4/26/2013
fnames = ['Kaimal']  # CHECKED 2/25/2015
#fnames=['IecKai'] #CHECKED 4/26/2013
#fnames=['IecKai_short'] #CHECKED 4/26/2013
#fnames=['Smooth'] #CHECKED 4/26/2013
#fnames=['Tidal'] #CHECKED 4/26/2013
#fnames=['GPllj']
#fnames=['River'] #CHECKED 4/26/2013
#fnames=['NWTCup'] #CHECKED 4/26/2013

# Make sure the output directories exist:
try:
    os.mkdir('./ts/')
except:
    pass
try:
    os.mkdir('./pyts/')
except:
    pass
error = Exception('TurbSim (original) is not present in the working directory.'
                  'Download the TurbSim program from:\n'
                  '   http://wind.nrel.gov/designcodes/preprocessors/turbsim/\n'
                  'and copy one of the executables to this directory.')

##############################
## Run the turbsim programs ##
##############################
if flag.get('run_ts', False):
    ## Check to see that a TurbSim executable exists:
    if sys.platform.startswith('win'):
        if os.path.isfile('TurbSim.exe'):
            ts_exec_file = 'TurbSim.exe'
        elif os.path.isfile('TurbSim64.exe'):
            ts_exec_file = 'TurbSim.exe'
        else:
            raise error
    else:
        if os.path.isfile('TurbSim'):
            ts_exec_file = 'TurbSim'
        else:
            raise error
## Now run TurbSim and PyTurbSim on the input files specified above.
for fnm in fnames:
    ## Run PyTurbSim:
    if flag.get('run_pyts', False):
        tsdat = pyts.run(pyts.readInput('./inp_files/' + fnm + '.inp'))
        #error
        tsdat.write_bladed('./pyts/' + fnm + '.inp')  # Write out the data.
    if flag.get('run_ts', False):
        ## Run TurbSim:
        call(['./' + ts_exec_file, './inp_files/' + fnm + '.inp'])
        dst = './ts/' + fnm + ts_file_type
        try:
            os.remove(dst)  # This is for windows compatability.
        except:
            pass
        os.rename('./inp_files/' + fnm + ts_file_type, dst)

#################################################################
## Plot the results of the two versions and compare to 'theory' #
#################################################################
if flag.get('plot', False):
    for c, nm in enumerate(fnames):

        ## Load the data from the files:
        tsdat = tsio.readModel('./ts/' + nm + ts_file_type)
        ptsdat = tsio.readModel('./pyts/' + nm + ts_file_type)

        ## Create a TurbSim 'run' object based on the input file.
        ## First load the data from the input file into a 'tscfg' object:
        tscfg = pyts.readInput('./inp_files/' + nm + '.inp')
        # Now create a 'tsrun' object.
        tsr = pyts.cfg2tsrun(tscfg)
        ## If you want to, you can 'run' this by uncommenting:
        #ptsdat2 = tsr()
        ## This should be identical to `ptsdat`.

        ## This creates a 'figure object'
        fg = pt.FigAxForm(3000 + c,  # fignum
                          nfft=1024,  # specify the nfft for spectral plots.
                          ## Here you can specify which variables to compare:
                          ## (see options in the pt.axform module)
                          axforms=[pt.axform.velprof(),
                                   # Specify some axes parameters here:
                                   pt.axform.tkeprof(xlim=[0, 10]),
                                   pt.axform.spec(ylim=[1e-4, 1e4]),
                                   ],
                          # Retitle the figure:
                          title=nm.upper().replace('_', '-') + ' spectral model',
                          # This specifies the border space around
                          # the axes [bot, top, left, right] (in
                          # inches). Note that I've made space for the
                          # legend on the right:
                          frame=[.7, .5, 1.1, 1.5],
                          )
        ## Now comes the true power of these 'axforms':
        ## We can simply plot tsdat objects in one line:
        fg.plot(tsdat, color='r', label='TS')
        ## After supplying the data object these plot calls can take
        ## all of the arguments as defined in matplotlib.pyplot.plot
        fg.plot(ptsdat, color='b', linestyle='-', marker='.', label='pyTS')
        ## When calling fg.plot on a tsrun object, these axform
        ## objects plot the theoretical line:
        fg.plot(tsr, color='g', label='Target')
        ## Add a legend to the upper-right axes:
        ## (Note here that indexing the 'figure object' gives axes in
        ## the grid)
        fg[0, -1].legend(loc='upper left',
                         bbox_to_anchor=(1.02, 1),
                         prop=dict(size='medium'),
                         )
        # This does some 'tidying up' of the figure:
        fg.finalize()
        # You can save the figure:
        #fg.savefig('<path-to-somewhere>/compareTSvPyTS.png', dpi=300)
