"""
Main entry point for launching the Tkinter-based GUI.

This module contains the `run_gui` function, which initializes and runs
the main application window. It attempts to apply a theme using the
`ttkthemes` library if it is available.
"""
import logging
import tkinter as tk

from ._tk.tkroot import SmsGUITk

logger = logging.getLogger(__file__)

try:
    from ttkthemes import ThemedTk
except ImportError:
    ThemedTk = None
    logger.warning("The ttkthemes module is not available. Falling back to unthemed app.")


def run_gui():
    """
    Initializes and runs the main Tkinter application window.

    This function sets up the root window. It attempts to use the `ThemedTk`
    class from the `ttkthemes` library to create a modern-looking window with
    the 'arc' theme. If `ttkthemes` is not installed or fails, it gracefully
    falls back to the standard `tk.Tk` window, ensuring the application
    can still run.
    """
    try:
        root = ThemedTk(theme="arc")
        _ = SmsGUITk(root)
        root.mainloop()
    except (tk.TclError, TypeError):
        root = tk.Tk()
        _ = SmsGUITk(root)
        root.mainloop()
