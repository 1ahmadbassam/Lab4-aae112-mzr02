"""
Provides validation functions for various data fields.

This module contains a collection of functions to validate the format and
content of common data types used in the School Management System, such as
names, ages, emails, and various ID formats. It adaptively uses more powerful
libraries like `regex` and `email_validator` if they are installed, with
fallbacks to standard library implementations.
"""

import logging

logger = logging.getLogger(__name__)

try:
    from regex import re

    UNICODE_SUPPORT = True
except ImportError:
    import re

    UNICODE_SUPPORT = False
    logger.warning("The regex module is not installed. Falling back to re module. Unicode is not supported.")

try:
    from email_validator import validate_email, EmailNotValidError
except ImportError:
    validate_email = None
    EmailNotValidError = None
    logger.warning("The email-validator module is not installed. Falling back to basic email validation.")


def check_name(name: str) -> bool:
    """
    Validates a person's name.

    Checks if the name contains valid characters (letters, apostrophes, hyphens, etc.).
    Supports Unicode characters if the `regex` library is installed.

    :param name: The name to validate.
    :type name: str
    :return: True if the name is valid, False otherwise.
    :rtype: bool
    """
    # regex adapted from https://stackoverflow.com/questions/2385701/regular-expression-for-first-and-last-name
    if not re.fullmatch("^[\p{L}\p{M}' -.]+$" if UNICODE_SUPPORT else r"^[a-zA-Z' .-]+$", name.strip()):
        return False
    return True


def check_age(age: int) -> bool:
    """
    Validates a person's age.

    Checks if the age is within a reasonable range (0 to 120).

    :param age: The age to validate.
    :type age: int
    :return: True if the age is valid, False otherwise.
    :rtype: bool
    """
    return 0 <= age <= 120


def check_email_r(email: str) -> tuple[bool, str]:
    """
    Validates an email address and returns a reason for failure.

    Uses the `email_validator` library if available for robust, RFC-compliant
    validation. Falls back to a basic regular expression if the library is not installed.

    :param email: The email address to validate.
    :type email: str
    :return: A tuple containing a boolean (True for valid) and a string (error message if invalid).
    :rtype: tuple[bool, str]
    """
    # I'd like to use email-validator library, but IDK if allowed
    # so instead, let's offer a fallback
    if validate_email and EmailNotValidError:
        try:
            validate_email(email.strip())
            return True, ""
        except EmailNotValidError as e:
            return False, e.args[0]

    # regex obtained from https://emailregex.com/
    if not re.fullmatch(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email.strip()):
        return False, ""
    return True, ""


def check_email(email: str) -> bool:
    """
    Validates an email address.

    This is a convenience wrapper around `check_email_r` that returns only a boolean.

    :param email: The email address to validate.
    :type email: str
    :return: True if the email is valid, False otherwise.
    :rtype: bool
    """
    return check_email_r(email)[0]


def check_id(p_id: str) -> bool:
    """
    Validates a student or instructor ID.

    Checks if the ID consists of exactly 9 digits.

    :param p_id: The ID to validate.
    :type p_id: str
    :return: True if the ID is valid, False otherwise.
    :rtype: bool
    """
    # AUB id format: 9 digits (e.g. 202456789)
    if not re.fullmatch(r"^\d{9}$", p_id.strip()):
        return False
    return True


def check_course_id(c_id: str) -> bool:
    """
    Validates a course ID.

    Checks if the ID follows the format of 4 letters, 3 numbers, and an
    optional trailing letter (e.g., EECE230, MATH201, EECE435L).

    :param c_id: The course ID to validate.
    :type c_id: str
    :return: True if the course ID is valid, False otherwise.
    :rtype: bool
    """
    # AUB id format: 4 letters + 3 numbers + optional letter (e.g. EECE230 - MATH201 - EECE435L)
    if not re.fullmatch(r"^[a-zA-Z]{4}\d{3}[a-zA-Z]?$", c_id.strip()):
        return False
    return True


def check_course_name(name: str) -> bool:
    """
    Validates a course name.

    Checks for a reasonable length and ensures it contains only allowed
    characters (alphanumeric and common punctuation).

    :param name: The course name to validate.
    :type name: str
    :return: True if the course name is valid, False otherwise.
    :rtype: bool
    """
    # AUB course name format: words, numbers, some characters
    if not (3 < len(name.strip()) <= 100):
        return False
    if not re.fullmatch(r"^[a-zA-Z0-9 '.,:&()/-]+$", name.strip()):
        return False
    return True
