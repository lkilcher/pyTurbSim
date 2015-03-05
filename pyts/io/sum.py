import numpy as np
from pyts.io.formatter import SuperFormatter
import pkg_resources
import pyts._version as ver
from .base import convname


class SumFormatter(SuperFormatter):

    default_format_prfx = '>10'

    def _format_f(self, value):
        return format(value, '10.3f')

    def _format_b(self, value):
        return format('FT'[value], '>10s')

    def _format_ScaleIECtxt(self, value):
        return format({0: 'None',
                       1: 'HUB',
                       2: 'ALL'}[value], '>5s')

    def _format_TurbModelstr(self, value):
        return format(value, '>10s')

    def _format_WindProfilestr(self, value):
        return format(value, '>10s')

    def _format_stringlist(self, value):
        out = ''
        for v in value:
            out += v + '\n'
        return out

    def _format_grid(self, value, form):
        out = ''
        if isinstance(value, (np.ndarray)) and value.ndim > 1:
            for v in value:
                out += self._format_grid(v, form) + '\n'
            return out

        n = len(value)
        form = form.split(',')
        # Extrapolate the last value to the last n points:
        form = form + [form[-1]] * (n - len(form))

        for v, f in zip(value, form):
            out += format(v, f)

        return out

    def _format_tup(self, value):
        return '( %8.3f, %8.3f )' % tuple(value)


# This is the input-file template object:
template = SumFormatter(
    pkg_resources.resource_string(ver.pkg_name,
                                  'io/templates/sum'))


def write(filename, in_dict):
    """
    Write a sum file.
    """

    with open(convname(filename, '.sum'), 'w') as outfl:
        outfl.write(template(**in_dict))


if __name__ == '__main__':

    from .input import read as readInput
    from ..runInput import run

    inp = readInput('tmp/TurbSim.inp')
    tsdat = run(inp)
    write('tmp/TurbSim.sum', tsdat._sumdict)

    tsdat.writeSum('tmp/TurbSim_alt.sum')
