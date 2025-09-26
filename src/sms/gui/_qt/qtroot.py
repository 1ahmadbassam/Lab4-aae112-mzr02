"""
Main GUI Window for the School Management System.

This module defines the main window of the application, SmsGUIQt, which inherits
from QMainWindow. It sets up the entire user interface, including the menu bar,
a tabbed interface for managing students, instructors, and courses, and a
status bar.
"""
import shutil

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                             QAction, QMenu, QStatusBar, QFileDialog, QMessageBox)

from .constants import LABEL_FONT
from .course_frame import CourseFrame
from .instructor_frame import InstructorFrame
from .student_frame import StudentFrame
from ...data.data_manager import data_manager as dm
from config import ENABLE_DATABASE


class SmsGUIQt(QMainWindow):
    """
    The main window for the School Management System application.

    This class builds the main application interface, including menus, tabs for
    different data models, and a status bar. It acts as the central controller
    for the GUI, handling user actions and coordinating data display across
    different frames.
    """
    def __init__(self):
        """
        Constructor for the SmsGUIQt main window.
        """
        super().__init__()
        self.setWindowTitle("School Management System")
        self.setGeometry(100, 100, 1100, 750)
        self.setFont(LABEL_FONT)

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self._create_actions()
        self._create_menu_bar()
        self._create_tab_widget()
        self._create_status_bar()
        self.refresh_all_tabs()

    def _create_actions(self):
        """
        Initializes all QAction objects for the menu bar.
        """
        self.load_json_action = QAction("&from JSON File...", self)
        self.load_json_action.triggered.connect(self.load_from_json)
        self.load_csv_action = QAction("&from CSV Directory...", self)
        self.load_csv_action.triggered.connect(self.load_from_csv)
        self.save_json_action = QAction("&to JSON File...", self)
        self.save_json_action.triggered.connect(self.save_to_json)
        self.save_csv_action = QAction("&to CSV Directory...", self)
        self.save_csv_action.triggered.connect(self.save_to_csv)
        if ENABLE_DATABASE:
            self.backup_db_action = QAction("&Backup Database...", self)
            self.backup_db_action.triggered.connect(self.backup_database)
        self.exit_action = QAction("E&xit", self)
        self.exit_action.triggered.connect(self.close)

    def _create_menu_bar(self):
        """
        Creates the main menu bar with 'File' and sub-menus.
        """
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        load_menu = QMenu("Load Data", self)
        load_menu.addAction(self.load_json_action)
        load_menu.addAction(self.load_csv_action)
        save_menu = QMenu("Save Data", self)
        save_menu.addAction(self.save_json_action)
        save_menu.addAction(self.save_csv_action)
        file_menu.addMenu(load_menu)
        file_menu.addMenu(save_menu)
        if ENABLE_DATABASE:
            file_menu.addSeparator()
            file_menu.addAction(self.backup_db_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

    def _create_tab_widget(self):
        """
        Creates the main QTabWidget and populates it with management frames.
        """
        self.notebook = QTabWidget()
        self.main_layout.addWidget(self.notebook)
        self.student_tab = StudentFrame(self, self)
        self.instructor_tab = InstructorFrame(self, self)
        self.course_tab = CourseFrame(self, self)
        self.notebook.addTab(self.student_tab, "Students")
        self.notebook.addTab(self.instructor_tab, "Instructors")
        self.notebook.addTab(self.course_tab, "Courses")
        self.notebook.currentChanged.connect(self.on_tab_changed)

    def _create_status_bar(self):
        """
        Initializes the status bar at the bottom of the main window.
        """
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("Welcome!")

    def on_tab_changed(self, index):
        """
        Slot that triggers when the current tab is changed.

        Refreshes the data in the newly selected tab.

        :param index: The index of the newly selected tab.
        :type index: int
        """
        current_tab_widget = self.notebook.widget(index)
        if hasattr(current_tab_widget, 'refresh_data'):
            current_tab_widget.refresh_data()

    def update_status(self, message):
        """
        Displays a message on the status bar for a short duration.

        :param message: The text message to display.
        :type message: str
        """
        self.status_bar.showMessage(message, 5000)

    def backup_database(self):
        """
        Handles the database backup operation.

        Opens a file dialog to ask the user for a destination path and copies
        the current database file to that location.
        """
        if not ENABLE_DATABASE: return
        source_db_path = dm.get_db_path()
        if not source_db_path:
            QMessageBox.critical(self, "Backup Error", "Could not determine the source database path.")
            return
        backup_path, _ = QFileDialog.getSaveFileName(self, "Backup Database As", "",
                                                     "SQLite Database (*.db);;All Files (*.*)")
        if not backup_path:
            self.update_status("Database backup cancelled.")
            return
        try:
            shutil.copy(source_db_path, backup_path)
            msg = f"Database successfully backed up to {backup_path}"
            self.update_status(msg)
            QMessageBox.information(self, "Backup Successful", msg)
        except Exception as e:
            self.update_status("Database backup failed.")
            QMessageBox.critical(self, "Backup Error", f"An error occurred during backup:\n{e}")

    def save_to_json(self):
        """
        Handles saving all application data to a single JSON file.
        """
        filepath, _ = QFileDialog.getSaveFileName(self, "Save School Data to JSON", "",
                                                  "JSON Files (*.json);;All Files (*.*)")
        if not filepath: return
        try:
            dm.data_to_json(filepath)
            self.update_status(f"Data saved to {filepath}.")
            QMessageBox.information(self, "Success", "Data saved to JSON successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save JSON file: {e}")

    def load_from_json(self):
        """
        Handles loading all application data from a single JSON file.
        """
        filepath, _ = QFileDialog.getOpenFileName(self, "Load School Data from JSON", "",
                                                  "JSON Files (*.json);;All Files (*.*)")
        if not filepath: return
        try:
            dm.data_from_json(filepath)
            self.update_status(f"Data loaded from {filepath}")
            QMessageBox.information(self, "Success", "Data loaded from JSON successfully.")
            self.refresh_all_tabs()
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load JSON file: {e}")

    def save_to_csv(self):
        """
        Handles saving application data to multiple CSV files in a directory.
        """
        dirpath = QFileDialog.getExistingDirectory(self, "Select Directory to Save CSV Files")
        if not dirpath: return
        try:
            dm.data_to_csv(dirpath)
            self.update_status(f"Data saved to CSVs in {dirpath}")
            QMessageBox.information(self, "Success", "Data saved to CSV successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save CSV files: {e}")

    def load_from_csv(self):
        """
        Handles loading application data from multiple CSV files in a directory.
        """
        dirpath = QFileDialog.getExistingDirectory(self, "Select Directory with CSV Files")
        if not dirpath: return
        try:
            dm.data_from_csv(dirpath)
            self.update_status(f"Data loaded from CSVs in {dirpath}")
            QMessageBox.information(self, "Success", "Data loaded from CSV successfully.")
            self.refresh_all_tabs()
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load CSV files: {e}")

    def refresh_all_tabs(self):
        """
        Calls the refresh_data method on all tabs in the notebook.
        """
        for i in range(self.notebook.count()):
            tab_widget = self.notebook.widget(i)
            if hasattr(tab_widget, 'refresh_data'):
                tab_widget.refresh_data()
