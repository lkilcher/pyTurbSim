"""
This module is for reading/writing PyTurbSim config (.inp) files.
"""
from os import listdir
from ..runConfig.base import tscfg
from copy import deepcopy
import numpy as np
from ..base import ts_float,userroot,tsroot

# Inpute files are in fixed format. That is, variables are defined by linenumber.
# This defines the input-file format:
inputfile_form={
    3:'RandSeed1',
    4:'RandSeed2',
    5:'WrBHHTP',
    6:'WrFHHTP',
    7:'WrADHH',
    8:'WrADFF',
    9:'WrBLFF',
    10:'WrADTWR',
    11:'WrFMTFF',
    12:'WrACT',
    13:'Clockwise',
    14:'ScaleIEC',
    17:'NumGrid_Z',
    18:'NumGrid_Y',
    19:'TimeStep',
    20:'AnalysisTime',
    21:'UsableTime',
    22:'HubHt',
    23:'GridHeight',
    24:'GridWidth',
    25:'VFlowAng',
    26:'HFlowAng',
    29:'TurbModel',
    30:'IECstandard',
    31:'IECturbc',
    32:'IEC_WindType',
    33:'ETMc',
    34:'WindProfileType',
    35:'RefHt',
    36:'URef',
    37:'ZJetMax',
    38:'PLExp',
    39:'Z0',
    42:'Latitude',
    43:'RICH_NO',
    44:'UStar',
    45:'ZI',
    46:'PC_UW',
    47:'PC_UV',
    48:'PC_VW',
    49:'IncDec1',
    50:'IncDec2',
    51:'IncDec3',
    52:'CohExp',
    55:'CTEventPath',
    56:'CTEventFile',
    57:'Randomize',
    58:'DistScl',
    59:'CTLy',
    60:'CTLz',
    61:'CTStartTime',
    64:'NumUSRz',
    65:'StdScale1',
    66:'StdScale2',
    67:'StdScale3',
    }

def write(fname,config,headertext=None):
    """
    Writeout a config file.

    Parameters
    ----------
    *fname*   - The filename to write out.
    *config*  - The PyTurbSim config dictionary.
    
    """
    format=open(tsroot+'form/input.form','r')
    out=open(fname,'w')
    for idx,ln in enumerate(format):
        if idx==0 and headertext is not None:
            ln+=headertext
        if inputfile_form.has_key(idx):
            val=config[inputfile_form[idx]]
            if inputfile_form[idx]=='RandSeed2' and val is None:
                val='RANLUX'
            elif val.__class__ is str:
                val='"'+val+'"'
            elif val is None:
                val='default'
            elif val.__class__ is np.ndarray:
                val=('"'+'%0.2g '*(len(val)-1)+'%0.2g"') % tuple(val)
            s=str(val)
            s+=' '*(25-len(s))
            ln=s+ln
        out.write(ln)
    out.close()
    
def read(fname):
    """
    Read a TurbSim input (.inp) file.
    

    Parameters
    ----------
    *fname*   - The filename to read the config from.

    Returns
    -------
    *config*  - A PyTurbSim config dictionary.

    """
    # TurbSim input files are static:
    #   Variable are determined by line number.
    #   Only the first string on the line matters.
    #   All else is commenting.
    #   Therefore we simply assign variables by line number.
    ril=_readInputLine
    out=tscfg()
    out.filename=fname
    out['UserProfile']=False
    with open(fname) as fl:
        dat=fl.readlines()
    fl.close()
    out['header']=dat[0] # Header line at top of file.  Sometimes used to indicate the files specific use.
    # Deal the data from the file:
    for idx,ln in enumerate(dat):
        if inputfile_form.has_key(idx):
            out[inputfile_form[idx]]=ril(dat[idx])
    # Customize the input fields for pyTurbSim...
    if out['RandSeed2'].__class__ is str and out['RandSeed2'].upper()=='RANLUX':
        out['RandSeed2']=None
    for nm in ['IncDec1','IncDec2','IncDec3']:
        if out[nm] is not None:
            out[nm]=np.array(out[nm].split(),dtype=ts_float)
    if len(dat)>=70 and dat[64].split()[1]=='NumUSRz':
        # This file has a user-defined profile.
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
    out.__original__=deepcopy(out)
    return out



def _readInputLine(line):
    """
    This function parses data from config file lines and returns it as the 
    correct 'type' (e.g. int, float, bool, str).
    """
    types=[np.int32,np.float32,bool,str]
    if line[0]=='"':
        val=line.split('"')[1]
    elif line[0]=="'":
        val=line.split("'")[1]
    else:
        val=line.split()[0]
    idx=0
    if val=='default':
        return None
    while True:
        try:
            if types[idx] is bool:
                tmp=val.lower().replace('"','').replace("'","")
                if not (tmp=='false' or tmp=='true'):
                    raise ValueError
                else:
                    return tmp=='true'
            out=types[idx](val)
            if types[idx] is str and out.startswith('"') and out.endswith('"'):
                out=out[1:-1]
            return out
        except ValueError:
            idx+=1

def readInPSD(fname):
    """
    Read the input spectrum from file *fname*, and return it as a
    dictionary.

    Parameters
    ----------
    *fname*   - The filename to read the PSD from.

    The frequency in the input file should be in units of hz, and the
    spectrum should be in units of m^2/s^2/hz.
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
    out['freq']=np.empty(NumUSRf,**ts_float)
    out['Suu']=np.empty(NumUSRf,**ts_float)
    out['Svv']=np.empty(NumUSRf,**ts_float)
    out['Sww']=np.empty(NumUSRf,**ts_float)
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
