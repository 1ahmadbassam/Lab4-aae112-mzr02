"""
Defines the data model for a course.

This module contains the `Course` class, which encapsulates all information
related to a specific course, including its ID, name, assigned instructor,
and a list of enrolled students.
"""
from __future__ import annotations

from .instructor import Instructor
from .student import Student
from ..utils.validator import check_course_id, check_course_name


class Course:
    """
    Represents a course in the School Management System.

    This class holds details about a course, manages the list of students
    enrolled in it, and links to the instructor teaching it.

    :ivar course_id: The unique ID of the course (e.g., 'EECE230').
    :vartype course_id: str
    :ivar course_name: The full name of the course.
    :vartype course_name: str
    :ivar instructor: The `Instructor` object assigned to the course.
    :vartype instructor: Instructor
    :ivar enrolled_students: A list of `Student` objects enrolled in the course.
    :vartype enrolled_students: list[Student]
    """

    def __init__(self, course_id: str, course_name: str, instructor: Instructor):
        """
        Initializes a Course object.

        Upon initialization, the course is automatically assigned to the
        provided instructor.

        :param course_id: The unique ID for the course.
        :type course_id: str
        :param course_name: The name of the course.
        :type course_name: str
        :param instructor: The `Instructor` object for the course.
        :type instructor: Instructor
        :raises ValueError: If the course ID or name is invalid.
        """
        if not check_course_id(course_id.strip()):
            raise ValueError("Invalid Course ID.")
        self.course_id: str = course_id.strip().upper()
        if not check_course_name(course_name.strip()):
            raise ValueError("Invalid Course Name.")
        self.course_name: str = course_name
        self.instructor: Instructor = instructor
        self.enrolled_students: list[Student] = []

        # assign course to instructor after creation
        self.instructor.assign_course(self)

    def add_student(self, student: Student):
        """
        Adds a student to the course's enrollment list.

        This method is idempotent; it will not add a student if they are
        already enrolled.

        :param student: The `Student` object to enroll.
        :type student: Student
        """
        if student.student_id not in {s.student_id for s in self.enrolled_students}:
            self.enrolled_students.append(student)

    def update(self, **kwargs):
        """
        Updates the course's attributes from keyword arguments.

        Allows for partial updates. Supported fields are `course_name` and `instructor`.

        :param kwargs: Keyword arguments for attributes to update.
        :raises ValueError: If the provided course name is invalid.
        """
        course_name = kwargs.get("course_name")
        instructor = kwargs.get("instructor")

        if course_name:
            if not check_course_name(course_name.strip()):
                raise ValueError("Invalid Course Name.")
            self.course_name = course_name.strip()

        if instructor:
            self.instructor = instructor

    def __repr__(self) -> str:
        """
        Provides an unambiguous string representation of the Course object.

        :return: A string for developers to understand the object state.
        :rtype: str
        """
        instructor_id = self.instructor.instructor_id
        student_ids = [s.student_id for s in self.enrolled_students]

        return (f"Course(ID='{self.course_id}', Name='{self.course_name}', "
                f"InstructorID='{instructor_id}', EnrolledStudents={student_ids})")

    def __str__(self) -> str:
        """
        Provides a user-friendly string representation of the Course object.

        :return: The same as `__repr__` for this class.
        :rtype: str
        """
        return self.__repr__()

    def to_dict(self) -> dict:
        """
        Serializes the object's data to a dictionary.

        :return: A dictionary mapping attribute names to their values.
        :rtype: dict
        """
        return {"course_id": self.course_id, "course_name": self.course_name,
                "instructor_id": self.instructor.instructor_id,
                "enrolled_students": [student.student_id for student in self.enrolled_students]}

    @staticmethod
    def row() -> list[str]:
        """
        Returns the header row for CSV serialization.

        :return: A list of attribute names for the CSV header.
        :rtype: list[str]
        """
        return ["course_id", "course_name", "instructor_id"]

    def to_row(self) -> list[str]:
        """
        Serializes the object's data to a list for a CSV row.

        :return: A list of the course's key attributes as strings.
        :rtype: list[str]
        """
        return [self.course_id, self.course_name, self.instructor.instructor_id]
