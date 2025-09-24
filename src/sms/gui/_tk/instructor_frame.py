"""
Defines the GUI frame for instructor management in the Tkinter application.

This module contains the `InstructorFrame` class, which provides all the UI
elements and logic for adding, viewing, editing, deleting, and searching
for instructors.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from ...data.data_manager import DataError
from ...data.data_manager import data_manager as dm
from ...models.instructor import Instructor
from ...utils.validator import check_name, check_age, check_email_r, check_id


class InstructorFrame(ttk.Frame):
    """
    A Tkinter frame that encapsulates the instructor management interface.

    This frame includes a treeview for displaying instructors, entry fields for
    instructor details, and buttons for performing CRUD operations. It also
    displays the courses assigned to a selected instructor.

    :ivar controller: The main application controller for inter-frame communication.
    """
    def __init__(self, parent, controller):
        """
        Initializes the InstructorFrame.

        :param parent: The parent widget.
        :param controller: The main application controller.
        """
        super().__init__(parent)
        self.controller = controller
        self.selected_instructor_id = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        search_frame = ttk.Labelframe(self, text="Search Instructors", padding=(15, 10))
        search_frame.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=(10, 0))
        search_frame.columnconfigure(1, weight=1)
        ttk.Label(search_frame, text="Search by Name/ID:").grid(row=0, column=0, sticky=tk.W)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        search_button = ttk.Button(search_frame, text="Search", command=self.search_instructors)
        search_button.grid(row=0, column=2, padx=5)
        clear_button = ttk.Button(search_frame, text="Clear", command=self.refresh_data)
        clear_button.grid(row=0, column=3, padx=5)

        tree_container = ttk.Frame(self)
        tree_container.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=10)
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        columns = (*Instructor.row(by_id=True),)
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        self.tree.heading("instructor_id", text="Instructor ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("age", text="Age")
        self.tree.heading("email", text="Email")
        self.tree.column("instructor_id", width=120)
        self.tree.column("name", width=200)
        self.tree.column("age", width=50, anchor=tk.CENTER)
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.tree.bind("<<TreeviewSelect>>", self.on_instructor_select)
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)

        details_container = ttk.Frame(self)
        details_container.grid(row=2, column=0, sticky=tk.EW, padx=10, pady=10)
        details_container.columnconfigure(0, weight=1)
        details_container.columnconfigure(1, weight=1)

        details_frame = ttk.Labelframe(details_container, text="Instructor Details", padding=(15, 10))
        details_frame.grid(row=0, column=0, sticky=tk.NSEW)
        details_frame.columnconfigure(1, weight=1)
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = ttk.Entry(details_frame)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        ttk.Label(details_frame, text="Age:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.age_entry = ttk.Entry(details_frame)
        self.age_entry.grid(row=1, column=1, sticky=tk.EW, padx=5)
        ttk.Label(details_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.email_entry = ttk.Entry(details_frame)
        self.email_entry.grid(row=2, column=1, sticky=tk.EW, padx=5)
        ttk.Label(details_frame, text="Instructor ID:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.id_entry = ttk.Entry(details_frame)
        self.id_entry.grid(row=3, column=1, sticky=tk.EW, padx=5)

        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.E)
        self.action_btn = ttk.Button(button_frame, text="Add Instructor", command=self.add_instructor)
        self.action_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn = ttk.Button(button_frame, text="Delete Selected", state="disabled",
                                     command=self.delete_instructor)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        self.clear_btn = ttk.Button(button_frame, text="Clear Form", command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        courses_frame = ttk.Labelframe(details_container, text="Assigned Courses", padding=(15, 10))
        courses_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=(10, 0))
        courses_frame.columnconfigure(0, weight=1)
        courses_frame.rowconfigure(0, weight=1)
        course_cols = ("course_id", "course_name")
        self.courses_tree = ttk.Treeview(courses_frame, columns=course_cols, show="headings")
        self.courses_tree.heading("course_id", text="ID")
        self.courses_tree.heading("course_name", text="Course Name")
        self.courses_tree.column("course_id", width=80)
        self.courses_tree.grid(row=0, column=0, sticky=tk.NSEW)

    def refresh_data(self, instructor_list=None):
        """
        Refreshes the instructor treeview with current data.

        If an `instructor_list` is provided, it displays only those instructors;
        otherwise, it fetches all instructors from the data manager.

        :param instructor_list: An optional list of instructors to display.
        :type instructor_list: list[Instructor], optional
        """
        if instructor_list is None: self.search_entry.delete(0, tk.END)
        for item in self.tree.get_children(): self.tree.delete(item)
        instructors_to_display = instructor_list if instructor_list is not None else dm.get_instructors()
        for instructor in instructors_to_display:
            self.tree.insert("", tk.END, values=instructor.to_row(by_id=True))

    def search_instructors(self):
        """
        Filters the instructor treeview based on the search entry query.
        """
        query = self.search_entry.get().strip().lower()
        if not query:
            self.refresh_data()
            return
        all_instructors = dm.get_instructors()
        filtered = [inst for inst in all_instructors if query in inst.name.lower() or query in inst.instructor_id]
        if not filtered: messagebox.showinfo("No Results", "No instructors found.")
        self.refresh_data(instructor_list=filtered)
        self.controller.update_status(f"Found {len(filtered)} instructors matching '{query}'.")

    def on_instructor_select(self, _):
        """
        Handles the event when an instructor is selected in the treeview.

        Populates the detail form with the selected instructor's data and updates
        the UI to an "edit" state.

        :param _: The event object (unused).
        """
        selected_items = self.tree.selection()
        if not selected_items: return
        item = self.tree.item(selected_items[0])
        inst_id, name, age, email = item['values']
        inst_id = str(inst_id)
        self.clear_form()
        self.name_entry.insert(0, name)
        self.age_entry.insert(0, age)
        self.email_entry.insert(0, email)
        self.id_entry.insert(0, inst_id)
        self.id_entry.config(state="disabled")
        self.action_btn.config(text="Save Changes", command=self.save_changes)
        self.delete_btn.config(state="normal")
        self.selected_instructor_id = inst_id
        self.update_assigned_courses_view()

    def update_assigned_courses_view(self):
        """
        Updates the assigned courses list for the currently selected instructor.
        """
        for item in self.courses_tree.get_children(): self.courses_tree.delete(item)
        if self.selected_instructor_id:
            instructor = dm.get_instructor(self.selected_instructor_id)
            if instructor:
                for course in sorted(instructor.assigned_courses, key=lambda c: c.course_id):
                    self.courses_tree.insert("", tk.END, values=(course.course_id, course.course_name))

    def add_instructor(self):
        """
        Handles the "Add Instructor" button click.

        Validates form input and adds a new instructor via the data manager.
        """
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        email = self.email_entry.get().strip()
        instructor_id = self.id_entry.get().strip()

        if not name or not age or not email or not instructor_id:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        if not check_name(name):
            messagebox.showerror(title="Error Adding Instructor!", message="Invalid Name.")
            return

        try:
            age = int(age)
        except ValueError:
            messagebox.showerror(title="Error Adding Instructor!", message="Age must be a number.")
            return

        if not check_age(age):
            messagebox.showerror(title="Error Adding Instructor!", message="Invalid Age.")
            return

        if not (em := check_email_r(email))[0]:
            messagebox.showerror(title="Error Adding Instructor!",
                                 message="Invalid Email Address" + (f": {em[1]}" if em[1] else "."))
            return

        if not check_id(instructor_id):
            messagebox.showerror(title="Error Adding Instructor!", message="Invalid Instructor ID.")
            return

        try:
            dm.add_instructor(name=name, age=age, email=email, instructor_id=instructor_id)
        except DataError as e:
            messagebox.showerror("Database Error Adding Instructor", str(e))
            return

        messagebox.showinfo("Success", f"Instructor with ID '{instructor_id}' added successfully.")
        self.controller.update_status(f"Instructor {name} added.")
        self.clear_form()
        self.refresh_data()

    def save_changes(self):
        """
        Handles the "Save Changes" button click for an existing instructor.

        Validates form input and updates the selected instructor's record.
        """
        if not self.selected_instructor_id:
            return

        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        email = self.email_entry.get().strip()

        if not name or not age or not email:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        if not check_name(name):
            messagebox.showerror(title="Error Updating Instructor!", message="Invalid Name.")
            return

        try:
            age = int(age)
        except ValueError:
            messagebox.showerror(title="Error Updating Instructor!", message="Age must be a number.")
            return

        if not check_age(age):
            messagebox.showerror(title="Error Updating Instructor!", message="Invalid Age.")
            return

        if not (em := check_email_r(email))[0]:
            messagebox.showerror(title="Error Updating Instructor!",
                                 message="Invalid Email Address" + (f": {em[1]}" if em[1] else "."))
            return

        try:
            dm.edit_instructor(instructor_id=self.selected_instructor_id, name=name, age=age, email=email)
        except DataError as e:
            messagebox.showerror("Database Error Updating Instructor!", str(e))
            return

        messagebox.showinfo("Success", f"Instructor with ID '{self.selected_instructor_id}' updated successfully.")
        self.controller.update_status(f"Instructor {name} updated.")
        self.clear_form()
        self.refresh_data()

    def delete_instructor(self):
        """
        Handles the "Delete Selected" button click.

        Asks for user confirmation before deleting the currently selected
        instructor from the data store.
        """
        if not self.selected_instructor_id:
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this instructor?"):
            try:
                dm.remove_instructor(self.selected_instructor_id)
            except DataError as e:
                messagebox.showerror("Database Error Deleting Instructor!", str(e))
                return

            self.controller.update_status(f"Instructor {self.selected_instructor_id} deleted successfully.")
            messagebox.showinfo("Success", "Instructor deleted.")
            self.clear_form()
            self.refresh_data()

    def clear_form(self):
        """
        Clears all entry fields and resets the frame to its initial state.

        Resets form fields, buttons, and internal state variables to prepare
        for adding a new instructor or making a new selection.
        """
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.id_entry.config(state="normal")
        self.id_entry.delete(0, tk.END)
        self.action_btn.config(text="Add Instructor", command=self.add_instructor)
        self.delete_btn.config(state="disabled")
        self.selected_instructor_id = None
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection())
        for item in self.courses_tree.get_children(): self.courses_tree.delete(item)
