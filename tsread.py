import numpy as np
from struct import pack,unpack
ts_float=np.float32


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
