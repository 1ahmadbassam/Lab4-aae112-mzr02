"""
Defines the abstract interface for all data management classes.

This module provides the `BaseDataManager` abstract base class (ABC),
which establishes a contract for concrete data manager implementations
(e.g., for memory, file, or database storage). It ensures that all
data managers expose a consistent API for handling CRUD operations.
It also defines a custom `DataError` exception.
"""
from abc import ABC, abstractmethod

from ...models.course import Course
from ...models.instructor import Instructor
from ...models.student import Student


class DataError(ValueError):
    """Custom exception raised for data-related errors."""
    pass


class BaseDataManager(ABC):
    """
    Abstract base class that defines the data management interface.

    All concrete data manager classes must inherit from this class and
    implement all its abstract methods.
    """

    @staticmethod
    @abstractmethod
    def add_student(**kwargs) -> None:
        """
        Adds a new student to the data store.

        :param kwargs: Keyword arguments representing student attributes.
        :raises DataError: If student data is invalid or student already exists.
        """
        pass

    @staticmethod
    @abstractmethod
    def edit_student(**kwargs) -> None:
        """
        Edits an existing student's information.

        Requires 'student_id' in kwargs to identify the student.

        :param kwargs: Keyword arguments with fields to update.
        :raises DataError: If the student is not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def remove_student(student_id: str) -> None:
        """
        Removes a student from the data store.

        :param student_id: The ID of the student to remove.
        :type student_id: str
        :raises DataError: If the student is not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_student(student_id: str) -> Student:
        """
        Retrieves a single student object.

        :param student_id: The ID of the student to retrieve.
        :type student_id: str
        :return: The corresponding Student object.
        :rtype: Student
        :raises DataError: If the student is not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_students() -> list[Student]:
        """
        Retrieves a list of all student objects.

        :return: A list of all students.
        :rtype: list[Student]
        """
        pass

    @staticmethod
    @abstractmethod
    def add_instructor(**kwargs) -> None:
        """
        Adds a new instructor to the data store.

        :param kwargs: Keyword arguments representing instructor attributes.
        :raises DataError: If instructor data is invalid or instructor already exists.
        """
        pass

    @staticmethod
    @abstractmethod
    def edit_instructor(**kwargs) -> None:
        """
        Edits an existing instructor's information.

        Requires 'instructor_id' in kwargs to identify the instructor.

        :param kwargs: Keyword arguments with fields to update.
        :raises DataError: If the instructor is not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def remove_instructor(instructor_id: str) -> None:
        """
        Removes an instructor from the data store.

        :param instructor_id: The ID of the instructor to remove.
        :type instructor_id: str
        :raises DataError: If the instructor is not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_instructors() -> list[Instructor]:
        """
        Retrieves a list of all instructor objects.

        :return: A list of all instructors.
        :rtype: list[Instructor]
        """
        pass

    @staticmethod
    @abstractmethod
    def get_instructor(instructor_id: str) -> Instructor:
        """
        Retrieves a single instructor object.

        :param instructor_id: The ID of the instructor to retrieve.
        :type instructor_id: str
        :return: The corresponding Instructor object.
        :rtype: Instructor
        :raises DataError: If the instructor is not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def add_course(**kwargs) -> None:
        """
        Adds a new course to the data store.

        :param kwargs: Keyword arguments representing course attributes.
        :raises DataError: If course data is invalid or course already exists.
        """
        pass

    @staticmethod
    @abstractmethod
    def edit_course(**kwargs) -> None:
        """
        Edits an existing course's information.

        Requires 'course_id' in kwargs to identify the course.

        :param kwargs: Keyword arguments with fields to update.
        :raises DataError: If the course is not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def remove_course(course_id: str) -> None:
        """
        Removes a course from the data store.

        :param course_id: The ID of the course to remove.
        :type course_id: str
        :raises DataError: If the course is not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_course(course_id: str) -> Course:
        """
        Retrieves a single course object.

        :param course_id: The ID of the course to retrieve.
        :type course_id: str
        :return: The corresponding Course object.
        :rtype: Course
        :raises DataError: If the course is not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_courses() -> list[Course]:
        """
        Retrieves a list of all course objects.

        :return: A list of all courses.
        :rtype: list[Course]
        """
        pass

    @staticmethod
    @abstractmethod
    def enroll_student(student_id: str, course_id: str) -> None:
        """
        Enrolls a student in a course.

        :param student_id: The ID of the student to enroll.
        :type student_id: str
        :param course_id: The ID of the course to enroll in.
        :type course_id: str
        :raises DataError: If student or course is not found, or enrollment already exists.
        """
        pass

    @staticmethod
    @abstractmethod
    def data_to_json(filepath: str) -> None:
        """
        Serializes all data to a JSON file.

        :param filepath: The path to the output JSON file.
        :type filepath: str
        :raises IOError: If the file cannot be written.
        """
        pass

    @staticmethod
    @abstractmethod
    def data_from_json(filepath: str) -> None:
        """
        Deserializes and loads all data from a JSON file.

        :param filepath: The path to the input JSON file.
        :type filepath: str
        :raises IOError: If the file cannot be read.
        :raises DataError: If the data format is invalid.
        """
        pass

    @staticmethod
    @abstractmethod
    def data_to_csv(dirpath: str) -> None:
        """
        Serializes all data to multiple CSV files in a directory.

        :param dirpath: The path to the output directory.
        :type dirpath: str
        :raises IOError: If files cannot be written.
        """
        pass

    @staticmethod
    @abstractmethod
    def data_from_csv(dirpath: str) -> None:
        """
        Deserializes and loads all data from CSV files in a directory.

        :param dirpath: The path to the input directory.
        :type dirpath: str
        :raises IOError: If files cannot be read.
        :raises DataError: If the data format is invalid.
        """
        pass
