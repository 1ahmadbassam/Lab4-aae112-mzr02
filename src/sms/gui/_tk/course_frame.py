"""
Defines the GUI frame for course management in the Tkinter application.

This module contains the `CourseFrame` class, which provides all the UI
elements and logic for adding, viewing, editing, deleting, and searching
for courses.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from ...data.data_manager import DataError
from ...data.data_manager import data_manager as dm
from ...models.course import Course
from ...utils.validator import check_course_name, check_course_id


class CourseFrame(ttk.Frame):
    """
    A Tkinter frame that encapsulates the course management interface.

    This frame includes a treeview for displaying courses, entry fields for
    course details, and buttons for performing CRUD operations. It also
    displays the students enrolled in a selected course.

    :ivar controller: The main application controller for inter-frame communication.
    """
    def __init__(self, parent, controller):
        """
        Initializes the CourseFrame.

        :param parent: The parent widget.
        :param controller: The main application controller.
        """
        super().__init__(parent)
        self.controller = controller
        self.selected_course_id = None
        self.instructor_map = {}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        search_frame = ttk.Labelframe(self, text="Search Courses", padding=(15, 10))
        search_frame.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=(10, 0))
        search_frame.columnconfigure(1, weight=1)
        ttk.Label(search_frame, text="Search by Name/ID:").grid(row=0, column=0, sticky=tk.W)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        search_button = ttk.Button(search_frame, text="Search", command=self.search_courses)
        search_button.grid(row=0, column=2, padx=5)
        clear_button = ttk.Button(search_frame, text="Clear", command=self.refresh_data)
        clear_button.grid(row=0, column=3, padx=5)

        tree_container = ttk.Frame(self)
        tree_container.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=10)
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        columns = (*Course.row(),)
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        self.tree.heading("course_id", text="Course ID")
        self.tree.heading("course_name", text="Course Name")
        self.tree.heading("instructor_id", text="Instructor ID")
        self.tree.column("course_id", width=100)
        self.tree.column("course_name", width=250)
        self.tree.column("instructor_id", width=120)
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.tree.bind("<<TreeviewSelect>>", self.on_course_select)
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)

        details_container = ttk.Frame(self)
        details_container.grid(row=2, column=0, sticky=tk.EW, padx=10, pady=10)
        details_container.columnconfigure(0, weight=1)
        details_container.columnconfigure(1, weight=1)

        details_frame = ttk.Labelframe(details_container, text="Course Details", padding=(15, 10))
        details_frame.grid(row=0, column=0, sticky=tk.NSEW)
        details_frame.columnconfigure(1, weight=1)
        ttk.Label(details_frame, text="Course Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = ttk.Entry(details_frame)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        ttk.Label(details_frame, text="Course ID:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.id_entry = ttk.Entry(details_frame)
        self.id_entry.grid(row=1, column=1, sticky=tk.EW, padx=5)
        ttk.Label(details_frame, text="Instructor:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.instructor_combobox = ttk.Combobox(details_frame, state="readonly")
        self.instructor_combobox.grid(row=2, column=1, sticky=tk.EW, padx=5)

        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.E)
        self.action_btn = ttk.Button(button_frame, text="Add Course", command=self.add_course)
        self.action_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn = ttk.Button(button_frame, text="Delete Selected", state="disabled", command=self.delete_course)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        self.clear_btn = ttk.Button(button_frame, text="Clear Form", command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        students_frame = ttk.Labelframe(details_container, text="Enrolled Students", padding=(15, 10))
        students_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=(10, 0))
        students_frame.columnconfigure(0, weight=1)
        students_frame.rowconfigure(0, weight=1)
        student_cols = ("student_id", "student_name")
        self.students_tree = ttk.Treeview(students_frame, columns=student_cols, show="headings")
        self.students_tree.heading("student_id", text="ID")
        self.students_tree.heading("student_name", text="Student Name")
        self.students_tree.column("student_id", width=100)
        self.students_tree.grid(row=0, column=0, sticky=tk.NSEW)

    def refresh_data(self, course_list=None):
        """
        Refreshes the course treeview with current data.

        If a `course_list` is provided, it displays only those courses;
        otherwise, it fetches all courses from the data manager. It also
        refreshes the instructor dropdown list.

        :param course_list: An optional list of courses to display.
        :type course_list: list[Course], optional
        """
        if course_list is None: self.search_entry.delete(0, tk.END)
        for item in self.tree.get_children(): self.tree.delete(item)
        courses_to_display = course_list if course_list is not None else dm.get_courses()
        for course in courses_to_display:
            self.tree.insert("", tk.END, values=course.to_row())

        self.instructor_map = {f"{inst.name} ({inst.instructor_id})": inst for inst in dm.get_instructors()}
        self.instructor_combobox['values'] = list(self.instructor_map.keys())

    def search_courses(self):
        """
        Filters the course treeview based on the search entry query.
        """
        query = self.search_entry.get().strip().lower()
        if not query:
            self.refresh_data()
            return
        all_courses = dm.get_courses()
        filtered = [c for c in all_courses if query in c.course_name.lower() or query in c.course_id.lower()]
        if not filtered: messagebox.showinfo("No Results", "No courses found.")
        self.refresh_data(course_list=filtered)
        self.controller.update_status(f"Found {len(filtered)} courses matching '{query}'.")

    def on_course_select(self, _):
        """
        Handles the event when a course is selected in the treeview.

        Populates the detail form with the selected course's data and updates
        the UI to an "edit" state.

        :param _: The event object (unused).
        """
        selected_items = self.tree.selection()
        if not selected_items: return
        item = self.tree.item(selected_items[0])
        course_id, name, instructor_id = item['values']
        course_id = str(course_id)
        instructor_id = str(instructor_id)

        self.clear_form()
        self.name_entry.insert(0, name)
        self.id_entry.insert(0, course_id)

        for display_text, instructor_obj in self.instructor_map.items():
            if instructor_obj.instructor_id == instructor_id:
                self.instructor_combobox.set(display_text)
                break

        self.id_entry.config(state="disabled")
        self.action_btn.config(text="Save Changes", command=self.save_changes)
        self.delete_btn.config(state="normal")
        self.selected_course_id = course_id
        self.update_enrolled_students_view()

    def update_enrolled_students_view(self):
        """
        Updates the enrolled students list for the currently selected course.
        """
        for item in self.students_tree.get_children(): self.students_tree.delete(item)
        if self.selected_course_id:
            course = dm.get_course(self.selected_course_id)
            if course:
                for student in sorted(course.enrolled_students, key=lambda s: s.name):
                    self.students_tree.insert("", tk.END, values=(student.student_id, student.name))

    def add_course(self):
        """
        Handles the "Add Course" button click.

        Validates form input and adds a new course via the data manager.
        """
        course_name = self.name_entry.get().strip()
        course_id = self.id_entry.get().strip()
        selected_instructor_str = self.instructor_combobox.get()

        if not course_name or not course_id or not selected_instructor_str:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        instructor = self.instructor_map.get(selected_instructor_str)

        if not check_course_name(course_name):
            messagebox.showerror(title="Error Adding Course!", message="Invalid Course Name.")
            return

        if not check_course_id(course_id):
            messagebox.showerror(title="Error Adding Course!", message="Invalid Course ID.")
            return

        try:
            dm.add_course(course_name=course_name, course_id=course_id, instructor=instructor)
        except DataError as e:
            messagebox.showerror("Database Error Adding Course!", str(e))
            return

        messagebox.showinfo("Success", f"Course with ID '{course_id}' added successfully.")
        self.controller.update_status(f"Course {course_name} added.")
        self.clear_form()
        self.refresh_data()

    def save_changes(self):
        """
        Handles the "Save Changes" button click for an existing course.

        Validates form input and updates the selected course's record.
        """
        if not self.selected_course_id:
            return

        course_name = self.name_entry.get().strip()
        instructor_str = self.instructor_combobox.get()

        if not course_name or not instructor_str:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        if not check_course_name(course_name):
            messagebox.showerror(title="Error Updating Course!", message="Invalid Name.")
            return

        instructor = self.instructor_map.get(instructor_str)

        try:
            dm.edit_course(course_id=self.selected_course_id, course_name=course_name, instructor=instructor)
        except DataError as e:
            messagebox.showerror("Database Error Updating Course!", str(e))
            return

        messagebox.showinfo("Success", f"Course with ID '{self.selected_course_id}' updated successfully.")
        self.controller.update_status(f"Student {course_name} updated.")
        self.clear_form()
        self.refresh_data()

    def delete_course(self):
        """
        Handles the "Delete Selected" button click.

        Asks for user confirmation before deleting the currently selected
        course, which also unenrolls all students from it.
        """
        if not self.selected_course_id:
            return
        if messagebox.askyesno("Confirm Delete", "This will unregister all students from this course. "
                                                 "Are you sure?"):
            try:
                dm.remove_course(self.selected_course_id)
            except DataError as e:
                messagebox.showerror("Database Error Deleting Course!", str(e))
                return

            self.controller.update_status(f"Course {self.selected_course_id} deleted successfully.")
            messagebox.showinfo("Success", "Course deleted.")
            self.clear_form()
            self.refresh_data()

    def clear_form(self):
        """
        Clears all entry fields and resets the frame to its initial state.

        Resets form fields, buttons, and internal state variables to prepare
        for adding a new course or making a new selection.
        """
        self.name_entry.delete(0, tk.END)
        self.id_entry.config(state="normal")
        self.id_entry.delete(0, tk.END)
        self.instructor_combobox.set('')
        self.action_btn.config(text="Add Course", command=self.add_course)
        self.delete_btn.config(state="disabled")
        self.selected_course_id = None
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection())
        for item in self.students_tree.get_children(): self.students_tree.delete(item)
