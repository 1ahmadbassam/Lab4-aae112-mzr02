"""
GUI Font Definitions.

This module defines QFont constants that will be used ot style
the PyQt5 GUI.
Defining the fonts here allows for consistent styling accrsos the application
and make it easy to update fonts globally.

Attributes:
    TITLE_FONT (QFont): The font used for main titles within the application.
                        Set to Verdana, size 20.
    
    LABEL_FONT (QFont): The font used for general labels and descriptive text.
                        Set to Segoe UI, size 12.
"""
from PyQt5.QtGui import QFont


TITLE_FONT = QFont("Verdana", 20)
LABEL_FONT = QFont("Segoe UI", 12)
