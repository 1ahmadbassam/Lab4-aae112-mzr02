"""
Manages application-wide configuration settings.

This module contains global flags that control the application's behavior,
such as which data storage backend or GUI framework to use.
"""
ENABLE_DATABASE = True
"""If True, the application uses the database data manager; otherwise, it uses the in-memory manager."""

QT_GUI = True
"""If True, the application launches the PyQt5 GUI; otherwise, it launches the Tkinter GUI."""
