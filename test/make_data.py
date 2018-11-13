import sys
sys.path.append('./compare_TS/')
import test_compare2ts as compare2ts
from os import mkdir

figdir = './test_output_figs/'

try:
    mkdir(figdir)
except:
    pass

for nm, val in compare2ts.__dict__.items():
    if callable(val) and nm.startswith('test'):
        try:
            val(figdir=figdir)
        except TypeError:
            pass
