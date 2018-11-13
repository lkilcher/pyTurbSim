import sys
sys.path.append('./compare_TS/')
import test_compare2ts as compare2ts
from os import mkdir

datdir = './data/'

for nm, val in compare2ts.__dict__.items():
    if callable(val) and nm.startswith('test'):
        try:
            val(make_data=True, figdir=datdir)
        except TypeError:
            pass
