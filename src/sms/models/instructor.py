"""
Defines the data model for an instructor.

This module contains the `Instructor` class, which inherits from the `Person`
class and includes instructor-specific attributes and methods, such as an
instructor ID and course assignment functionality.
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


class Instructor(Person):
    """
    Represents an instructor in the School Management System.

    Inherits from the `Person` class and adds a unique instructor ID and a list
    of courses the instructor is assigned to teach.

    :ivar instructor_id: The instructor's unique 9-digit ID.
    :vartype instructor_id: str
    :ivar assigned_courses: A list of `Course` objects the instructor teaches.
    :vartype assigned_courses: list[Course]
    """
    def __init__(self, name: str, age: int, email: str, instructor_id: str):
        """
        Initializes an Instructor object.

        :param name: The instructor's full name.
        :type name: str
        :param age: The instructor's age in years.
        :type age: int
        :param email: The instructor's email address.
        :type email: str
        :param instructor_id: The instructor's unique 9-digit ID.
        :type instructor_id: str
        :raises ValueError: If the instructor ID or other person data is invalid.
        """
        super().__init__(name, age, email)
        if not check_id(instructor_id.strip()):
            raise ValueError("Invalid Instructor ID.")
        self.instructor_id: str = instructor_id
        # manually annotating type between quotes
        # cool python feature btw
        # requires __future__ import
        self.assigned_courses: list["Course"] = []

    def assign_course(self, course: "Course"):
        """
        Assigns a course to the instructor.

        This method is idempotent; it will not add a course if it's already assigned.

        :param course: The `Course` object to assign.
        :type course: Course
        """
        if course.course_id not in {c.course_id for c in self.assigned_courses}:
            self.assigned_courses.append(course)

    def __repr__(self) -> str:
        """
        Provides an unambiguous string representation of the Instructor object.

        :return: A string for developers to recreate the object.
        :rtype: str
        """
        course_ids = [c.course_id for c in self.assigned_courses]
        return f"Instructor({self.name}, {self.age}, {self._email}, {self.instructor_id}, AssignedCourses={course_ids})"

    def __str__(self) -> str:
        """
        Provides a user-friendly string representation of the Instructor object.

        :return: The same as `__repr__` for this class.
        :rtype: str
        """
        return self.__repr__()

    def to_dict(self) -> dict:
        """
        Serializes the object's data to a dictionary.

        Extends the parent `Person.to_dict` method with instructor-specific data.

        :return: A dictionary mapping attribute names to their values.
        :rtype: dict
        """
        data = super().to_dict()
        data.update({
            "type": "instructor",
            "instructor_id": self.instructor_id,
            "assigned_courses": [course.course_id for course in self.assigned_courses]
        })
        return data

    @staticmethod
    def row(by_id=False) -> list[str]:
        """
        Returns the header row for CSV serialization.

        :param by_id: If True, the instructor_id is the first column. Defaults to False.
        :type by_id: bool, optional
        :return: A list of attribute names for the CSV header.
        :rtype: list[str]
        """
        if by_id:
            return ["instructor_id", "name", "age", "email"]
        return ["name", "age", "email", "instructor_id"]

    def to_row(self, by_id=False) -> list[str]:
        """
        Serializes the object's data to a list for a CSV row.

        :param by_id: If True, the instructor_id is the first column. Defaults to False.
        :type by_id: bool, optional
        :return: A list of the instructor's attributes as strings.
        :rtype: list[str]
        """
        if by_id:
            return [self.instructor_id, self.name, str(self.age), self._email]
        return [self.name, str(self.age), self._email, self.instructor_id]
