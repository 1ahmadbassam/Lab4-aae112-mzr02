"""
Defines the main application window for the Tkinter GUI.

This module contains the `SmsGUITk` class, which constructs the root window,
menu bar, status bar, and the tabbed notebook interface that holds the
student, instructor, and course management frames.
"""
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .constants import *
from .course_frame import CourseFrame
from .instructor_frame import InstructorFrame
from .student_frame import StudentFrame
from ...data.data_manager import data_manager as dm
from config import ENABLE_DATABASE

class SmsGUITk:
    """
    The main controller and root window for the Tkinter GUI.

    This class assembles all the individual frames into a tabbed notebook,
    manages the top-level menu, and handles application-wide actions like
    saving/loading data and updating the status bar.

    :ivar root: The root Tkinter window.
    :ivar notebook: The ttk.Notebook widget that holds the management frames.
    :ivar student_tab: The frame for student management.
    :ivar instructor_tab: The frame for instructor management.
    :ivar course_tab: The frame for course management.
    :ivar status_bar: The label at the bottom of the window for status messages.
    """
    def __init__(self, root):
        """
        Initializes the main GUI window.

        :param root: The root `tk.Tk()` instance.
        """
        self.root = root
        self.root.title("School Management System")
        self.root.geometry("1000x700")

        style = ttk.Style(self.root)
        style.configure('TLabel', font=LABEL_FONT)
        style.configure('TButton', font=LABEL_FONT)

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        load_menu = tk.Menu(file_menu, tearoff=0)
        save_menu = tk.Menu(file_menu, tearoff=0)

        file_menu.add_cascade(label="Load Data", menu=load_menu)
        file_menu.add_cascade(label="Save Data", menu=save_menu)

        load_menu.add_command(label="from JSON File...", command=self.load_from_json)
        load_menu.add_command(label="from CSV Directory...", command=self.load_from_csv)

        save_menu.add_command(label="to JSON File...", command=self.save_to_json)
        save_menu.add_command(label="to CSV Directory...", command=self.save_to_csv)


        if ENABLE_DATABASE:
            file_menu.add_separator()
            file_menu.add_command(label="Backup Database...", command=self.backup_database)

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.student_tab = StudentFrame(self.notebook, self)
        self.instructor_tab = InstructorFrame(self.notebook, self)
        self.course_tab = CourseFrame(self.notebook, self)

        self.notebook.add(self.student_tab, text="Students")
        self.notebook.add(self.instructor_tab, text="Instructors")
        self.notebook.add(self.course_tab, text="Courses")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.status_bar = ttk.Label(self.root, text="Welcome!", relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.refresh_all_tabs()

    def on_tab_changed(self, _):
        """
        Callback for when the active notebook tab is changed.

        Refreshes the data in the newly selected tab.

        :param _: The event object (unused).
        """
        selected_tab = self.notebook.nametowidget(self.notebook.select())
        if hasattr(selected_tab, 'refresh_data'):
            selected_tab.refresh_data()

    def update_status(self, message):
        """
        Updates the text displayed in the status bar.

        :param message: The new message to display.
        :type message: str
        """
        self.status_bar.config(text=message)

    def backup_database(self):
        """
        Handles the 'Backup Database' menu command.

        Opens a save dialog to allow the user to copy the database file to a
        new location. This menu option is only available if database mode is enabled.
        """
        if ENABLE_DATABASE:
            source_db_path = dm.get_db_path()
            if not source_db_path:
                messagebox.showerror("Backup Error", "Could not determine the source database path.")
                return

            backup_path = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
                title="Backup Database As"
            )

            if not backup_path:
                self.update_status("Database backup cancelled.")
                return

            try:
                shutil.copy(source_db_path, backup_path)
                self.update_status(f"Database successfully backed up to {backup_path}")
                messagebox.showinfo("Backup Successful", "The database has been backed up successfully.")
            except Exception as e:
                self.update_status("Database backup failed.")
                messagebox.showerror("Backup Error", f"An error occurred during backup:\n{e}")


    def save_to_json(self):
        """
        Handles the 'Save to JSON' menu command.

        Opens a file dialog and saves all application data to a JSON file.
        """
        filepath = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                                                title="Save School Data to JSON")
        if not filepath: return
        try:
            dm.data_to_json(filepath)
            self.update_status(f"Data saved to {filepath}.")
            messagebox.showinfo("Success", "Data saved to JSON successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save JSON file: {e}")

    def load_from_json(self):
        """
        Handles the 'Load from JSON' menu command.

        Opens a file dialog, loads data from a JSON file, and refreshes all tabs.
        """
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                                              title="Load School Data from JSON")
        if not filepath: return
        try:
            dm.data_from_json(filepath)
            self.update_status(f"Data loaded from {filepath}")
            messagebox.showinfo("Success", "Data loaded from JSON successfully.")
            self.refresh_all_tabs()
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load JSON file: {e}")

    def save_to_csv(self):
        """
        Handles the 'Save to CSV' menu command.

        Opens a directory dialog and saves all application data to a set of CSV files.
        """
        dirpath = filedialog.askdirectory(title="Select Directory to Save CSV Files")
        if not dirpath: return
        try:
            dm.data_to_csv(dirpath)
            self.update_status(f"Data saved to CSVs in {dirpath}")
            messagebox.showinfo("Success", "Data saved to CSV successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save CSV files: {e}")

    def load_from_csv(self):
        """
        Handles the 'Load from CSV' menu command.

        Opens a directory dialog, loads data from a set of CSV files, and refreshes all tabs.
        """
        dirpath = filedialog.askdirectory(title="Select Directory with CSV Files")
        if not dirpath: return
        try:
            dm.data_from_csv(dirpath)
            self.update_status(f"Data loaded from CSVs in {dirpath}")
            messagebox.showinfo("Success", "Data loaded from CSV successfully.")
            self.refresh_all_tabs()
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load CSV files: {e}")
            self.refresh_all_tabs()

    def refresh_all_tabs(self):
        """
        Calls the `refresh_data` method on every tab in the notebook.

        Ensures that all views are synchronized with the current data state.
        """
        for tab_name in self.notebook.tabs():
            tab_widget = self.notebook.nametowidget(tab_name)
            if hasattr(tab_widget, 'refresh_data'):
                tab_widget.refresh_data()
