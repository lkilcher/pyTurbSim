import numpy as np
from pyts.io.formatter import SuperFormatter
import pkg_resources
import pyts._version as ver


class SumFormatter(SuperFormatter):

    format_prfx = '>10'

    def _format_f(self, value):
        return format(value, '10.3f')

    ## def _format_stringlist(self, value):

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
template.allow_sloppy = True


def write(filename, in_dict):
    """
    Write a config file.
    """

    outstr = template(**in_dict)

    with open(filename, 'w') as outfl:
        outfl.write(outstr)
    return outstr


if __name__ == '__main__':

    from pyts.base import statObj, tsGrid
    from pyts.io.config import read

    upwp = statObj(np.random.random(100))
    upwp.scale = 1e-4
    upwp.corr = 1e-4

    dout = {}
    dout.update(read('tmp/testfile.inp'))

    grid = tsGrid(90, 13, 13, 90, 110, nt=6000, dt=0.02)

    in_dict = dict(Latitude=45,
                   VerString=ver.VerString,
                   uhub=statObj(np.random.random(100)),
                   vhub=statObj(np.random.random(100)),
                   whub=statObj(np.random.random(100)),
                   upwp=upwp,
                   upvp=upwp,
                   vpwp=upwp,
                   hhub=upwp,
                   tke=upwp,
                   ctke=upwp,
                   u=upwp,
                   v=upwp,
                   w=upwp,
                   WindProfileType='LOG',
                   grid=grid,
                   )

    in_dict.update(dout)

    write('tmp/testfile.sum', in_dict)
