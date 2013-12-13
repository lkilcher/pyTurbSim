import log,power
model_alias={'pl':power.cfg_nwtc,
             'power':power.cfg_nwtc,
             'power.main':power.cfg_nwtc,
             'log':log.cfg_nwtc,
             'log.main':log.cfg_nwtc,
             'h2l':log.cfg_H2O,
             'h2log':log.cfg_H2O,
             'log.H2O':log.cfg_H2O,
             'log.h2o':log.cfg_H2O,
             #'iec':iec.main
             }

def getModel(config,grid):
    if config['WindProfileType'] is None:
        config['WindProfileType']={'gp_llj':'jet','tidal':'h2l','river':'h2log'}.get(config['TurbModel'].lower(),'iec')
    # return an instance of the appropriate model class:
    return model_alias[config['WindProfileType'].lower()](config,grid)
    
    
