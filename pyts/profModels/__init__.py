import log,power
model_alias={'pl':power.main,
             'power.main':power.main,
             'log':log.main,
             'log.main':log.main,
             'h2l':log.H2O,
             'h2log':log.H2O,
             'log.H2O':log.H2O,
             'log.h2o':log.H2O,
             #'iec':iec.main
             }

def getModel(config,grid):
    if config['WindProfileType'] is None:
        config['WindProfileType']={'gp_llj':'jet','tidal':'h2l','river':'h2log'}.get(config['TurbModel'].lower(),'iec')
    # return an instance of the appropriate model class:
    return model_alias[config['WindProfileType'].lower()](config,grid)
    
    
