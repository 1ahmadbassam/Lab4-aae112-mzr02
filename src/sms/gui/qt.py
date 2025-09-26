"""
The main file for running the PyQT5-based GUI.

The file contains the function run_gui() which will launch the GUI through making a main instance
of the main window (SmsGUIQt)
"""
import sys
from PyQt5.QtWidgets import QApplication
from ._qt.qtroot import SmsGUIQt

def run_gui():
    """Initializes and run the PyQt5 application
    
    The function sets up the QApplication, creates an instance of the main window (SmsQUIQt),
    which will diplsay it on the user's screen.
    The script can exit cleanly when the event loop is terminated by closing the main window for example.
    
    """
    app = QApplication(sys.argv)
    window = SmsGUIQt()
    window.show()
    sys.exit(app.exec_())
