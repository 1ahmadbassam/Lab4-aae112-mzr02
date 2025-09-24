"""
Manages all database operations for the School Management System.

This module provides the DatabaseManager class, which encapsulates the logic
for connecting to an SQLite database and performing CRUD operations
for students, instructors, courses, and enrollments.
"""

import logging
import os
import sqlite3

from .contract import *

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str = 'sms.db'):
        """
        Initializes the DatabaseManager and connects to the database.

        :param db_path: The file path for the SQLite database. Defaults to 'sms.db'.
        :type db_path: str
        """
        self.db_path = os.path.abspath(db_path)
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.db_path)
            # enable foreign key constraints
            self.conn.execute("PRAGMA foreign_keys = 1;")
            logger.info(f"Successfully connected to database at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")

    def create_tables(self) -> bool:
        """
        Creates all necessary tables in the database using the defined schemas.

        :return: True if tables were created successfully, False otherwise.
        :rtype: bool
        """
        if not self.conn:
            return False
        cursor = self.conn.cursor()

        try:
            for schema in [STUDENT_SCHEMA, INSTRUCTOR_SCHEMA, COURSE_SCHEMA, ENROLLMENT_SCHEMA]:
                cursor.execute(schema)
            self.conn.commit()
            logger.info("Database tables created.")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            return False
        finally:
            cursor.close()

        return True

    def add_student(self, student_id: str, name: str, age: int, email: str) -> bool:
        """
        Adds a new student to the database.

        :param student_id: The unique ID of the student.
        :type student_id: str
        :param name: The name of the student.
        :type name: str
        :param age: The age of the student.
        :type age: int
        :param email: The email address of the student.
        :type email: str
        :return: True upon successful insertion.
        :rtype: bool
        """
        sql = "INSERT INTO students (student_id, name, age, email) VALUES (?, ?, ?, ?)"
        cursor = self.conn.cursor()
        cursor.execute(sql, (student_id, name, age, email))
        self.conn.commit()
        return True

    def get_student(self, student_id: str) -> tuple:
        """
        Retrieves a single student's record from the database.

        :param student_id: The ID of the student to retrieve.
        :type student_id: str
        :return: A tuple containing the student's data, or None if not found.
        :rtype: tuple | None
        """
        sql = "SELECT * FROM students WHERE student_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(sql, (student_id,))
        return cursor.fetchone()

    def get_all_students(self) -> list[tuple]:
        """
        Retrieves all student records from the database.

        :return: A list of tuples, where each tuple represents a student.
        :rtype: list[tuple]
        """
        sql = "SELECT * FROM students"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def update_student(self, student_id: str, **kwargs) -> bool:
        """
        Updates a student's record in the database.

        Accepts keyword arguments for 'name', 'age', and 'email'.

        :param student_id: The ID of the student to update.
        :type student_id: str
        :param kwargs: Keyword arguments with fields to update.
        :return: True if the update was successful, False otherwise.
        :rtype: bool
        """
        allowed_fields = {"name", "age", "email"}
        update_fields = {key: value for key, value in kwargs.items() if key in allowed_fields}

        if not update_fields:
            return False

        set_clause = ", ".join([f"{key} = ?" for key in update_fields.keys()])
        sql = f"UPDATE students SET {set_clause} WHERE student_id = ?"

        values = list(update_fields.values()) + [student_id]

        cursor = self.conn.cursor()
        cursor.execute(sql, tuple(values))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_student(self, student_id: str) -> bool:
        """
        Deletes a student's record from the database.

        :param student_id: The ID of the student to delete.
        :type student_id: str
        :return: True if the deletion was successful, False otherwise.
        :rtype: bool
        """
        sql = "DELETE FROM students WHERE student_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(sql, (student_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def add_instructor(self, instructor_id: str, name: str, age: int, email: str) -> bool:
        """
        Adds a new instructor to the database.

        :param instructor_id: The unique ID of the instructor.
        :type instructor_id: str
        :param name: The name of the instructor.
        :type name: str
        :param age: The age of the instructor.
        :type age: int
        :param email: The email address of the instructor.
        :type email: str
        :return: True upon successful insertion.
        :rtype: bool
        """
        sql = "INSERT INTO instructors (instructor_id, name, age, email) VALUES (?, ?, ?, ?)"
        cursor = self.conn.cursor()
        cursor.execute(sql, (instructor_id, name, age, email))
        self.conn.commit()
        return True

    def get_instructor(self, instructor_id: str) -> tuple:
        """
        Retrieves a single instructor's record from the database.

        :param instructor_id: The ID of the instructor to retrieve.
        :type instructor_id: str
        :return: A tuple containing the instructor's data, or None if not found.
        :rtype: tuple | None
        """
        sql = "SELECT * FROM instructors WHERE instructor_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(sql, (instructor_id,))
        return cursor.fetchone()

    def get_all_instructors(self) -> list[tuple]:
        """
        Retrieves all instructor records from the database.

        :return: A list of tuples, where each tuple represents an instructor.
        :rtype: list[tuple]
        """
        sql = "SELECT * FROM instructors"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def update_instructor(self, instructor_id: str, **kwargs) -> bool:
        """
        Updates an instructor's record in the database.

        Accepts keyword arguments for 'name', 'age', and 'email'.

        :param instructor_id: The ID of the instructor to update.
        :type instructor_id: str
        :param kwargs: Keyword arguments with fields to update.
        :return: True if the update was successful, False otherwise.
        :rtype: bool
        """
        allowed_fields = {"name", "age", "email"}
        update_fields = {key: value for key, value in kwargs.items() if key in allowed_fields}

        if not update_fields:
            return False

        set_clause = ", ".join([f"{key} = ?" for key in update_fields.keys()])
        sql = f"UPDATE instructors SET {set_clause} WHERE instructor_id = ?"

        values = list(update_fields.values()) + [instructor_id]

        cursor = self.conn.cursor()
        cursor.execute(sql, tuple(values))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_instructor(self, instructor_id: str) -> bool:
        """
        Deletes an instructor's record from the database.

        :param instructor_id: The ID of the instructor to delete.
        :type instructor_id: str
        :return: True if the deletion was successful, False otherwise.
        :rtype: bool
        """
        sql = "DELETE FROM instructors WHERE instructor_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(sql, (instructor_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def add_course(self, course_id: str, course_name: str, instructor_id: str) -> bool:
        """
        Adds a new course to the database.

        :param course_id: The unique ID of the course.
        :type course_id: str
        :param course_name: The name of the course.
        :type course_name: str
        :param instructor_id: The ID of the instructor teaching the course.
        :type instructor_id: str
        :return: True upon successful insertion.
        :rtype: bool
        """
        sql = "INSERT INTO courses (course_id, course_name, instructor_id) VALUES (?, ?, ?)"
        cursor = self.conn.cursor()
        cursor.execute(sql, (course_id, course_name, instructor_id))
        self.conn.commit()
        return True

    def get_course(self, course_id: str) -> tuple:
        """
        Retrieves a single course's record along with its assigned instructor's details.

        :param course_id: The ID of the course to retrieve.
        :type course_id: str
        :return: A tuple containing the combined course and instructor data, or None if not found.
        :rtype: tuple | None
        """
        sql = """
              SELECT c.course_id,
                     c.course_name,
                     i.instructor_id,
                     i.name,
                     i.age,
                     i.email
              FROM courses c
                       JOIN
                   instructors i ON c.instructor_id = i.instructor_id
              WHERE c.course_id = ? \
              """
        cursor = self.conn.cursor()
        cursor.execute(sql, (course_id,))
        return cursor.fetchone()

    def get_all_courses(self) -> list[tuple]:
        """
        Retrieves all course records along with their assigned instructor's details.

        :return: A list of tuples, where each tuple represents a course and its instructor.
        :rtype: list[tuple]
        """
        sql = """
              SELECT c.course_id,
                     c.course_name,
                     i.instructor_id,
                     i.name,
                     i.age,
                     i.email
              FROM courses c
                       JOIN
                   instructors i ON c.instructor_id = i.instructor_id \
              """
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def update_course(self, course_id: str, **kwargs) -> bool:
        """
        Updates a course's record in the database.

        Accepts keyword arguments for 'course_name' and 'instructor_id'.

        :param course_id: The ID of the course to update.
        :type course_id: str
        :param kwargs: Keyword arguments with fields to update.
        :return: True if the update was successful, False otherwise.
        :rtype: bool
        """
        allowed_fields = {"course_name", "instructor_id"}
        update_fields = {key: value for key, value in kwargs.items() if key in allowed_fields}

        if not update_fields:
            return False

        set_clause = ", ".join([f"{key} = ?" for key in update_fields.keys()])
        sql = f"UPDATE courses SET {set_clause} WHERE course_id = ?"

        values = list(update_fields.values()) + [course_id]

        cursor = self.conn.cursor()
        cursor.execute(sql, tuple(values))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_course(self, course_id: str) -> bool:
        """
        Deletes a course's record from the database.

        :param course_id: The ID of the course to delete.
        :type course_id: str
        :return: True if the deletion was successful, False otherwise.
        :rtype: bool
        """
        sql = "DELETE FROM courses WHERE course_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(sql, (course_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def enroll_student(self, student_id, course_id):
        """
        Enrolls a student in a course by creating a record in the enrollments table.

        :param student_id: The ID of the student to enroll.
        :type student_id: str
        :param course_id: The ID of the course to enroll in.
        :type course_id: str
        :return: True upon successful enrollment.
        :rtype: bool
        """
        sql = "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)"
        cursor = self.conn.cursor()
        cursor.execute(sql, (student_id, course_id))
        self.conn.commit()
        return True

    def get_student_courses(self, student_id):
        """
        Retrieves all courses a specific student is enrolled in.

        :param student_id: The ID of the student.
        :type student_id: str
        :return: A list of tuples, each containing a course ID and name.
        :rtype: list[tuple]
        """
        sql = """
              SELECT c.course_id, c.course_name
              FROM courses c
                       JOIN enrollments e ON c.course_id = e.course_id
              WHERE e.student_id = ?
              """
        cursor = self.conn.cursor()
        cursor.execute(sql, (student_id,))
        return cursor.fetchall()

    def get_course_enrollments(self, course_id):
        """
        Retrieves all students enrolled in a specific course.

        :param course_id: The ID of the course.
        :type course_id: str
        :return: A list of tuples, each containing a student's ID and name.
        :rtype: list[tuple]
        """
        sql = """
              SELECT s.student_id, s.name
              FROM students s
                       JOIN enrollments e ON s.student_id = e.student_id
              WHERE e.course_id = ?
              """
        cursor = self.conn.cursor()
        cursor.execute(sql, (course_id,))
        return cursor.fetchall()

    def get_instructor_courses(self, instructor_id: str) -> list[tuple]:
        """
        Retrieves all courses taught by a specific instructor.

        :param instructor_id: The ID of the instructor.
        :type instructor_id: str
        :return: A list of tuples, each containing a course ID and name.
        :rtype: list[tuple]
        """
        sql = "SELECT course_id, course_name FROM courses WHERE instructor_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(sql, (instructor_id,))
        return cursor.fetchall()

    def get_all_enrollments(self) -> list[tuple]:
        """
        Retrieves all enrollment records from the database.

        :return: A list of tuples, where each tuple is a (student_id, course_id) pair.
        :rtype: list[tuple]
        """
        sql = "SELECT student_id, course_id FROM enrollments"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def get_courses_for_student(self, student_id: str) -> list[tuple]:
        """
        Retrieves full details for all courses a specific student is enrolled in.

        Includes course information and instructor details for each course.

        :param student_id: The ID of the student.
        :type student_id: str
        :return: A list of tuples, each representing a course with its instructor.
        :rtype: list[tuple]
        """
        sql = """
              SELECT c.course_id,
                     c.course_name,
                     i.instructor_id,
                     i.name,
                     i.age,
                     i.email
              FROM courses c
                       JOIN instructors i ON c.instructor_id = i.instructor_id
                       JOIN enrollments e ON c.course_id = e.course_id
              WHERE e.student_id = ?
              """
        cursor = self.conn.cursor()
        cursor.execute(sql, (student_id,))
        return cursor.fetchall()

    def get_students_for_course(self, course_id: str) -> list[tuple]:
        """
        Retrieves all students enrolled in a specific course.

        :param course_id: The ID of the course.
        :type course_id: str
        :return: A list of tuples, where each tuple is a student record.
        :rtype: list[tuple]
        """
        sql = """
              SELECT s.*
              FROM students s
                       JOIN enrollments e ON s.student_id = e.student_id
              WHERE e.course_id = ? \
              """
        cursor = self.conn.cursor()
        cursor.execute(sql, (course_id,))
        return cursor.fetchall()

    def clear_all_tables(self):
        """
        Deletes all records from all tables in the database.

        Performs deletions in an order that respects foreign key constraints.
        Rolls back the transaction if an error occurs.

        :raises sqlite3.Error: If a database error occurs during deletion.
        """
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM enrollments;")
            cursor.execute("DELETE FROM courses;")
            cursor.execute("DELETE FROM students;")
            cursor.execute("DELETE FROM instructors;")
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def close(self):
        """
        Closes the connection to the database.
        """
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")


if __name__ == '__main__':
    db_manager = DatabaseManager()
    db_manager.create_tables()
    db_manager.close()
