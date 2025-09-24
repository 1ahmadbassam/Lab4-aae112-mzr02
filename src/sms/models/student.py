"""
Defines the data model for a student.

This module contains the `Student` class, which inherits from the `Person`
class and includes student-specific attributes and methods, such as a
student ID and course registration functionality.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from .person import Person
from ..utils.validator import check_id

# prevent circular dependency loop by using
# type checking stage import
if TYPE_CHECKING:
    # noinspection PyUnusedImports
    from course import Course


class Student(Person):
    """
    Represents a student in the School Management System.

    Inherits from the `Person` class and adds a unique student ID and a list
    of courses the student is registered in.

    :ivar student_id: The student's unique 9-digit ID.
    :vartype student_id: str
    :ivar registered_courses: A list of `Course` objects the student is enrolled in.
    :vartype registered_courses: list[Course]
    """
    def __init__(self, name: str, age: int, email: str, student_id: str):
        """
        Initializes a Student object.

        :param name: The student's full name.
        :type name: str
        :param age: The student's age in years.
        :type age: int
        :param email: The student's email address.
        :type email: str
        :param student_id: The student's unique 9-digit ID.
        :type student_id: str
        :raises ValueError: If the student ID or other person data is invalid.
        """
        # call parent class constructor
        super().__init__(name, age, email)
        if not check_id(student_id.strip()):
            raise ValueError("Invalid Student ID.")
        self.student_id: str = student_id.strip()
        # manually annotating type between quotes
        # cool python feature btw
        # requires __future__ import
        self.registered_courses: list["Course"] = []

    def register_course(self, course: "Course"):
        """
        Registers the student for a course.

        Adds the course to the student's list of registered courses and also
        adds the student to the course's list of enrolled students. This
        method is idempotent; it won't add a duplicate course.

        :param course: The `Course` object to register for.
        :type course: Course
        """
        if course.course_id not in {c.course_id for c in self.registered_courses}:
            self.registered_courses.append(course)
            # register student in course
            course.add_student(self)

    def __repr__(self) -> str:
        """
        Provides an unambiguous string representation of the Student object.

        :return: A string for developers to recreate the object.
        :rtype: str
        """
        course_ids = [c.course_id for c in self.registered_courses]
        return f"Student({self.name}, {self.age}, {self._email}, {self.student_id}, RegisteredCourses={course_ids})"

    def __str__(self) -> str:
        """
        Provides a user-friendly string representation of the Student object.

        :return: The same as `__repr__` for this class.
        :rtype: str
        """
        return self.__repr__()

    def to_dict(self) -> dict:
        """
        Serializes the object's data to a dictionary.

        Extends the parent `Person.to_dict` method with student-specific data.

        :return: A dictionary mapping attribute names to their values.
        :rtype: dict
        """
        data = super().to_dict()
        data.update({
            "type": "student",
            "student_id": self.student_id,
            "registered_courses": [course.course_id for course in self.registered_courses]
        })
        return data

    @staticmethod
    def row(by_id=False) -> list[str]:
        """
        Returns the header row for CSV serialization.

        :param by_id: If True, the student_id is the first column. Defaults to False.
        :type by_id: bool, optional
        :return: A list of attribute names for the CSV header.
        :rtype: list[str]
        """
        if by_id:
            return ["student_id", "name", "age", "email"]
        return ["name", "age", "email", "student_id"]

    def to_row(self, by_id=False) -> list[str]:
        """
        Serializes the object's data to a list for a CSV row.

        :param by_id: If True, the student_id is the first column. Defaults to False.
        :type by_id: bool, optional
        :return: A list of the student's attributes as strings.
        :rtype: list[str]
        """
        if by_id:
            return [self.student_id, self.name, str(self.age), self._email]
        return [self.name, str(self.age), self._email, self.student_id]
