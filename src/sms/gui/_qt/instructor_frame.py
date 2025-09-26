"""
Instructor Management Frame.

This module contains the InstructorFrame class, a QWidget for the user interface
that manages instructors. It enables users to view, search, add, update, and
delete instructors, and to see the courses assigned to a selected instructor.

"""
from PyQt5.QtWidgets import (QWidget, QGridLayout, QGroupBox, QLabel, QLineEdit,
                             QPushButton, QTreeWidget, QTreeWidgetItem, QMessageBox,
                             QVBoxLayout, QHBoxLayout, QHeaderView)

from ...data.data_manager import DataError
from ...data.data_manager import data_manager as dm
from ...utils.validator import check_name, check_age, check_email_r, check_id


class InstructorFrame(QWidget):
    """
    A QWidget for displaying and managing instructor data.

    This frame provides all UI elements for instructor management, including
    searching, a list view of all instructors, a detail form for adding or
    editing instructor information, and a view for courses assigned to an
    instructor. It interfaces with the data_manager for all data operations.
    """
    def __init__(self, parent, controller):
        """
        Constructor for InstructorFrame.
        
        :param parent: The parent widget.
        :type parent: QWidget
        :param controller: The main application controller, used for status updates.
        :type controller: an object with an `update_status` method
        """
        super().__init__(parent)
        self.controller = controller
        self.selected_instructor_id = None

        main_layout = QVBoxLayout(self)

        search_group = QGroupBox("Search Instructors")
        search_layout = QHBoxLayout()
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)

        search_layout.addWidget(QLabel("Search by Name/ID:"))
        self.search_entry = QLineEdit()
        search_layout.addWidget(self.search_entry)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_instructors)
        search_layout.addWidget(self.search_button)
        self.clear_search_button = QPushButton("Clear")
        self.clear_search_button.clicked.connect(self.refresh_data)
        search_layout.addWidget(self.clear_search_button)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["Instructor ID", "Name", "Age", "Email"])
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.header().setStretchLastSection(True)
        main_layout.addWidget(self.tree)
        self.tree.itemSelectionChanged.connect(self.on_instructor_select)

        details_container_layout = QHBoxLayout()
        main_layout.addLayout(details_container_layout)

        details_group = QGroupBox("Instructor Details")
        details_layout = QGridLayout()
        details_group.setLayout(details_layout)
        details_container_layout.addWidget(details_group, 2)

        details_layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_entry = QLineEdit()
        details_layout.addWidget(self.name_entry, 0, 1)

        details_layout.addWidget(QLabel("Age:"), 1, 0)
        self.age_entry = QLineEdit()
        details_layout.addWidget(self.age_entry, 1, 1)

        details_layout.addWidget(QLabel("Email:"), 2, 0)
        self.email_entry = QLineEdit()
        details_layout.addWidget(self.email_entry, 2, 1)

        details_layout.addWidget(QLabel("Instructor ID:"), 3, 0)
        self.id_entry = QLineEdit()
        details_layout.addWidget(self.id_entry, 3, 1)

        button_layout = QHBoxLayout()
        details_layout.addLayout(button_layout, 4, 0, 1, 2)
        button_layout.addStretch()
        self.action_btn = QPushButton("Add Instructor")
        self.action_btn.clicked.connect(self.add_instructor)
        button_layout.addWidget(self.action_btn)
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_instructor)
        button_layout.addWidget(self.delete_btn)
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)

        courses_group = QGroupBox("Assigned Courses")
        courses_layout = QVBoxLayout()
        courses_group.setLayout(courses_layout)
        details_container_layout.addWidget(courses_group, 1)

        self.courses_tree = QTreeWidget()
        self.courses_tree.setColumnCount(2)
        self.courses_tree.setHeaderLabels(["ID", "Course Name"])
        self.courses_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.courses_tree.header().setStretchLastSection(True)
        courses_layout.addWidget(self.courses_tree)

    def refresh_data(self, _=None, instructor_list=None):
        """
        Refreshes all data views in the frame.

        Clears and repopulates the instructor tree. If an `instructor_list`
        is provided (e.g., from a search), it displays that list. Otherwise,
        it fetches all instructors from the data manager.

        :param instructor_list: An optional list of Instructor objects to display.
        :type instructor_list: list, optional
        """
        if instructor_list is None:
            self.search_entry.clear()

        self.tree.clear()
        instructors_to_display = instructor_list if instructor_list is not None else dm.get_instructors()

        for instructor in instructors_to_display:
            item = QTreeWidgetItem([str(val) for val in instructor.to_row(by_id=True)])
            self.tree.addTopLevelItem(item)
        self.clear_form()

    def search_instructors(self):
        """
        Filters the instructor tree based on the search query.

        The search is case-insensitive and matches against instructor name and ID.
        If the search query is empty, the full instructor list is restored.
        """
        query = self.search_entry.text().strip().lower()
        if not query:
            self.refresh_data()
            return
        all_instructors = dm.get_instructors()
        filtered = [inst for inst in all_instructors if query in inst.name.lower() or query in inst.instructor_id]
        if not filtered:
            QMessageBox.information(self, "No Results", "No instructors found.")
        self.refresh_data(instructor_list=filtered)
        self.controller.update_status(f"Found {len(filtered)} instructors matching '{query}'.")

    def on_instructor_select(self):
        """
        Handles the event of an instructor being selected in the tree.

        Populates the detail form with the selected instructor's data and
        switches the form to "edit mode". It also updates the assigned
        courses view.
        """
        selected_items = self.tree.selectedItems()
        if not selected_items: return
        item = selected_items[0]
        inst_id, name, age, email = [item.text(i) for i in range(4)]
        self.clear_form()
        self.name_entry.setText(name)
        self.age_entry.setText(age)
        self.email_entry.setText(email)
        self.id_entry.setText(inst_id)
        self.id_entry.setEnabled(False)
        self.action_btn.setText("Save Changes")
        self.action_btn.clicked.disconnect()
        self.action_btn.clicked.connect(self.save_changes)
        self.delete_btn.setEnabled(True)
        self.selected_instructor_id = inst_id
        self.update_assigned_courses_view()

    def update_assigned_courses_view(self):
        """
        Populates the assigned courses tree for the selected instructor.
        """
        self.courses_tree.clear()
        if self.selected_instructor_id:
            instructor = dm.get_instructor(self.selected_instructor_id)
            if instructor:
                for course in sorted(instructor.assigned_courses, key=lambda c: c.course_id):
                    item = QTreeWidgetItem([course.course_id, course.course_name])
                    self.courses_tree.addTopLevelItem(item)

    def add_instructor(self):
        """
        Handles adding a new instructor.

        Validates form input and calls the data manager to add the instructor.
        Displays appropriate success or error messages.
        """
        name = self.name_entry.text().strip()
        age = self.age_entry.text().strip()
        email = self.email_entry.text().strip()
        instructor_id = self.id_entry.text().strip()

        if not all([name, age, email, instructor_id]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        if not check_name(name):
            QMessageBox.critical(self, "Error Adding Instructor!", "Invalid Name.")
            return

        try:
            age_val = int(age)
        except ValueError:
            QMessageBox.critical(self, "Error Adding Instructor!", "Age must be a number.")
            return

        if not check_age(age_val):
            QMessageBox.critical(self, "Error Adding Instructor!", "Invalid Age.")
            return

        if not (em := check_email_r(email))[0]:
            msg = "Invalid Email Address" + (f": {em[1]}" if em[1] else ".")
            QMessageBox.critical(self, "Error Adding Instructor!", msg)
            return

        if not check_id(instructor_id):
            QMessageBox.critical(self, "Error Adding Instructor!", "Invalid Instructor ID.")
            return

        try:
            dm.add_instructor(name=name, age=age_val, email=email, instructor_id=instructor_id)
        except DataError as e:
            QMessageBox.critical(self, "Database Error Adding Instructor", str(e))
            return

        QMessageBox.information(self, "Success", f"Instructor with ID '{instructor_id}' added successfully.")
        self.controller.update_status(f"Instructor {name} added.")
        self.refresh_data()

    def save_changes(self):
        """
        Handles saving changes to an existing instructor.

        Validates form input and calls the data manager to update the instructor.
        Displays appropriate success or error messages.
        """
        if not self.selected_instructor_id: return
        name = self.name_entry.text().strip()
        age = self.age_entry.text().strip()
        email = self.email_entry.text().strip()

        if not all([name, age, email]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        if not check_name(name):
            QMessageBox.critical(self, "Error Updating Instructor!", "Invalid Name.")
            return

        try:
            age_val = int(age)
        except ValueError:
            QMessageBox.critical(self, "Error Updating Instructor!", "Age must be a number.")
            return

        if not check_age(age_val):
            QMessageBox.critical(self, "Error Updating Instructor!", "Invalid Age.")
            return

        if not (em := check_email_r(email))[0]:
            msg = "Invalid Email Address" + (f": {em[1]}" if em[1] else ".")
            QMessageBox.critical(self, "Error Updating Instructor!", msg)
            return

        try:
            dm.edit_instructor(instructor_id=self.selected_instructor_id, name=name, age=age_val, email=email)
        except DataError as e:
            QMessageBox.critical(self, "Database Error Updating Instructor!", str(e))
            return

        QMessageBox.information(self, "Success",
                                f"Instructor with ID '{self.selected_instructor_id}' updated successfully.")
        self.controller.update_status(f"Instructor {name} updated.")
        self.refresh_data()

    def delete_instructor(self):
        """
        Handles deleting the selected instructor.

        Shows a confirmation dialog before calling the data manager to remove
        the instructor. Displays appropriate success or error messages.
        """
        if not self.selected_instructor_id: return
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this instructor?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                dm.remove_instructor(self.selected_instructor_id)
            except DataError as e:
                QMessageBox.critical(self, "Database Error Deleting Instructor!", str(e))
                return
            self.controller.update_status(f"Instructor {self.selected_instructor_id} deleted successfully.")
            QMessageBox.information(self, "Success", "Instructor deleted.")
            self.refresh_data()

    def clear_form(self):
        """
        Resets the detail form to its default, empty state.

        Clears all input fields, resets the action button to "Add Instructor",
        disables the delete button, and clears any selections in the trees.
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
        self.action_btn.setText("Add Instructor")
        self.action_btn.clicked.connect(self.add_instructor)

        self.delete_btn.setEnabled(False)
        self.selected_instructor_id = None
        self.tree.clearSelection()
        self.courses_tree.clear()
