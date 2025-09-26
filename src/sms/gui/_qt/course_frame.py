"""
Course Management Frame.

This module contains the CourseFrame class, a QWidget that provides the user
interface for managing courses within the application. It allows users to view,
search, add, update, and delete courses. It also displays the list of students
enrolled in a selected course.

"""
from PyQt5.QtWidgets import (QWidget, QGridLayout, QGroupBox, QLabel, QLineEdit,
                             QPushButton, QTreeWidget, QTreeWidgetItem, QComboBox,
                             QMessageBox, QVBoxLayout, QHBoxLayout, QHeaderView)

from ...data.data_manager import DataError
from ...data.data_manager import data_manager as dm
from ...utils.validator import check_course_name, check_course_id


class CourseFrame(QWidget):
    """
    A QWidget for displaying and managing course data.

    This frame includes widgets for searching courses, displaying a list of
    courses in a tree view, editing course details (name, ID, instructor),
    and viewing students enrolled in a selected course. It handles all user
    interactions for course management and communicates with the central
    data_manager.
    """

    def __init__(self, parent, controller):
        """
        Constructor for CourseFrame.
        
        :param parent: The parent widget.
        :type parent: QWidget
        :param controller: The main controller object for the application, used for
                       updating the status bar.
        :type controller: an object with an `update_status` method
        """
        super().__init__(parent)
        self.controller = controller
        self.selected_course_id = None
        self.instructor_map = {}

        main_layout = QVBoxLayout(self)

        search_group = QGroupBox("Search Courses")
        search_layout = QHBoxLayout()
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)

        search_layout.addWidget(QLabel("Search by Name/ID:"))
        self.search_entry = QLineEdit()
        search_layout.addWidget(self.search_entry)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_courses)
        search_layout.addWidget(self.search_button)
        self.clear_search_button = QPushButton("Clear")
        self.clear_search_button.clicked.connect(self.refresh_data)
        search_layout.addWidget(self.clear_search_button)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Course ID", "Course Name", "Instructor ID"])
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.header().setStretchLastSection(False)
        main_layout.addWidget(self.tree)
        self.tree.itemSelectionChanged.connect(self.on_course_select)

        details_container_layout = QHBoxLayout()
        main_layout.addLayout(details_container_layout)

        details_group = QGroupBox("Course Details")
        details_layout = QGridLayout()
        details_group.setLayout(details_layout)
        details_container_layout.addWidget(details_group, 2)

        details_layout.addWidget(QLabel("Course Name:"), 0, 0)
        self.name_entry = QLineEdit()
        details_layout.addWidget(self.name_entry, 0, 1)

        details_layout.addWidget(QLabel("Course ID:"), 1, 0)
        self.id_entry = QLineEdit()
        details_layout.addWidget(self.id_entry, 1, 1)

        details_layout.addWidget(QLabel("Instructor:"), 2, 0)
        self.instructor_combobox = QComboBox()
        details_layout.addWidget(self.instructor_combobox, 2, 1)

        button_layout = QHBoxLayout()
        details_layout.addLayout(button_layout, 3, 0, 1, 2)
        button_layout.addStretch()
        self.action_btn = QPushButton("Add Course")
        self.action_btn.clicked.connect(self.add_course)
        button_layout.addWidget(self.action_btn)
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_course)
        button_layout.addWidget(self.delete_btn)
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)

        students_group = QGroupBox("Enrolled Students")
        students_layout = QVBoxLayout()
        students_group.setLayout(students_layout)
        details_container_layout.addWidget(students_group, 1)

        self.students_tree = QTreeWidget()
        self.students_tree.setColumnCount(2)
        self.students_tree.setHeaderLabels(["ID", "Student Name"])
        self.students_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.students_tree.header().setStretchLastSection(True)
        students_layout.addWidget(self.students_tree)

    def refresh_data(self, _=None, course_list=None):
        """
        Refreshes all data views in the frame.

        Clears and repopulates the course tree and the instructor dropdown.
        If a `course_list` is provided, it populates the tree with that list.
        Otherwise, it fetches all courses from the data manager. Also clears
        the search bar if no specific list is provided.

        :param course_list: An optional list of Course objects to display.
        :type course_list: list, optional
        """
        if course_list is None:
            self.search_entry.clear()

        self.tree.clear()
        courses_to_display = course_list if course_list is not None else dm.get_courses()

        for course in courses_to_display:
            item = QTreeWidgetItem([str(val) for val in course.to_row()])
            self.tree.addTopLevelItem(item)

        self.instructor_combobox.clear()
        self.instructor_map = {f"{inst.name} ({inst.instructor_id})": inst for inst in dm.get_instructors()}
        self.instructor_combobox.addItems(["", *self.instructor_map.keys()])
        self.clear_form()

    def search_courses(self):
        """
        Filters the course tree based on the text in the search entry.
        """
        query = self.search_entry.text().strip().lower()
        if not query:
            self.refresh_data()
            return
        all_courses = dm.get_courses()
        filtered = [c for c in all_courses if query in c.course_name.lower() or query in c.course_id.lower()]
        if not filtered:
            QMessageBox.information(self, "No Results", "No courses found.")
        self.refresh_data(course_list=filtered)
        self.controller.update_status(f"Found {len(filtered)} courses matching '{query}'.")

    def on_course_select(self):
        """
        Handles the event when a user selects a course in the tree.

        Populates the detail form fields with the selected course's data.
        Updates the UI to "edit mode" by disabling the ID field, enabling the
        delete button, and changing the action button to "Save Changes". 
        """
        selected_items = self.tree.selectedItems()
        if not selected_items: return
        item = selected_items[0]
        course_id, name, instructor_id = [item.text(i) for i in range(3)]

        self.clear_form()
        self.name_entry.setText(name)
        self.id_entry.setText(course_id)

        for display_text, instructor_obj in self.instructor_map.items():
            if instructor_obj.instructor_id == instructor_id:
                self.instructor_combobox.setCurrentText(display_text)
                break

        self.id_entry.setEnabled(False)
        self.action_btn.setText("Save Changes")
        self.action_btn.clicked.disconnect()
        self.action_btn.clicked.connect(self.save_changes)
        self.delete_btn.setEnabled(True)
        self.selected_course_id = course_id
        self.update_enrolled_students_view()

    def update_enrolled_students_view(self):
        """
        Populates the enrolled students tree for the currently selected course.
        """
        self.students_tree.clear()
        if self.selected_course_id:
            course = dm.get_course(self.selected_course_id)
            if course:
                for student in sorted(course.enrolled_students, key=lambda s: s.name):
                    item = QTreeWidgetItem([student.student_id, student.name])
                    self.students_tree.addTopLevelItem(item)

    def add_course(self):
        """
        Handles adding a new course to the system.

        Retrieves data from the form, validates it, and then calls the
        data manager to add the course. Displays success or error messages.
        """
        course_name = self.name_entry.text().strip()
        course_id = self.id_entry.text().strip()
        selected_instructor_str = self.instructor_combobox.currentText()

        if not all([course_name, course_id, selected_instructor_str]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        instructor = self.instructor_map.get(selected_instructor_str)

        if not check_course_name(course_name):
            QMessageBox.critical(self, "Error Adding Course!", "Invalid Course Name.")
            return

        if not check_course_id(course_id):
            QMessageBox.critical(self, "Error Adding Course!", "Invalid Course ID.")
            return

        try:
            dm.add_course(course_name=course_name, course_id=course_id, instructor=instructor)
        except DataError as e:
            QMessageBox.critical(self, "Database Error Adding Course!", str(e))
            return

        QMessageBox.information(self, "Success", f"Course with ID '{course_id}' added successfully.")
        self.controller.update_status(f"Course {course_name} added.")
        self.refresh_data()

    def save_changes(self):
        """
        Handles saving changes to an existing, selected course.

        Retrieves updated data from the form, validates it, and calls the data
        manager to update the course. Displays success or error messages.
        """
        if not self.selected_course_id: return
        course_name = self.name_entry.text().strip()
        instructor_str = self.instructor_combobox.currentText()

        if not all([course_name, instructor_str]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        if not check_course_name(course_name):
            QMessageBox.critical(self, "Error Updating Course!", "Invalid Name.")
            return

        instructor = self.instructor_map.get(instructor_str)
        try:
            dm.edit_course(course_id=self.selected_course_id, course_name=course_name, instructor=instructor)
        except DataError as e:
            QMessageBox.critical(self, "Database Error Updating Course!", str(e))
            return

        QMessageBox.information(self, "Success", f"Course with ID '{self.selected_course_id}' updated successfully.")
        self.controller.update_status(f"Course {course_name} updated.")
        self.refresh_data()

    def delete_course(self):
        """
        Handles deletion of the currently selected course.

        Shows a confirmation dialog to the user before proceeding. If confirmed,
        it calls the data manager to remove the course. Displays success or
        error messages.
        """
        if not self.selected_course_id: return
        msg = "This will unregister all students from this course. Are you sure?"
        reply = QMessageBox.question(self, "Confirm Delete", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                dm.remove_course(self.selected_course_id)
            except DataError as e:
                QMessageBox.critical(self, "Database Error Deleting Course!", str(e))
                return
            self.controller.update_status(f"Course {self.selected_course_id} deleted successfully.")
            QMessageBox.information(self, "Success", "Course deleted.")
            self.refresh_data()

    def clear_form(self):
        """
        Resets the detail form to its default state.

        Clears all input fields, resets the action button to "Add Course",
        disables the delete button, and clears any selection.
        """
        self.name_entry.clear()
        self.id_entry.setEnabled(True)
        self.id_entry.clear()
        self.instructor_combobox.setCurrentIndex(0)

        try:
            self.action_btn.clicked.disconnect()
        except TypeError:
            pass
        self.action_btn.setText("Add Course")
        self.action_btn.clicked.connect(self.add_course)

        self.delete_btn.setEnabled(False)
        self.selected_course_id = None
        self.tree.clearSelection()
        self.students_tree.clear()
