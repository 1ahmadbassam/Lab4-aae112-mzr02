"""
Defines the base model for a person.

This module contains the `Person` class, which serves as a base class
for other human-like models in the system, such as `Student` and `Instructor`.
It encapsulates common attributes like name, age, and email.
"""
import random

from ..utils.validator import check_name, check_age, check_email_r


class Person:
    """
    Represents a generic person in the School Management System.

    This class includes basic attributes and validation for a person's name,
    age, and email. It is intended to be subclassed by more specific
    person types.

    :ivar name: The name of the person.
    :vartype name: str
    :ivar age: The age of the person.
    :vartype age: int
    :ivar _email: The private email address of the person.
    :vartype _email: str
    """

    def __init__(self, name: str, age: int, email: str):
        """
        Initializes a Person object.

        :param name: The person's full name.
        :type name: str
        :param age: The person's age in years.
        :type age: int
        :param email: The person's email address.
        :type email: str
        :raises ValueError: If any of the provided arguments are invalid.
        """
        if not check_name(name.strip()):
            raise ValueError("Invalid Name.")
        self.name: str = name.strip()
        if not check_age(age):
            raise ValueError("Invalid Age.")
        self.age: int = age
        if not (em := check_email_r(email.strip()))[0]:
            raise ValueError("Invalid Email Address" + (f": {em[1]}" if em[1] else "."))
        self._email: str = email.strip()

    def introduce(self):
        """Prints a brief, randomized introduction message to the console."""
        print(
            random.choice(["Hello", "Hi",
                           "Hey"]) + f"! I am {self.name}. I am {self.age} year{'s' if self.age != 1 else ''} old."
        )

    def update(self, **kwargs):
        """
        Updates the person's attributes from keyword arguments.

        This method allows for partial updates. Only provided fields are changed.

        :param kwargs: Keyword arguments for attributes to update (e.g., name, age, email).
        :raises ValueError: If any of the provided values are invalid.
        """
        name = kwargs.get("name")
        age = kwargs.get("age")
        email = kwargs.get("email")

        if name:
            if not check_name(name.strip()):
                raise ValueError("Invalid Name.")
            self.name = name.strip()

        if age:
            age = int(age)
            if not check_age(age):
                raise ValueError("Invalid Age.")
            self.age = age

        if email:
            if not (em := check_email_r(email.strip()))[0]:
                raise ValueError("Invalid Email Address" + (f": {em[1]}" if em[1] else "."))
            self._email = email.strip()

    def __repr__(self) -> str:
        """
        Provides an unambiguous string representation of the Person object.

        :return: A string for developers to recreate the object.
        :rtype: str
        """
        return f"Person({self.name}, {self.age}, {self._email})"

    def __str__(self) -> str:
        """
        Provides a user-friendly string representation of the Person object.

        :return: The same as `__repr__` for this class.
        :rtype: str
        """
        return self.__repr__()

    @staticmethod
    def row() -> list[str]:
        """
        Returns the header row for CSV serialization.

        :return: A list of attribute names for the CSV header.
        :rtype: list[str]
        """
        return ["name", "age", "email"]

    def to_row(self) -> list[str]:
        """
        Serializes the object's data to a list for a CSV row.

        :return: A list of the person's attributes as strings.
        :rtype: list[str]
        """
        return [self.name, str(self.age), self._email]

    def to_dict(self) -> dict:
        """
        Serializes the object's data to a dictionary.

        :return: A dictionary mapping attribute names to their values.
        :rtype: dict
        """
        return {
            "name": self.name,
            "age": self.age,
            "email": self._email
        }
