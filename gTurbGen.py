#!/usr/bin/python

import TurbGen.gui as gui
import sys

app = gui.gTurbApp(redirect=False)
if len(sys.argv)>1:
    app.setfile(sys.argv[1])
app.MainLoop()

