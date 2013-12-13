import nwtc,iec,hydro
model_alias={
    'ieckai':iec.cfg_ieckai,
    'iecvkm':iec.cfg_iecvkm,
    'smooth':nwtc.cfg_smooth,
    'nwtcup':nwtc.cfg_nwtcup,
#    'wf_upw':wf.inf_turb,
#    'wf_07d':wf.outf_turb,
#    'wf_14d':wf.outf_turb,
#    'gp_llj':wf.gp_llj,
#    'usrvkm':vonKrmn.main,
    'tidal':hydro.cfg_tidal,
    'river':hydro.cfg_river,
    }

def getModel(config,profModel):
    # return an instance of the appropriate model class:
    if '.' in config['TurbModel']:
        return eval(config['TurbModel'].lower()+'(config,profModel)')
    else:
        return model_alias[config['TurbModel'].lower()](config,profModel)
