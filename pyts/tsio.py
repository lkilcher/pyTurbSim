import numpy as np
from struct import pack,unpack
from os import listdir,path
from base import tscfg,prog,ts_float,tsdata
import time

e='<'

def convname(fname,sfx=''):
    """
    Change the suffix from '.inp', if necessary.
    """
    if sfx in ['.inp','inp']:
        return fname.rsplit('.',1)[0]+'.inp'
    if fname.endswith('inp'):
        if not sfx.startswith('.'):
            sfx='.'+sfx
        return fname.rsplit('.',1)[0]+sfx
    return fname

def _readInputLine(line):
    types=[np.int32,np.float32,bool,str]
    val=line.split()[0]
    idx=0
    while True:
        try:
            if types[idx] is bool:
                if not (val=='False' or val=='True'):
                    raise ValueError
                else:
                    if val=='False':
                        return False
                    else:
                        return True
            out=types[idx](val)
            if types[idx] is str and out.startswith('"') and out.endswith('"'):
                out=out[1:-1]
            return out
        except ValueError:
            idx+=1

def readInPSD(fname):
    """
    Read the input spectrum from file *fname*, and return it as a dictionary.

    The frequency in the input file should be in units of hz, and the spectrum should be in units of m^2/s^2/hz.
    """
    ril=_readInputLine
    out={}
    if fname.__class__ is file:
        dat=fname.readlines()
    else:
        with open(fname) as fl:
            dat=fl.readlines()
    NumUSRf=ril(dat[3])
    SpecScale1=ril(dat[4])
    SpecScale2=ril(dat[5])
    SpecScale3=ril(dat[6])
    out['freq']=np.empty(NumUSRf,dtype=ts_float)
    out['Suu']=np.empty(NumUSRf,dtype=ts_float)
    out['Svv']=np.empty(NumUSRf,dtype=ts_float)
    out['Sww']=np.empty(NumUSRf,dtype=ts_float)
    for ind in range(out.NumUSRf):
        tmp=dat[ind+11].split()
        out['freq'][ind]=tmp[0]
        out['Suu'][ind]=tmp[1]
        out['Svv'][ind]=tmp[2]
        out['Sww'][ind]=tmp[3]
    out['Suu']*=SpecScale1
    out['Svv']*=SpecScale2
    out['Sww']*=SpecScale3
    return out

def readConfig(fname):
    """
    Read a TurbSim input (.inp) file.
    
    Returns a dictionary of TurbSim config options.
    """
    # TurbSim input files are static:
    #   Variable are determined by line number.
    #   Only the first string on the line matters.
    #   All else is commenting.
    #   Therefore we simply assign variables by line number.
    ril=_readInputLine
    out=tscfg()
    out['UserProfile']=False
    with open(fname) as fl:
        dat=fl.readlines()
    out['header']=dat[0] # Header line at top of file.  Sometimes used to indicate the files specific use.
    tmp0=ril(dat[3])
    tmp1=ril(dat[4])
    # This block just handles the random numbers...
    if tmp0.__class__ is str and tmp1.__class__ is str:
        out['RandSeed']=None
    elif tmp0.__class__ is not str and tmp1.__class__ is not str:
        out['RandSeed']=np.uint(np.abs(tmp0+tmp1))
    elif tmp1.__class__ is str:
        if tmp0<0:
            tmp0+=np.uint(2**31)
        out['RandSeed']=np.uint(tmp0)
    else:
        if tmp1<0:
            tmp1+=2**31
        out['RandSeed']=np.uint(tmp1)
        
    out['writeout_BHHTP']=ril(dat[5])
    out['writeout_FHHTP']=ril(dat[6])
    out['writeout_ADHH']=ril(dat[7])
    out['writeout_ADFF']=ril(dat[8])
    out['writeout_BLFF']=ril(dat[9])
    out['writeout_ADTWR']=ril(dat[10])
    out['writeout_MFTFF']=ril(dat[11])
    out['writeout_ACT']=ril(dat[12])
    out['clockwise']=ril(dat[13])
    out['ScaleIEC']=ril(dat[14])
    out['NumGrid_Z']=ril(dat[17])
    out['NumGrid_Y']=ril(dat[18])
    out['TimeStep']=ril(dat[19])
    out['AnalysisTime']=ril(dat[20])
    out['UsableTime']=ril(dat[21])
    out['HubHt']=ril(dat[22])
    out['GridHeight']=ril(dat[23])
    out['GridWidth']=ril(dat[24])
    out['VFlowAng']=ril(dat[25])
    out['HFlowAng']=ril(dat[26])
    out['TurbModel']=ril(dat[29])
    out['IECstandard']=ril(dat[30])
    out['IECturbc']=ril(dat[31])
    out['IEC_WindType']=ril(dat[32])
    out['ETMc']=ril(dat[33])
    out['WindProfileType']=ril(dat[34])
    out['RefHt']=ril(dat[35])
    out['URef']=ril(dat[36])
    out['ZJetMax']=ril(dat[37])
    out['PLExp']=ril(dat[38])
    out['Z0']=ril(dat[39])
    out['Latitude']=ril(dat[42])
    out['RICH_NO']=ril(dat[43])
    out['UStar']=ril(dat[44])
    out['ZI']=ril(dat[45])
    out['PC_UW']=ril(dat[46])
    out['PC_UV']=ril(dat[47])
    out['PC_VW']=ril(dat[48])
    if not dat[49].startswith('default'):
        out['IncDec1']=np.array(dat[49].split('"')[1].split(),dtype=ts_float)
    else:
        out['IncDec1']=None
    if not dat[50].startswith('default'):
        out['IncDec2']=np.array(dat[50].split('"')[1].split(),dtype=ts_float)
    else:
        out['IncDec2']=None
    if not dat[51].startswith('default'):
        out['IncDec3']=np.array(dat[51].split('"')[1].split(),dtype=ts_float)
    else:
        out['IncDec3']=None
    out['CohExp']=ril(dat[52])
    out['CTEventPath']=ril(dat[55])
    out['CTEventFile']=ril(dat[56])
    out['Randomize']=ril(dat[57])
    out['DistScl']=ril(dat[58])
    out['CTLy']=ril(dat[59])
    out['CTLz']=ril(dat[60])
    out['CTStartTime']=ril(dat[61])
    if len(dat)>=70 and dat[64].split()[1]=='NumUSRz':
        # This has a user-defined profile.
        out['NumUSRz']=ril(dat[64])
        out['StdScale']=np.empty((3),dtype=ts_float)
        out['StdScale'][0]=ril(dat[65])
        out['StdScale'][1]=ril(dat[66])
        out['StdScale'][2]=ril(dat[67])
        out['UserProf_H']=np.empty(out['NumUSRz'],dtype='float32')
        out['UserProf_U']=np.empty_like(out['UserProf_H'])
        out['UserProf_Ang']=np.empty_like(out['UserProf_H'])
        out['UserProf_Std']=np.empty_like(out['UserProf_H'])
        out['UserProf_L']=np.empty_like(out['UserProf_H'])
        for i in range(out['NumUSRz']):
            tmp=dat[72+i].split()
            out['UserProf_H'][i]=ts_float(tmp[0])
            out['UserProf_U'][i]=ts_float(tmp[1])
            out['UserProf_Ang'][i]=ts_float(tmp[2])
            out['UserProf_Std'][i]=ts_float(tmp[3])
            out['UserProf_L'][i]=ts_float(tmp[4])
        out['UserProfile']=True
        fls=listdir(fname.rpartition('/')[0])
        for fl in [fname.rpartition('/')[2].rpartition('.')[0]+'_Spec.inp','UsrSpec.inp',]:
            if fl in fls:
                break
        out['psd']=readInPSD(fname.rpartition('/')[0]+'/'+fl)
    for ky,val in out.iteritems():
        if val=='default':
            out[ky]=None
    return out

def writeBladed(fname,tsdat):
    """
    Write the data to a Bladed-format binary file.

    This code was copied from the original TSsubs.f90.
    """
    stats=tsdat.stats
    tsconfig=tsdat.config
    ts=tsdat.utotal
    ti=stats['Ti'].copy()
    ti[ti<1e-5]=1
    scale=1000./(tsdat.UHUB*ti[:,None,None,None])
    off=np.array([1000./(ti[0]),0,0])[:,None,None,None]
    if fname.endswith('.inp'):
        fname=convname(fname,'.wnd')
    fl=file(fname,'wb')
    # First write some setup data:
    fl.write(pack(e+'2hl3f',-99,4,3,tsconfig['Latitude'],tsconfig['Z0'],tsdat.grid.z[0]+tsdat.grid.height/2.0))
    # Now write the turbulence intensity, grid spacing, numsteps, and hub mean wind speed
    # For some reason this takes half the number of timesteps...
    fl.write(pack(e+'3f',*(100*ti)))
    fl.write(pack(e+'3flf',tsdat.grid.dz,tsdat.grid.dy,tsdat.UHUB*tsdat.dt,tsdat.shape[-1]/2,tsdat.UHUB))
    fl.write(pack(e+'3fl',*([0]*4))) # Unused bytes
    fl.write(pack(e+'3l',tsconfig['RandSeed'],tsdat.grid.n_z,tsdat.grid.n_y))
    fl.write(pack(e+'6l',*([0]*6))) # Unused bytes
    if tsconfig['clockwise']:
        out=(ts[:,::-1,::-1,:]*scale-off).astype(np.int16)
    else:
        out=(ts[:,::-1]*scale-off).astype(np.int16)
    # Swap the y and z indices so that fortran-order writing agrees with the file format.
    out=np.rollaxis(out,2,1)
    # Write the data so that the first index varies fastest (F order).
    # With the swap of y and z indices above, the indexes vary in the following
    # (decreasing) order:
    # component (fastest), y-index, z-index, time (slowest).
    fl.write(out.tostring(order='F'))
    fl.close()

def readBladed(fname,):
    """
    Read Bladed format (.wnd, .bl) full-field time-series binary data files.
    """
    with file(fname,'rb') as fl:
        junk,nffc,ncomp,lat,z0,zoff=unpack(e+'2hl3f',fl.read(20))
        if junk!=-99 or nffc!=4:
            error
        ti=np.array(unpack(e+'3f',fl.read(12)))/100
        dz,dy,dx,n_f,uhub=unpack(e+'3flf',fl.read(20))
        n_t=int(2*n_f)
        fl.seek(16,1) # Unused bytes
        randseed,n_z,n_y=unpack(e+'3l',fl.read(12))
        fl.seek(24,1) # Unused bytes
        nbt=ncomp*n_y*n_z*n_t
        dat=np.rollaxis(np.fromstring(fl.read(2*nbt),dtype=np.int16).astype(np.float32).reshape([ncomp,n_y,n_z,n_t],order='F'),2,1)[:,::-1]
    dat[0]+=1000.0/ti[0]
    dat/=1000./(uhub*ti[:,None,None,None])
    return dat

def writeAero(fname,tsdat):
    """
    Write the data to a AeroDyn-/TurbSim-format binary file.

    This code was translated from the original TSsubs.f90 file.
    """
    ts=tsdat.utotal
    intmin=-32768
    intrng=65536
    u_minmax=np.empty((3,2),dtype=ts_float)
    u_off=np.empty((3),dtype=ts_float)
    u_scl=np.empty((3),dtype=ts_float)
    desc_str='generated by %s v%s, %s.' % (prog['name'],prog['ver'],time.strftime('%b %d, %Y, %H:%M (%Z)',time.localtime()))
    # Calculate the ranges:
    out=np.empty(tsdat.shape,dtype=np.int16)
    for ind in range(3):
        u_minmax[ind]=ts[ind].min(),ts[ind].max()
        if u_minmax[ind][0]==u_minmax[ind][1]:
            u_scl[ind]=1
        else:
            u_scl[ind]=intrng/np.diff(u_minmax[ind])
        u_off[ind]=intmin-u_scl[ind]*u_minmax[ind,0]
        out[ind]=(ts[ind]*u_scl[ind]+u_off[ind]).astype(np.int16)
    fl=file(convname(fname,'.bts'),'wb')
    fl.write(pack(e+'h4l12fl',7,tsdat.grid.n_z,tsdat.grid.n_y,tsdat.grid.n_tower,tsdat.shape[-1],tsdat.grid.dz,tsdat.grid.dy,tsdat.dt,tsdat.UHUB,tsdat.grid.zhub,tsdat.grid.z[0],u_scl[0],u_off[0],u_scl[1],u_off[1],u_scl[2],u_off[2],len(desc_str)))
    fl.write(desc_str)
    # Swap the y and z indices so that fortran-order writing agrees with the file format.
    # Also, we swap the order of z-axis to agree with the file format.
    # Write the data so that the first index varies fastest (F order).
    # The indexes vary in the following order:
    # component (fastest), y-index, z-index, time (slowest).
    fl.write(np.rollaxis(out[:,::-1],2,1).tostring(order='F'))
    fl.close()


def readAero(fname):
    """
    Read AeroDyn/TurbSim format (.bts) full-field time-series binary data files.
    """
    u_scl=np.zeros(3,ts_float)
    u_off=np.zeros(3,ts_float)
    fl=file(convname(fname,'.bts'),'rb')
    junk,n_z,n_y,n_tower,n_t,dz,dy,dt,uhub,zhub,z0,u_scl[0],u_off[0],u_scl[1],u_off[1],u_scl[2],u_off[2],strlen=unpack(e+'h4l12fl',fl.read(70))
    print fname,u_scl,u_off
    desc_str=fl.read(strlen)
    nbt=3*n_y*n_z*n_t
    out=np.rollaxis(np.fromstring(fl.read(2*nbt),dtype=np.int16).astype(ts_float).reshape([3,n_y,n_z,n_t],order='F'),2,1)[:,::-1]
    out-=u_off[:,None,None,None]
    out/=u_scl[:,None,None,None]
    return out

    
def writeOut(fname,tsdat):
    """
    Write out the requested summary and binary files.
    """
    if tsdat.config['writeout_BLFF']:
        writeBladed(fname,tsdat)
    if tsdat.config['writeout_ADFF']:
        writeAero(fname,tsdat)


readers={'wnd':readBladed,
         'bl':readBladed,
         'bts':readAero,}

def readModel(fname,inp_fname=None):
    """
    Reads a TurbSim data and input (config) file and returns a tsdata object.
    If *fname* ends in .inp, it reads this input file, and searches for a binary file
    that can be read (throws error if none is found).
    
    If *fname* is a filetype that can be read, it reads that file and the associated .inp file.

    In other words:
      tsdat=readModel('TurbSim.inp')
        and
      tsdat=readModel('TurbSim.bts')
    Do essentially the same thing.
    
    """
    if fname.endswith('.inp'):
        config=readConfig(fname)
        for sfx,rdr in readers.iteritems():
            fnm=convname(fname,sfx)
            if path.isfile(fnm):
                utmp=rdr(fnm)
                break
    else:
        if inp_fname is None:
            config=readConfig(convname(fname,'inp'))
        else:
            config=readConfig(inp_fname)
        sfx=fname.split('.')[-1]
        if readers.has_key(sfx):
            rdr=readers[sfx]
            utmp=rdr(fname)
        else:
            raise Exception('No reader for this file type.')
    umn=utmp.mean(-1)
    utmp-=umn[:,:,:,None]
    out=tsdata(config,utmp,umn)
    return out
