"""
The main entry point for the School Management System application.

This script reads the configuration settings and launches the appropriate
Graphical User Interface (GUI), either PyQt5 or Tkinter, based on the
`QT_GUI` flag in the config file.
"""
from config import QT_GUI

if QT_GUI:
    import sms.gui.qt as gui
else:
    import sms.gui.tk as gui

#gui.run_gui()
