"""
Defines the database schema for the School Management System.

This module contains string constants, each holding a SQL `CREATE TABLE`
statement for a specific entity in the system. These schemas are used by
the DatabaseManager to initialize the database tables.

Attributes:
    STUDENT_SCHEMA (str): SQL schema for the 'students' table.
    INSTRUCTOR_SCHEMA (str): SQL schema for the 'instructors' table.
    COURSE_SCHEMA (str): SQL schema for the 'courses' table.
    ENROLLMENT_SCHEMA (str): SQL schema for the 'enrollments' join table.
"""

STUDENT_SCHEMA = """
                 CREATE TABLE IF NOT EXISTS students
                 (
                     name       TEXT    NOT NULL,
                     age        INTEGER NOT NULL,
                     email      TEXT    NOT NULL,
                     student_id TEXT PRIMARY KEY
                 );
                 """

INSTRUCTOR_SCHEMA = """
                    CREATE TABLE IF NOT EXISTS instructors
                    (
                        name          TEXT    NOT NULL,
                        age           INTEGER NOT NULL,
                        email         TEXT    NOT NULL,
                        instructor_id TEXT PRIMARY KEY
                    );
                    """

COURSE_SCHEMA = """
                CREATE TABLE IF NOT EXISTS courses
                (
                    course_id     TEXT PRIMARY KEY,
                    course_name   TEXT NOT NULL,
                    instructor_id TEXT NOT NULL,
                    FOREIGN KEY (instructor_id) REFERENCES instructors (instructor_id)
                );
                """

ENROLLMENT_SCHEMA = """
                    CREATE TABLE IF NOT EXISTS enrollments
                    (
                        student_id TEXT NOT NULL,
                        course_id  TEXT NOT NULL,
                        PRIMARY KEY (student_id, course_id),
                        FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
                    );
                    """
