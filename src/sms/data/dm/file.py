"""
Handles data serialization and deserialization to/from file formats.

This module provides the FileManager class, which is responsible for saving the
application's in-memory data (students, instructors, courses) to JSON or CSV
files, and loading data from those files back into memory.
"""
import csv
import json
import logging

from ...models.course import Course
from ...models.instructor import Instructor
from ...models.student import Student

logger = logging.getLogger(__name__)


class FileManager:
    """
    Manages saving and loading of application data to files.

    This class holds the application's data in dictionaries for efficient
    access and provides methods to serialize this data to JSON or CSV formats,
    and deserialize it back into memory.
    """

    def __init__(self, students: list[Student] = None, instructors: list[Instructor] = None,
                 courses: list[Course] = None):
        """
        Initializes the FileManager with optional initial data.

        :param students: An optional list of Student objects to start with.
        :type students: list[Student], optional
        :param instructors: An optional list of Instructor objects to start with.
        :type instructors: list[Instructor], optional
        :param courses: An optional list of Course objects to start with.
        :type courses: list[Course], optional
        """
        self.students: dict[str, Student] = {student.student_id: student for student in students} if students else {}
        self.instructors: dict[str, Instructor] = {instructor.instructor_id: instructor for instructor in
                                                   instructors} if instructors else {}
        self.courses: dict[str, Course] = {course.course_id: course for course in courses} if courses else {}

    def save_to_json(self, file_path: str):
        """
        Serializes the current data state to a single JSON file.

        :param file_path: The full path for the output JSON file.
        :type file_path: str
        """
        data = {"students": [s.to_dict() for s in self.students.values()],
                "instructors": [i.to_dict() for i in self.instructors.values()],
                "courses": [c.to_dict() for c in self.courses.values()]}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Data successfully saved to {file_path}")

    def load_from_json(self, file_path: str):
        """
        Loads and reconstructs data from a JSON file, overwriting current data.

        This method clears all existing data before loading from the file. It handles
        potential file not found and JSON decoding errors internally by logging them.

        :param file_path: The full path of the JSON file to load.
        :type file_path: str
        """
        self.students.clear()
        self.instructors.clear()
        self.courses.clear()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error(f"Error: The file {file_path} was not found for reading.")
            return
        except json.JSONDecodeError:
            logger.error(f"Error: The file {file_path} is not a valid JSON file.")
            return

        for i_data in data["instructors"]:
            instructor_id = i_data["instructor_id"]
            self.instructors[instructor_id] = Instructor(i_data["name"], i_data["age"], i_data["email"], instructor_id)

        for s_data in data["students"]:
            student_id = s_data["student_id"]
            self.students[student_id] = Student(s_data["name"], s_data["age"], s_data["email"], student_id)

        for c_data in data["courses"]:
            course_id = c_data["course_id"]
            instructor = self.instructors.get(c_data["instructor_id"])
            if instructor:
                self.courses[course_id] = Course(course_id, c_data["course_name"], instructor)

        # link courses to students
        for s_data in data["students"]:
            student = self.students[s_data["student_id"]]
            for course_id in s_data["registered_courses"]:
                course = self.courses.get(course_id)
                if course:
                    student.register_course(course)

        logger.info(f"Data successfully loaded from {file_path}")

    def save_to_csv(self, directory_path: str):
        """
        Serializes the current data state into multiple CSV files in a directory.

        Creates separate files for instructors, students, courses, and enrollments.

        :param directory_path: The path to the directory where CSV files will be saved.
        :type directory_path: str
        """
        # newline parameter needed for windows
        # open() converts \n to \r\n
        # CSV module handles newlines automatically
        # prevent double newline error

        with open(f"{directory_path}/instructors.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(Instructor.row())
            for i in self.instructors.values():
                writer.writerow(i.to_row())

        with open(f"{directory_path}/students.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(Student.row())
            for s in self.students.values():
                writer.writerow(s.to_row())

        with open(f"{directory_path}/courses.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(Course.row())
            for c in self.courses.values():
                writer.writerow(c.to_row())

        # link, like a database
        with open(f"{directory_path}/enrollments.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["student_id", "course_id"])
            for s in self.students.values():
                for c in s.registered_courses:
                    writer.writerow([s.student_id, c.course_id])

        logger.info(f"Data successfully saved to CSV files in {directory_path}")

    def load_from_csv(self, directory_path: str):
        """
        Loads and reconstructs data from CSV files in a directory, overwriting current data.

        This method expects specific filenames (e.g., instructors.csv, students.csv).
        It clears all existing data before loading and handles file not found errors
        internally by logging them.

        :param directory_path: The path to the directory containing the CSV files.
        :type directory_path: str
        """
        self.students.clear()
        self.instructors.clear()
        self.courses.clear()

        try:
            with open(f"{directory_path}/instructors.csv", 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.instructors[row["instructor_id"]] = Instructor(row["name"], int(row["age"]), row["email"],
                                                                        row["instructor_id"])

            with open(f"{directory_path}/students.csv", 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.students[row["student_id"]] = Student(row["name"], int(row["age"]), row["email"],
                                                               row["student_id"])

            with open(f"{directory_path}/courses.csv", 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    instructor = self.instructors.get(row["instructor_id"])
                    if instructor:
                        self.courses[row["course_id"]] = Course(row["course_id"], row["course_name"], instructor)

            with open(f"{directory_path}/enrollments.csv", 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    student = self.students.get(row["student_id"])
                    course = self.courses.get(row["course_id"])
                    if student and course:
                        student.register_course(course)
        except FileNotFoundError:
            logger.error(f"Error: Could not find one or more required CSV files in the directory '{directory_path}'.")

            self.students.clear()
            self.instructors.clear()
            self.courses.clear()

            return

        logger.info(f"Data successfully loaded from CSV files in {directory_path}")
