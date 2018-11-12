import TurbGen.api as tg

seed_init = 834383478
hub_ht = 100
grid = tg.RectGrid(center=hub_ht, ny=10, nz=10,
                   height=50, width=50, time_sec=600, dt=0.1)

def test_IECVKM():
    # Initialize the run
    tgrun = tg.TGrun(RandSeed=seed_init)
    tgrun.grid = grid

    # Set the statistics
    tgrun.prof = tg.profModels.pl(Uref=10, Zref=hub_ht)
    tgrun.spec = tg.specModels.iecvkm(IECwindtype='ntm', IECstandard=1, IECedition=3,
                                      IECturbc=0.1)
    tgrun.stress = tg.stressModels.uniform()
    tgrun.cohere = tg.cohereModels.iec()

    out = tgrun()
