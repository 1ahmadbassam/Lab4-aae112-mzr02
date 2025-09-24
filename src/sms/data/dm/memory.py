"""
Provides an in-memory implementation of the data management interface.

This module contains the `MemoryDataManager` class, which uses a singleton
`FileManager` instance as a global in-memory datastore. It handles all
CRUD operations by directly manipulating Python objects in memory.
"""
from .file import FileManager
from .interface import BaseDataManager, DataError
from ...models.course import Course
from ...models.instructor import Instructor
from ...models.student import Student

datastore = FileManager()
"""The global, in-memory data store for the application."""


class MemoryDataManager(BaseDataManager):
    """
    Implements the BaseDataManager interface for in-memory data storage.

    All methods are static and operate on the module-level `datastore` object,
    providing a concrete way to manage data while the application is running.
    """

    @staticmethod
    def add_student(**kwargs) -> None:
        """
        Adds a new student to the in-memory datastore.

        :param kwargs: Keyword arguments representing student attributes.
        :raises DataError: If student data is invalid or a student with the same ID already exists.
        """
        try:
            s = Student(**kwargs)
        except ValueError as e:
            raise DataError(e)
        if s.student_id in datastore.students:
            raise DataError(f"Student with ID '{s.student_id}' already exists.")
        datastore.students[s.student_id] = s

    @staticmethod
    def edit_student(**kwargs) -> None:
        """
        Edits an existing student's information in memory.

        Requires 'student_id' in kwargs to identify the student.

        :param kwargs: Keyword arguments with fields to update.
        :raises DataError: If the student ID is missing or the student is not found.
        """
        student_id = kwargs.get('student_id')
        if not student_id:
            raise DataError("Student ID is required.")

        if student_id not in datastore.students:
            raise DataError(f"Student with ID '{student_id}' not found.")

        try:
            datastore.students[student_id].update(**kwargs)
        except ValueError as e:
            raise DataError(e)

    @staticmethod
    def remove_student(student_id: str) -> None:
        """
        Removes a student from the in-memory datastore.

        :param student_id: The ID of the student to remove.
        :type student_id: str
        :raises DataError: If the student is not found.
        """
        if not datastore.students.get(student_id):
            raise DataError(f"Student with ID '{student_id}' does not exist.")
        del datastore.students[student_id]

    @staticmethod
    def get_student(student_id: str) -> Student:
        """
        Retrieves a single student object from memory.

        :param student_id: The ID of the student to retrieve.
        :type student_id: str
        :return: The corresponding Student object.
        :rtype: Student
        :raises DataError: If the student is not found.
        """
        s = datastore.students.get(student_id)
        if not s:
            raise DataError(f"Student with ID '{student_id}' not found.")
        return s

    @staticmethod
    def get_students() -> list[Student]:
        """
        Retrieves a list of all student objects from memory.

        :return: A list of all students.
        :rtype: list[Student]
        """
        return list(datastore.students.values())

    @staticmethod
    def add_instructor(**kwargs) -> None:
        """
        Adds a new instructor to the in-memory datastore.

        :param kwargs: Keyword arguments representing instructor attributes.
        :raises DataError: If instructor data is invalid or an instructor with the same ID already exists.
        """
        try:
            i = Instructor(**kwargs)
        except ValueError as e:
            raise DataError(e)
        if i.instructor_id in datastore.instructors:
            raise DataError(f"Instructor with ID '{i.instructor_id}' already exists.")
        datastore.instructors[i.instructor_id] = i

    @staticmethod
    def edit_instructor(**kwargs) -> None:
        """
        Edits an existing instructor's information in memory.

        Requires 'instructor_id' in kwargs to identify the instructor.

        :param kwargs: Keyword arguments with fields to update.
        :raises DataError: If the instructor ID is missing or the instructor is not found.
        """
        instructor_id = kwargs.get('instructor_id')
        if not instructor_id:
            raise DataError("Instructor ID is required.")

        if instructor_id not in datastore.instructors:
            raise DataError(f"Instructor with ID '{instructor_id}' not found.")

        try:
            datastore.instructors[instructor_id].update(**kwargs)
        except ValueError as e:
            raise DataError(e)

    @staticmethod
    def remove_instructor(instructor_id: str) -> None:
        """
        Removes an instructor from the in-memory datastore.

        :param instructor_id: The ID of the instructor to remove.
        :type instructor_id: str
        :raises DataError: If the instructor is not found.
        """
        if not datastore.instructors.get(instructor_id):
            raise DataError(f"Instructor with ID '{instructor_id}' does not exist.")
        del datastore.instructors[instructor_id]

    @staticmethod
    def get_instructor(instructor_id: str) -> Instructor:
        """
        Retrieves a single instructor object from memory.

        :param instructor_id: The ID of the instructor to retrieve.
        :type instructor_id: str
        :return: The corresponding Instructor object.
        :rtype: Instructor
        :raises DataError: If the instructor is not found.
        """
        i = datastore.instructors.get(instructor_id)
        if not i:
            raise DataError(f"Instructor with ID '{instructor_id}' not found.")
        return i

    @staticmethod
    def get_instructors() -> list[Instructor]:
        """
        Retrieves a list of all instructor objects from memory.

        :return: A list of all instructors.
        :rtype: list[Instructor]
        """
        return list(datastore.instructors.values())

    @staticmethod
    def add_course(**kwargs) -> None:
        """
        Adds a new course to the in-memory datastore.

        :param kwargs: Keyword arguments representing course attributes.
        :raises DataError: If course data is invalid or a course with the same ID already exists.
        """
        try:
            c = Course(**kwargs)
        except ValueError as e:
            raise DataError(e)
        if c.course_id in datastore.courses:
            raise DataError(f"Course with ID '{c.course_id}' already exists.")
        datastore.courses[c.course_id] = c

    @staticmethod
    def edit_course(**kwargs) -> None:
        """
        Edits an existing course's information in memory.

        Requires 'course_id' in kwargs to identify the course.

        :param kwargs: Keyword arguments with fields to update.
        :raises DataError: If the course ID is missing or the course is not found.
        """
        course_id = kwargs.get('course_id')
        if not course_id:
            raise DataError("Course ID is required.")

        if course_id not in datastore.courses:
            raise DataError(f"Course with ID '{course_id}' not found.")

        try:
            datastore.courses[course_id].update(**kwargs)
        except ValueError as e:
            raise DataError(e)

    @staticmethod
    def remove_course(course_id: str) -> None:
        """
        Removes a course and all its associations from the in-memory datastore.

        This also de-registers the course from its assigned instructor and all
        enrolled students.

        :param course_id: The ID of the course to remove.
        :type course_id: str
        :raises DataError: If the course is not found.
        """
        if not datastore.courses.get(course_id):
            raise DataError(f"Course with ID '{course_id}' does not exist.")
        c = datastore.courses[course_id]
        c.instructor.assigned_courses.remove(c)
        for student in c.enrolled_students:
            student.registered_courses.remove(c)
        del datastore.courses[course_id]

    @staticmethod
    def get_course(course_id: str) -> Course:
        """
        Retrieves a single course object from memory.

        :param course_id: The ID of the course to retrieve.
        :type course_id: str
        :return: The corresponding Course object.
        :rtype: Course
        :raises DataError: If the course is not found.
        """
        c = datastore.courses.get(course_id)
        if not c:
            raise DataError(f"Course with ID '{course_id}' not found.")
        return c

    @staticmethod
    def get_courses() -> list[Course]:
        """
        Retrieves a list of all course objects from memory.

        :return: A list of all courses.
        :rtype: list[Course]
        """
        return list(datastore.courses.values())

    @staticmethod
    def enroll_student(student_id: str, course_id: str) -> None:
        """
        Enrolls a student in a course in memory.

        :param student_id: The ID of the student to enroll.
        :type student_id: str
        :param course_id: The ID of the course to enroll in.
        :type course_id: str
        :raises DataError: If the student or course is not found.
        """
        s = datastore.students.get(student_id)
        if not s:
            raise DataError(f"Student with ID '{student_id}' not found.")
        c = datastore.courses.get(course_id)
        if not c:
            raise DataError(f"Course with ID '{course_id}' not found.")
        s.register_course(c)

    @staticmethod
    def data_to_json(filepath: str) -> None:
        """
        Delegates saving all in-memory data to a JSON file.

        :param filepath: The path to the output JSON file.
        :type filepath: str
        """
        datastore.save_to_json(filepath)

    @staticmethod
    def data_from_json(filepath: str) -> None:
        """
        Delegates loading all data from a JSON file into memory.

        :param filepath: The path to the input JSON file.
        :type filepath: str
        """
        datastore.load_from_json(filepath)

    @staticmethod
    def data_to_csv(dirpath: str) -> None:
        """
        Delegates saving all in-memory data to CSV files.

        :param dirpath: The path to the output directory.
        :type dirpath: str
        """
        datastore.save_to_csv(dirpath)

    @staticmethod
    def data_from_csv(dirpath: str) -> None:
        """
        Delegates loading all data from CSV files into memory.

        :param dirpath: The path to the input directory.
        :type dirpath: str
        """
        datastore.load_from_csv(dirpath)
