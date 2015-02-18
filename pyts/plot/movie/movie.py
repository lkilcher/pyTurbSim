import sys
if '../' not in sys.path:
    sys.path.append('../')
import pyts
from pyts_plot import supax
import subprocess
import os

tsread = pyts.tsio

###################################################
# A script for creating movies of TurbSim output.
# The script has 3 steps:
#   1) Load the data,
#   2) Use matplotlib to create a sequence of images,
#   3) Use mencoder*** to create the movie from the images.
#
# ***: If you are on a system that does not have mencoder (e.g. Windows or Mac,
#      you will need to use a different program to build a movie from the
#      image sequence.
#
# Note that the file movie.inp

dat_file_name = 'movie'  # This should match the 

###########################
########## STEP 1 #########
###### Load the data ######
if 'tsdat' not in vars():
    try:
        tsdat = tsread.readModel('./%s.inp' % dat_file_name)
    except IOError:
        print 'Warning: running TurbSim to create data.  It may save time to create the TurbSim output separately (run `pyts.run(%s.inp)`), and then run this movie script.' % dat_file_name
        tsdat = pyts.run_out('./%s.inp' % dat_file_name)


tmpdir = './tmp/'  # This is the temporary directory where figures will be saved.

try:
    os.mkdir(tmpdir)
except OSError:
    pass

rot_rad = 4.5  # Radius of the rotor (meters).  Note that this is consistent with the domain size of the movie.inp file (10m width and height).
ycirc = np.arange(-rot_rad, rot_rad+.1, .01)

# Some scaling constants
circ_scale = 400 # For the u-component 'velocity dots'
quiv_scale = 3 # for the v,w component 'arrows'

###########################
########## STEP 2 #########
### Create image files ####

# Setup the figure:
fg2 = supax.figobj(309, (1, [.5, 1]), axsize=[4, 4], frame=[0.7, 0.4, .7, .4], sharey=True, sharex=False)
axp = fg2.ax[0]
ax = fg2.ax[1]
#cpc=fg2.ax[0].pcolormesh(tsdat.y,tsdat.z,tsdat.uturb[0,:,:,0],clim=[-.03,.03])
y, z = np.meshgrid(tsdat.y, tsdat.z)
y, z = y.flatten(), z.flatten()
zintrp = np.arange(.1, 12, .1)

# Loop over each timestep of the output and create the images...
for ind in range(tsdat.shape[-1]):
    ax.cla()
    axp.cla()
    ax.set_xlabel('y [m]')
    axp.set_ylabel('z [m]')
    ax.fill(ycirc, tsdat.grid.zhub+np.sqrt(rot_rad**2-ycirc**2),
            '-', fc=[.8, .95, .8, 1], ec='none', zorder=-10)
    ax.fill(ycirc, tsdat.grid.zhub-np.sqrt(rot_rad**2-ycirc**2),
            '-', fc=[.8, .95, .8, 1], ec='none', zorder=-10)
    # cpc=ax.contourf(tsdat.y,tsdat.z,tsdat.uturb[0,:,:,ind],100,clim=[-.03,.03],alpha=1)
    dt = tsdat.uturb[:,:,:, ind].reshape((3, -1))
    ipo = dt[0] >= 0
    ing = np.logical_not(ipo)
    ax.scatter(y[ipo], z[ipo], dt[0, ipo] * circ_scale, c='b', edgecolor='b')
    ax.scatter(y[ing], z[ing], -dt[0, ing] * circ_scale, c='r', edgecolor='r')
    ax.quiver(y[ipo], z[ipo], dt[0, ipo]*quiv_scale, dt[2, ipo]*quiv_scale, angles='xy',
              scale_units='xy', scale=1, headwidth=0.01, color='b', width=0.004, headlength=1, headaxislength=1)
    ax.quiver(y[ing], z[ing], dt[1, ing]*quiv_scale, dt[2, ing]*quiv_scale, angles='xy',
              scale_units='xy', scale=1, headwidth=0.0001, color='r', width=.004, headlength=1, headaxislength=1)
    show()
    ax.set_ylim([1, 11])
    ax.set_xlim([-5, 5])
    #ax.plot([0,0],[0,20],'k--',linewidth=2)
    ax.plot([0], [1.02], 'v', markersize=9, clip_on=False,
            transform=ax.transDataXAxesY, mec='k', mfc='k')
    axp.set_xticks(np.arange(0, 6, 1))
    axp.set_xlim([0, 3])
    fg2.hide('yticklabels', axp)
    pudat = tsdat.uprof[0,:, tsdat.ihub[1]]
    pudati = np.interp(zintrp, tsdat.z[::-1], pudat[::-1])
    axp.plot(pudat, tsdat.z, 'k-', linewidth=2)
    dtp = np.interp(zintrp, tsdat.z[::-1], dt[0].reshape(15, 15)[:, 7][::-1])
    stddev = tsdat.uturb[0,:, 7,:].std(-1)
    axp.fill_betweenx(tsdat.z, pudat-stddev, pudat + \
                      stddev, facecolor='0.7', edgecolor='none', zorder=-8)
    axp.fill_betweenx(zintrp, pudati, pudati+dtp, where=dtp > 0, facecolor='b', edgecolor='none')
    axp.fill_betweenx(zintrp, pudati, pudati+dtp, where=dtp < 0, facecolor='r', edgecolor='none')
    axp.fill_between([0, 4], tsdat.grid.zhub+rot_rad*np.ones(2), tsdat.grid.zhub - \
                     rot_rad*np.ones(2), facecolor=[.8, .95, .8, .9], edgecolor='none', zorder=-10)
    axp.set_xlabel('u [m/s]')
    fname = tmpdir+'_%sFile%05d.png' % (dat_file_name, ind)
    #print fname
    #break
    fg2.savefig(fname)


###########################
########## STEP 3 #########
#### Create movie file ####

thisdir = os.getcwd()
os.chdir(tmpdir)
command2 = ('mencoder',
          'mf://_mov2File*.png',
          '-mf',
          'type=png:w=742:h=522:fps=20',
              # Note that the fps (20) here matches the timestep in the movie.inp file (0.05s). This makes the movie be in realtime.
          '-ovc',
         'lavc',
          '-lavcopts',
          'vcodec=msmpeg4v2:vhq:vbitrate=2400',
          '-o',
          '%s/%s.avi' % (thisdir, dat_file_name,),
          )
subprocess.check_call(command2)
os.chdir(thisdir)
