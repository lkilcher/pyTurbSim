"""
This is the PyTurbSim debug package. It contains debugging tools
specifically valuable to PyTurbSim.
"""

import time


class timer(object):

    """
    A timer class for tracking 'real' time (rather than CPU time).
    """

    def __init__(self, label='NONE'):
        self.tnew = 0.
        self.total = 0.
        self.label = label

    def start(self,):
        self.tnew = time.time()

    def reset(self,):
        self.total = 0.
        self.start()

    def stop(self,):
        self.total += time.time() - self.tnew

    def __repr__(self):
        return "So far the *%s* timer has clocked %0.3f seconds." % (self.label, self.total)
