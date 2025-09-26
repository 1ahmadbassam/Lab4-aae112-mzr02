"""
Student Management Frame.

This module contains the StudentFrame class, a QWidget that provides the UI
for managing students. It allows for viewing, searching, adding, updating,
and deleting students, as well as registering them for courses.

"""
from PyQt5.QtWidgets import (QWidget, QGridLayout, QGroupBox, QLabel, QLineEdit,
                             QPushButton, QTreeWidget, QTreeWidgetItem, QComboBox,
                             QMessageBox, QVBoxLayout, QHBoxLayout, QHeaderView)

from ...data.data_manager import DataError
from ...data.data_manager import data_manager as dm
from ...models.student import Student
from ...utils.validator import check_name, check_age, check_email_r, check_id


class StudentFrame(QWidget):
    """
    A QWidget for displaying and managing student data.

    This frame contains all necessary widgets for student operations, including
    a searchable list, a detail form for editing information, and functionality
    for course registration. It interacts with the data_manager to perform
    backend data manipulations.
    """
    def __init__(self, parent, controller):
        """
        Constructor for StudentFrame.
        
        :param parent: The parent widget.
        :type parent: QWidget
        :param controller: The main application controller for status updates.
        :type controller: an object with an `update_status` method
        """
        super().__init__(parent)
        self.controller = controller
        self.selected_student_id = None
        self.course_map = {}

        main_layout = QVBoxLayout(self)

        search_group = QGroupBox("Search Students")
        search_layout = QHBoxLayout()
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)

        search_layout.addWidget(QLabel("Search by Name/ID:"))
        self.search_entry = QLineEdit()
        search_layout.addWidget(self.search_entry)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_students)
        search_layout.addWidget(self.search_button)
        self.clear_search_button = QPushButton("Clear")
        self.clear_search_button.clicked.connect(self.refresh_data)
        search_layout.addWidget(self.clear_search_button)

        columns = (*Student.row(by_id=True),)
        self.tree = QTreeWidget()
        self.tree.setColumnCount(len(columns))
        self.tree.setHeaderLabels(["Student ID", "Name", "Age", "Email"])
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.header().setStretchLastSection(True)
        main_layout.addWidget(self.tree)
        self.tree.itemSelectionChanged.connect(self.on_student_select)

        details_container_layout = QHBoxLayout()
        main_layout.addLayout(details_container_layout)

        details_group = QGroupBox("Student Details")
        details_layout = QGridLayout()
        details_group.setLayout(details_layout)
        details_container_layout.addWidget(details_group, 2)

        details_layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_entry = QLineEdit()
        details_layout.addWidget(self.name_entry, 0, 1, 1, 3)

        details_layout.addWidget(QLabel("Age:"), 1, 0)
        self.age_entry = QLineEdit()
        details_layout.addWidget(self.age_entry, 1, 1, 1, 3)

        details_layout.addWidget(QLabel("Email:"), 2, 0)
        self.email_entry = QLineEdit()
        details_layout.addWidget(self.email_entry, 2, 1, 1, 3)

        details_layout.addWidget(QLabel("Student ID:"), 3, 0)
        self.id_entry = QLineEdit()
        details_layout.addWidget(self.id_entry, 3, 1, 1, 3)

        details_layout.addWidget(QLabel("Register for Course:"), 4, 0)
        self.course_combobox = QComboBox()
        self.course_combobox.setEnabled(False)
        details_layout.addWidget(self.course_combobox, 4, 1, 1, 2)

        self.register_btn = QPushButton("Register")
        self.register_btn.setEnabled(False)
        self.register_btn.clicked.connect(self.register_for_course)
        details_layout.addWidget(self.register_btn, 4, 3)

        button_layout = QHBoxLayout()
        details_layout.addLayout(button_layout, 5, 0, 1, 4)
        button_layout.addStretch()
        self.action_btn = QPushButton("Add Student")
        self.action_btn.clicked.connect(self.add_student)
        button_layout.addWidget(self.action_btn)
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_student)
        button_layout.addWidget(self.delete_btn)
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)

        courses_group = QGroupBox("Registered Courses")
        courses_layout = QVBoxLayout()
        courses_group.setLayout(courses_layout)
        details_container_layout.addWidget(courses_group, 1)

        self.courses_tree = QTreeWidget()
        self.courses_tree.setColumnCount(2)
        self.courses_tree.setHeaderLabels(["ID", "Course Name"])
        self.courses_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.courses_tree.header().setStretchLastSection(True)
        courses_layout.addWidget(self.courses_tree)

    def refresh_data(self, _=None, student_list=None):
        """
        Refreshes all data views in the frame.

        Populates the student tree and the course registration dropdown.
        If a `student_list` is provided (e.g., from a search), it uses
        that list; otherwise, it fetches all students.

        :param student_list: An optional list of Student objects to display.
        :type student_list: list, optional
        """
        if student_list is None:
            self.search_entry.clear()
        self.tree.clear()
        students_to_display = student_list if student_list is not None else dm.get_students()

        for student in students_to_display:
            item = QTreeWidgetItem([str(val) for val in student.to_row(by_id=True)])
            self.tree.addTopLevelItem(item)

        self.course_combobox.clear()
        self.course_map = {f"{c.course_name} ({c.course_id})": c for c in dm.get_courses()}
        self.course_combobox.addItems(["", *self.course_map.keys()])
        self.clear_form()

    def search_students(self):
        """
        Filters the student tree based on the search query.

        The search is case-insensitive and matches against student name and ID.
        """
        query = self.search_entry.text().strip().lower()
        if not query:
            self.refresh_data()
            return
        all_students = dm.get_students()
        filtered = [s for s in all_students if query in s.name.lower() or query in s.student_id]
        if not filtered:
            QMessageBox.information(self, "No Results", "No students found matching search query.")
        self.refresh_data(student_list=filtered)
        self.controller.update_status(f"Found {len(filtered)} students matching '{query}'.")

    def on_student_select(self):
        """
        Handles the event of a student being selected in the tree.

        Populates the detail form with student data, switches to "edit mode",
        and updates the registered courses view.
        """
        selected_items = self.tree.selectedItems()
        if not selected_items: return
        item = selected_items[0]
        student_id, name, age, email = [item.text(i) for i in range(4)]
        self.clear_form()
        self.name_entry.setText(name)
        self.age_entry.setText(age)
        self.email_entry.setText(email)
        self.id_entry.setText(student_id)
        self.id_entry.setEnabled(False)
        self.action_btn.setText("Save Changes")
        self.action_btn.clicked.disconnect()
        self.action_btn.clicked.connect(self.save_changes)
        self.delete_btn.setEnabled(True)
        self.course_combobox.setEnabled(True)
        self.register_btn.setEnabled(True)
        self.selected_student_id = student_id
        self.update_registered_courses_view()

    def update_registered_courses_view(self):
        """
        Populates the registered courses tree for the selected student.
        """
        self.courses_tree.clear()
        if self.selected_student_id:
            student = dm.get_student(self.selected_student_id)
            if student:
                for course in sorted(student.registered_courses, key=lambda c: c.course_id):
                    item = QTreeWidgetItem([course.course_id, course.course_name])
                    self.courses_tree.addTopLevelItem(item)

    def add_student(self):
        """
        Handles adding a new student to the system.

        Validates form data and calls the data manager to add the student.
        """
        name = self.name_entry.text().strip()
        age = self.age_entry.text().strip()
        email = self.email_entry.text().strip()
        student_id = self.id_entry.text().strip()

        if not all([name, age, email, student_id]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        if not check_name(name):
            QMessageBox.critical(self, "Error Adding Student!", "Invalid Name.")
            return

        try:
            age_val = int(age)
        except ValueError:
            QMessageBox.critical(self, "Error Adding Student!", "Age must be a number.")
            return

        if not check_age(age_val):
            QMessageBox.critical(self, "Error Adding Student!", "Invalid Age.")
            return

        if not (em := check_email_r(email))[0]:
            msg = "Invalid Email Address" + (f": {em[1]}" if em[1] else ".")
            QMessageBox.critical(self, "Error Adding Student!", msg)
            return

        if not check_id(student_id):
            QMessageBox.critical(self, "Error Adding Student!", "Invalid Student ID.")
            return

        try:
            dm.add_student(name=name, age=age_val, email=email, student_id=student_id)
        except DataError as e:
            QMessageBox.critical(self, "Database Error Adding Student!", str(e))
            return

        QMessageBox.information(self, "Success", f"Student with ID '{student_id}' added successfully.")
        self.controller.update_status(f"Student {name} added.")
        self.refresh_data()

    def save_changes(self):
        """
        Handles saving changes to an existing student.

        Validates form data and calls the data manager to update the student.
        """
        if not self.selected_student_id: return
        name = self.name_entry.text().strip()
        age = self.age_entry.text().strip()
        email = self.email_entry.text().strip()

        if not all([name, age, email]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        if not check_name(name):
            QMessageBox.critical(self, "Error Updating Student!", "Invalid Name.")
            return

        try:
            age_val = int(age)
        except ValueError:
            QMessageBox.critical(self, "Error Updating Student!", "Age must be a number.")
            return

        if not check_age(age_val):
            QMessageBox.critical(self, "Error Updating Student!", "Invalid Age.")
            return

        if not (em := check_email_r(email))[0]:
            msg = "Invalid Email Address" + (f": {em[1]}" if em[1] else ".")
            QMessageBox.critical(self, "Error Updating Student!", msg)
            return

        try:
            dm.edit_student(name=name, age=age_val, email=email, student_id=self.selected_student_id)
        except DataError as e:
            QMessageBox.critical(self, "Database Error Updating Student!", str(e))
            return

        QMessageBox.information(self, "Success", f"Student with ID '{self.selected_student_id}' updated successfully.")
        self.controller.update_status(f"Student {name} updated.")
        self.refresh_data()

    def delete_student(self):
        """
        Handles deleting the selected student.

        Displays a confirmation dialog before calling the data manager.
        """
        if not self.selected_student_id: return
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this student?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                dm.remove_student(self.selected_student_id)
            except DataError as e:
                QMessageBox.critical(self, "Database Error Deleting Student!", str(e))
                return
            self.controller.update_status(f"Student {self.selected_student_id} deleted successfully.")
            QMessageBox.information(self, "Success", "Student deleted.")
            self.refresh_data()

    def register_for_course(self):
        """
        Registers the selected student for the selected course.
        """
        if not self.selected_student_id:
            QMessageBox.warning(self, "Selection Error", "Please select a student first.")
            return
        selected_course_str = self.course_combobox.currentText()
        if not selected_course_str:
            QMessageBox.warning(self, "Selection Error", "Please select a course to register.")
            return

        student = dm.get_student(self.selected_student_id)
        course = self.course_map.get(selected_course_str)

        if course.course_id in {c.course_id for c in student.registered_courses}:
            QMessageBox.warning(self, "Registration Error", f"{student.name} is already registered for this course.")
            return

        dm.enroll_student(student.student_id, course.course_id)
        self.controller.update_status(f"Registered {student.name} for {course.course_name}.")
        QMessageBox.information(self, "Success", "Student registered successfully.")
        self.course_combobox.setCurrentIndex(0)
        self.update_registered_courses_view()

    def clear_form(self):
        """
        Resets the detail form to its default, empty state.
        """
        self.name_entry.clear()
        self.age_entry.clear()
        self.email_entry.clear()
        self.id_entry.setEnabled(True)
        self.id_entry.clear()

        try:
            self.action_btn.clicked.disconnect()
        except TypeError:
            pass
        self.action_btn.setText("Add Student")
        self.action_btn.clicked.connect(self.add_student)

        self.delete_btn.setEnabled(False)
        self.course_combobox.setEnabled(False)
        self.register_btn.setEnabled(False)
        self.course_combobox.setCurrentIndex(0)

        self.selected_student_id = None
        self.tree.clearSelection()
        self.courses_tree.clear()
