import nwtc,iec,vonKrmn,hydro,wf
model_alias={
    'ieckai':iec.ieckai,
    'iecvkm':iec.iecvkm,
    'smooth':nwtc.smooth,
    'nwtcup':nwtc.nwtcup,
    'wf_upw':wf.inf_turb,
    'wf_07d':wf.outf_turb,
    'wf_14d':wf.outf_turb,
    'gp_llj':wf.gp_llj,
    'usrvkm':vonKrmn.main,
    'tidal':hydro.tidal,
    'river':hydro.river,
    }

def getModel(config,profModel):
    # return an instance of the appropriate model class:
    if '.' in config['TurbModel']:
        return eval(config['TurbModel'].lower()+'(profModel)')
    else:
        return model_alias[config['TurbModel'].lower()](profModel)
