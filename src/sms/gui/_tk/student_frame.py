"""
Defines the GUI frame for student management in the Tkinter application.

This module contains the `StudentFrame` class, which provides all the UI
elements and logic for adding, viewing, editing, deleting, and searching
for students, as well as handling course registrations.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from ...data.data_manager import DataError
from ...data.data_manager import data_manager as dm
from ...models.student import Student
from ...utils.validator import check_name, check_age, check_email_r, check_id


class StudentFrame(ttk.Frame):
    """
    A Tkinter frame that encapsulates the student management interface.

    This frame includes a treeview for displaying students, entry fields for
    student details, and buttons for performing CRUD  operations.
    It also manages student enrollment in courses.

    :ivar controller: The main application controller, used for inter-frame communication.
    """
    def __init__(self, parent, controller):
        """
        Initializes the StudentFrame.

        :param parent: The parent widget.
        :param controller: The main application controller.
        """
        super().__init__(parent)
        self.controller = controller
        self.selected_student_id = None
        self.course_map = {}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        search_frame = ttk.Labelframe(self, text="Search Students", padding=(15, 10))
        search_frame.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=(10, 0))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Search by Name/ID:").grid(row=0, column=0, sticky=tk.W)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)

        search_button = ttk.Button(search_frame, text="Search", command=self.search_students)
        search_button.grid(row=0, column=2, padx=5)

        clear_button = ttk.Button(search_frame, text="Clear", command=self.refresh_data)
        clear_button.grid(row=0, column=3, padx=5)

        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=10)
        tree_frame.columnconfigure(0, weight=1)

        columns = (*Student.row(by_id=True),)
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        self.tree.heading("student_id", text="Student ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("age", text="Age")
        self.tree.heading("email", text="Email")

        self.tree.column("student_id", width=100)
        self.tree.column("name", width=200)
        self.tree.column("age", width=50)

        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_student_select)

        details_container = ttk.Frame(self)
        details_container.grid(row=2, column=0, sticky=tk.EW, padx=10, pady=10)
        details_container.columnconfigure(0, weight=1)
        details_container.columnconfigure(1, weight=1)

        details_frame = ttk.Labelframe(details_container, text="Student Details", padding=(15, 10))
        details_frame.grid(row=0, column=0, sticky=tk.NSEW)
        details_frame.columnconfigure(1, weight=1)

        # Form Fields
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = ttk.Entry(details_frame)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)

        ttk.Label(details_frame, text="Age:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.age_entry = ttk.Entry(details_frame)
        self.age_entry.grid(row=1, column=1, sticky=tk.EW, padx=5)

        ttk.Label(details_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.email_entry = ttk.Entry(details_frame)
        self.email_entry.grid(row=2, column=1, sticky=tk.EW, padx=5)

        ttk.Label(details_frame, text="Student ID:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.id_entry = ttk.Entry(details_frame)
        self.id_entry.grid(row=3, column=1, sticky=tk.EW, padx=5)

        ttk.Label(details_frame, text="Register for Course:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5), pady=2)
        self.course_combobox = ttk.Combobox(details_frame, state="disabled")
        self.course_combobox.grid(row=0, column=3, sticky=tk.EW, padx=5)

        self.register_btn = ttk.Button(details_frame, text="Register", state="disabled",
                                       command=self.register_for_course)
        self.register_btn.grid(row=1, column=3, sticky=tk.E, padx=5)

        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10, sticky=tk.E)

        self.action_btn = ttk.Button(button_frame, text="Add Student", command=self.add_student)
        self.action_btn.pack(side=tk.LEFT, padx=5)

        self.delete_btn = ttk.Button(button_frame, text="Delete Selected", state="disabled",
                                     command=self.delete_student)
        self.delete_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(button_frame, text="Clear Form", command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        courses_frame = ttk.Labelframe(details_container, text="Registered Courses", padding=(15, 10))
        courses_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=(10, 0))
        courses_frame.columnconfigure(0, weight=1)
        courses_frame.rowconfigure(0, weight=1)

        course_cols = ("course_id", "course_name")
        self.courses_tree = ttk.Treeview(courses_frame, columns=course_cols, show="headings")
        self.courses_tree.heading("course_id", text="ID")
        self.courses_tree.heading("course_name", text="Course Name")
        self.courses_tree.column("course_id", width=80)
        self.courses_tree.grid(row=0, column=0, sticky=tk.NSEW)

    def refresh_data(self, student_list=None):
        """
        Refreshes the student treeview with current data.

        Clears and repopulates the main student list. If a `student_list` is
        provided, it displays only those students; otherwise, it fetches all
        students from the data manager. It also refreshes the course dropdown.

        :param student_list: An optional list of students to display.
        :type student_list: list[Student], optional
        """
        if student_list is None:
            self.search_entry.delete(0, tk.END)

        for item in self.tree.get_children():
            self.tree.delete(item)

        students_to_display = student_list if student_list is not None else dm.get_students()

        for student in students_to_display:
            self.tree.insert("", tk.END, values=(*student.to_row(by_id=True),))

        self.course_map = {f"{c.course_name} ({c.course_id})": c for c in dm.get_courses()}
        self.course_combobox['values'] = list(self.course_map.keys())

    def search_students(self):
        """
        Filters the student treeview based on the search entry query.
        """
        query = self.search_entry.get().strip().lower()
        if not query:
            self.refresh_data()
            return

        all_students = dm.get_students()
        filtered_students = [student for student in all_students if
                             query in student.name.lower() or query in student.student_id]

        if not filtered_students:
            messagebox.showinfo("No Results", "No students found matching search query.")

        self.refresh_data(student_list=filtered_students)
        self.controller.update_status(f"Found {len(filtered_students)} students matching '{query}'.")

    def on_student_select(self, _):
        """
        Handles the event when a student is selected in the treeview.

        Populates the detail form with the selected student's data and updates
        the UI to an "edit" state.

        :param _: The event object (unused).
        """
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item = self.tree.item(selected_items[0])
        student_id, name, age, email = item['values']
        # treeview auto ints it
        student_id = str(student_id)

        self.clear_form()  # Clear form before populating
        self.name_entry.insert(0, name)
        self.age_entry.insert(0, age)
        self.email_entry.insert(0, email)
        self.id_entry.insert(0, student_id)

        self.id_entry.config(state="disabled")  # Prevent editing ID
        self.action_btn.config(text="Save Changes", command=self.save_changes)
        self.delete_btn.config(state="normal")
        self.course_combobox.config(state="readonly")
        self.register_btn.config(state="normal")

        self.selected_student_id = student_id
        self.update_registered_courses_view()

    def update_registered_courses_view(self):
        """
        Updates the registered courses list for the currently selected student.
        """
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)

        if self.selected_student_id:
            student = dm.get_student(self.selected_student_id)
            if student:
                for course in sorted(student.registered_courses, key=lambda c: c.course_id):
                    self.courses_tree.insert("", tk.END, values=(course.course_id, course.course_name))

    def add_student(self):
        """
        Handles the "Add Student" button click.

        Validates form input and adds a new student via the data manager.
        Displays success or error messages to the user.
        """
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        email = self.email_entry.get().strip()
        student_id = self.id_entry.get().strip()

        if not name or not age or not email or not student_id:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        if not check_name(name):
            messagebox.showerror(title="Error Adding Student!", message="Invalid Name.")
            return

        try:
            age = int(age)
        except ValueError:
            messagebox.showerror(title="Error Adding Student!", message="Age must be a number.")
            return

        if not check_age(age):
            messagebox.showerror(title="Error Adding Student!", message="Invalid Age.")
            return

        if not (em := check_email_r(email))[0]:
            messagebox.showerror(title="Error Adding Student!",
                                 message="Invalid Email Address" + (f": {em[1]}" if em[1] else "."))
            return

        if not check_id(student_id):
            messagebox.showerror(title="Error Adding Student!", message="Invalid Student ID.")
            return

        try:
            dm.add_student(name=name, age=age, email=email, student_id=student_id)
        except DataError as e:
            messagebox.showerror("Database Error Adding Student!", str(e))
            return

        messagebox.showinfo("Success", f"Student with ID '{student_id}' added successfully.")
        self.controller.update_status(f"Student {name} added.")
        self.clear_form()
        self.refresh_data()

    def save_changes(self):
        """
        Handles the "Save Changes" button click for an existing student.

        Validates form input and updates the selected student's record
        via the data manager.
        """
        if not self.selected_student_id:
            return

        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        email = self.email_entry.get().strip()

        if not name or not age or not email:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        if not check_name(name):
            messagebox.showerror(title="Error Updating Student!", message="Invalid Name.")
            return

        try:
            age = int(age)
        except ValueError:
            messagebox.showerror(title="Error Updating Student!", message="Age must be a number.")
            return

        if not check_age(age):
            messagebox.showerror(title="Error Updating Student!", message="Invalid Age.")
            return

        if not (em := check_email_r(email))[0]:
            messagebox.showerror(title="Error Updating Student!",
                                 message="Invalid Email Address" + (f": {em[1]}" if em[1] else "."))
            return

        try:
            dm.edit_student(name=name, age=age, email=email, student_id=self.selected_student_id)
        except DataError as e:
            messagebox.showerror("Database Error Updating Student!", str(e))
            return

        messagebox.showinfo("Success", f"Student with ID '{self.selected_student_id}' updated successfully.")
        self.controller.update_status(f"Student {name} updated.")
        self.clear_form()
        self.refresh_data()

    def delete_student(self):
        """
        Handles the "Delete Selected" button click.

        Asks for user confirmation before deleting the currently selected
        student from the data store.
        """
        if not self.selected_student_id:
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
            try:
                dm.remove_student(self.selected_student_id)
            except DataError as e:
                messagebox.showerror("Database Error Deleting Student!", str(e))
                return

            self.controller.update_status(f"Student {self.selected_student_id} deleted successfully.")
            messagebox.showinfo("Success", "Student deleted.")
            self.clear_form()
            self.refresh_data()

    def register_for_course(self):
        """
        Handles the "Register" button click.

        Enrolls the selected student in the selected course from the dropdown.
        """
        if not self.selected_student_id:
            messagebox.showwarning("Selection Error", "Please select a student first.")
            return

        selected_course_str = self.course_combobox.get()
        if not selected_course_str:
            messagebox.showwarning("Selection Error", "Please select a course to register.")
            return

        student = dm.get_student(self.selected_student_id)
        course = self.course_map.get(selected_course_str)

        if course.course_id in {c.course_id for c in student.registered_courses}:
            messagebox.showwarning("Registration Error", f"{student.name} is already registered for this course.")
            return

        dm.enroll_student(student.student_id, course.course_id)
        self.controller.update_status(f"Registered {student.name} for {course.course_name}.")
        messagebox.showinfo("Success", "Student registered successfully.")
        self.course_combobox.set('')
        self.update_registered_courses_view()

    def clear_form(self):
        """
        Clears all entry fields and resets the frame to its initial state.

        Resets form fields, buttons, and internal state variables to prepare
        for adding a new student or making a new selection.
        """
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.id_entry.config(state="normal")
        self.id_entry.delete(0, tk.END)

        self.action_btn.config(text="Add Student", command=self.add_student)
        self.delete_btn.config(state="disabled")
        self.course_combobox.config(state="disabled")
        self.register_btn.config(state="disabled")
        self.course_combobox.set('')

        self.selected_student_id = None
        self.tree.selection_remove(self.tree.selection())
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)
