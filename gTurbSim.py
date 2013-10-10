#!/usr/bin/python

import pyts.gui as gui
import sys

app = gui.gTurbApp(redirect=False)
if len(sys.argv)>1:
    app.setfile(sys.argv[1])
app.MainLoop()

