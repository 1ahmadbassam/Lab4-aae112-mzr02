"""
Provides a database-backed implementation of the data management interface.

This module uses a `DatabaseManager` for direct SQL operations and implements
the `DatabaseDataManager` class. This class uses an in-memory caching strategy
to "hydrate" data from the database into a network of Python objects,
improving performance for read operations. Write operations are sent
directly to the database.
"""
import json
import sqlite3

from .file import FileManager
from .interface import BaseDataManager, DataError
from ..db.manager import DatabaseManager as DatabaseManager
from ...models.course import Course
from ...models.instructor import Instructor
from ...models.student import Student

dbm = DatabaseManager()
"""The global instance for direct, low-level database communication."""
dbm.create_tables()


class DatabaseDataManager(BaseDataManager):
    """
    Implements the data management interface using a persistent SQLite database.

    This class provides CRUD operations that interact with the database.
    It uses a class-level cache to store hydrated object models, reducing
    database queries for repeated read operations. Write operations (add, edit,
    remove) are performed directly on the database and invalidate the cache.
    """
    _cache = {}
    """Internal cache for storing hydrated data objects to minimize DB queries."""

    @staticmethod
    def get_db_path():
        """
        Gets the file path of the connected SQLite database.

        :return: The absolute path to the database file.
        :rtype: str
        """
        return dbm.db_path

    @staticmethod
    def _clear_cache():
        """Invalidates the in-memory cache, forcing a refresh from the database."""
        DatabaseDataManager._cache = {}

    @staticmethod
    def _get_hydrated_data():
        """
        Fetches all data from the database and "hydrates" it into a network of objects.

        If the cache is empty, this method reads all tables from the database,
        reconstructs the `Student`, `Instructor`, and `Course` objects, and links
        them together (i.e., enrollments). The resulting object graph and lookup
        maps are stored in the class cache for fast retrieval.

        :return: A dictionary containing lists and lookup maps of all data objects.
        :rtype: dict
        :raises DataError: If an underlying database error occurs.
        """
        if DatabaseDataManager._cache:
            return DatabaseDataManager._cache

        try:
            all_student_tuples = dbm.get_all_students()
            all_instructor_tuples = dbm.get_all_instructors()
            all_course_tuples = dbm.get_all_courses()
            all_enrollments = dbm.get_all_enrollments()

            all_students = [Student(*s) for s in all_student_tuples]
            all_instructors = [Instructor(*i) for i in all_instructor_tuples]

            all_courses = []
            instructors_map_temp = {i.instructor_id: i for i in all_instructors}
            for row in all_course_tuples:
                instructor = instructors_map_temp.get(row[2])
                if instructor:
                    course = Course(course_id=row[0], course_name=row[1], instructor=instructor)
                    all_courses.append(course)

            students_map = {s.student_id: s for s in all_students}
            instructors_map = {i.instructor_id: i for i in all_instructors}
            courses_map = {c.course_id: c for c in all_courses}

            for student_id, course_id in all_enrollments:
                student = students_map.get(student_id)
                course = courses_map.get(course_id)
                if student and course:
                    student.registered_courses.append(course)
                    course.enrolled_students.append(student)

            hydrated_data = {"students": all_students, "instructors": all_instructors, "courses": all_courses,
                             "students_map": students_map, "instructors_map": instructors_map,
                             "courses_map": courses_map, }
            DatabaseDataManager._cache = hydrated_data
            return hydrated_data
        except sqlite3.Error as e:
            raise DataError(e)

    @staticmethod
    def get_students() -> list[Student]:
        """
        Retrieves a list of all student objects from the database.

        :return: A list of all students.
        :rtype: list[Student]
        """
        DatabaseDataManager._clear_cache()
        data = DatabaseDataManager._get_hydrated_data()
        return data["students"]

    @staticmethod
    def get_student(student_id: str) -> Student:
        """
        Retrieves a single student object from the database.

        :param student_id: The ID of the student to retrieve.
        :type student_id: str
        :return: The corresponding Student object.
        :rtype: Student
        :raises DataError: If the student is not found.
        """
        DatabaseDataManager._clear_cache()
        data = DatabaseDataManager._get_hydrated_data()
        student = data["students_map"].get(student_id)
        if not student:
            raise DataError(f"Student with ID '{student_id}' not found.")
        return student

    @staticmethod
    def get_instructors() -> list[Instructor]:
        """
        Retrieves a list of all instructor objects from the database.

        :return: A list of all instructors.
        :rtype: list[Instructor]
        """
        DatabaseDataManager._clear_cache()
        data = DatabaseDataManager._get_hydrated_data()
        return data["instructors"]

    @staticmethod
    def get_instructor(instructor_id: str) -> Instructor:
        """
        Retrieves a single instructor object from the database.

        :param instructor_id: The ID of the instructor to retrieve.
        :type instructor_id: str
        :return: The corresponding Instructor object.
        :rtype: Instructor
        :raises DataError: If the instructor is not found.
        """
        DatabaseDataManager._clear_cache()
        data = DatabaseDataManager._get_hydrated_data()
        instructor = data["instructors_map"].get(instructor_id)
        if not instructor:
            raise DataError(f"Instructor with ID '{instructor_id}' not found.")
        return instructor

    @staticmethod
    def get_courses() -> list[Course]:
        """
        Retrieves a list of all course objects from the database.

        :return: A list of all courses.
        :rtype: list[Course]
        """
        DatabaseDataManager._clear_cache()
        data = DatabaseDataManager._get_hydrated_data()
        return data["courses"]

    @staticmethod
    def get_course(course_id: str) -> Course:
        """
        Retrieves a single course object from the database.

        :param course_id: The ID of the course to retrieve.
        :type course_id: str
        :return: The corresponding Course object.
        :rtype: Course
        :raises DataError: If the course is not found.
        """
        DatabaseDataManager._clear_cache()
        data = DatabaseDataManager._get_hydrated_data()
        course = data["courses_map"].get(course_id)
        if not course:
            raise DataError(f"Course with ID '{course_id}' not found.")
        return course

    @staticmethod
    def add_student(**kwargs) -> None:
        """
        Adds a new student directly to the database.

        :param kwargs: Keyword arguments representing student attributes.
        :raises DataError: If student data is invalid, the student already exists, or a DB error occurs.
        """
        try:
            s = Student(**kwargs)
        except ValueError as e:
            raise DataError(e)
        try:
            if dbm.get_student(s.student_id):
                raise DataError(f"Student with ID '{s.student_id}' already exists.")
            dbm.add_student(**kwargs)
        except sqlite3.Error as e:
            raise DataError(e)

    @staticmethod
    def edit_student(**kwargs) -> None:
        """
        Edits an existing student's information in the database.

        Requires 'student_id' in kwargs to identify the student.

        :param kwargs: Keyword arguments with fields to update.
        :raises DataError: If the student ID is missing, the student is not found, or a DB error occurs.
        """
        student_id = kwargs.get('student_id')
        if not student_id:
            raise DataError("Student ID is required.")
        try:
            if not dbm.get_student(student_id):
                raise DataError(f"Student with ID '{student_id}' not found.")
            dbm.update_student(**kwargs)
        except sqlite3.Error as e:
            raise DataError(e)

    @staticmethod
    def remove_student(student_id: str) -> None:
        """
        Removes a student from the database.

        :param student_id: The ID of the student to remove.
        :type student_id: str
        :raises DataError: If the student is not found or a DB error occurs.
        """
        try:
            if not dbm.get_student(student_id):
                raise DataError(f"Student with ID '{student_id}' does not exist.")
            dbm.delete_student(student_id)
        except sqlite3.Error as e:
            raise DataError(e)

    @staticmethod
    def add_instructor(**kwargs) -> None:
        """
        Adds a new instructor directly to the database.

        :param kwargs: Keyword arguments representing instructor attributes.
        :raises DataError: If instructor data is invalid, the instructor already exists, or a DB error occurs.
        """
        try:
            i = Instructor(**kwargs)
        except ValueError as e:
            raise DataError(e)
        try:
            if dbm.get_instructor(i.instructor_id):
                raise DataError(f"Instructor with ID '{i.instructor_id}' already exists.")
            dbm.add_instructor(**kwargs)
        except sqlite3.Error as e:
            raise DataError(e)

    @staticmethod
    def edit_instructor(**kwargs) -> None:
        """
        Edits an existing instructor's information in the database.

        Requires 'instructor_id' in kwargs to identify the instructor.

        :param kwargs: Keyword arguments with fields to update.
        :raises DataError: If the instructor ID is missing, the instructor is not found, or a DB error occurs.
        """
        instructor_id = kwargs.get('instructor_id')
        if not instructor_id:
            raise DataError("Instructor ID is required.")
        try:
            if not dbm.get_instructor(instructor_id):
                raise DataError(f"Instructor with ID '{instructor_id}' not found.")
            dbm.update_instructor(**kwargs)
        except sqlite3.Error as e:
            raise DataError(e)

    @staticmethod
    def remove_instructor(instructor_id: str) -> None:
        """
        Removes an instructor from the database.

        :param instructor_id: The ID of the instructor to remove.
        :type instructor_id: str
        :raises DataError: If the instructor is not found or a DB error occurs.
        """
        try:
            if not dbm.get_instructor(instructor_id):
                raise DataError(f"Instructor with ID '{instructor_id}' does not exist.")
            dbm.delete_instructor(instructor_id)
        except sqlite3.Error as e:
            raise DataError(e)

    @staticmethod
    def add_course(**kwargs) -> None:
        """
        Adds a new course directly to the database.

        :param kwargs: Keyword arguments representing course attributes.
        :raises DataError: If course data is invalid, the course already exists, or a DB error occurs.
        """
        try:
            c = Course(**kwargs)
        except ValueError as e:
            raise DataError(e)
        try:
            if dbm.get_course(c.course_id):
                raise DataError(f"Course with ID '{c.course_id}' already exists.")
            dbm.add_course(course_id=c.course_id, course_name=c.course_name, instructor_id=c.instructor.instructor_id)
        except sqlite3.Error as e:
            raise DataError(e)

    @staticmethod
    def edit_course(**kwargs) -> None:
        """
        Edits an existing course's information in the database.

        Requires 'course_id' in kwargs to identify the course.

        :param kwargs: Keyword arguments with fields to update.
        :raises DataError: If the course ID is missing, the course is not found, or a DB error occurs.
        """
        course_id = kwargs.get('course_id')
        if not course_id:
            raise DataError("Course ID is required.")
        try:
            if not dbm.get_course(course_id):
                raise DataError(f"Course with ID '{course_id}' not found.")
            if kwargs.get('instructor'):
                kwargs["instructor_id"] = kwargs.pop('instructor').instructor_id
            dbm.update_course(**kwargs)
        except sqlite3.Error as e:
            raise DataError(e)

    @staticmethod
    def remove_course(course_id: str) -> None:
        """
        Removes a course from the database.

        :param course_id: The ID of the course to remove.
        :type course_id: str
        :raises DataError: If the course is not found or a DB error occurs.
        """
        try:
            if not dbm.get_course(course_id):
                raise DataError(f"Course with ID '{course_id}' does not exist.")
            dbm.delete_course(course_id)
        except sqlite3.Error as e:
            raise DataError(e)

    @staticmethod
    def enroll_student(student_id: str, course_id: str) -> None:
        """
        Enrolls a student in a course by creating a database record.

        :param student_id: The ID of the student to enroll.
        :type student_id: str
        :param course_id: The ID of the course to enroll in.
        :type course_id: str
        :raises DataError: If student or course is not found, or a DB error occurs.
        """
        try:
            if not dbm.get_student(student_id):
                raise DataError(f"Student with ID '{student_id}' not found.")
            if not dbm.get_course(course_id):
                raise DataError(f"Course with ID '{course_id}' not found.")
            dbm.enroll_student(student_id, course_id)
        except sqlite3.Error as e:
            raise DataError(e)

    @staticmethod
    def data_to_json(filepath: str) -> None:
        """
        Exports all data from the database to a JSON file.

        Hydrates all database records into objects and uses a FileManager to serialize them.

        :param filepath: The path to the output JSON file.
        :type filepath: str
        """
        fm = FileManager()
        DatabaseDataManager._clear_cache()
        data = DatabaseDataManager._get_hydrated_data()
        fm.students = data["students_map"]
        fm.instructors = data["instructors_map"]
        fm.courses = data["courses_map"]
        fm.save_to_json(filepath)

    @staticmethod
    def data_from_json(filepath: str) -> None:
        """
        Imports data from a JSON file into the database, overwriting existing data.

        The process involves clearing all tables, loading the JSON into temporary
        in-memory objects, and then populating the database from these objects.

        :param filepath: The path to the input JSON file.
        :type filepath: str
        :raises DataError: If loading or populating fails.
        """
        try:
            dbm.clear_all_tables()

            datastore = FileManager()
            datastore.load_from_json(filepath)

            DatabaseDataManager._populate_db_from_file_manager(datastore)
        except (FileNotFoundError, json.JSONDecodeError, sqlite3.Error) as e:
            raise DataError(f"Failed to load data from JSON: {e}")

    @staticmethod
    def data_to_csv(dirpath: str) -> None:
        """
        Exports all data from the database to a set of CSV files.

        Hydrates all database records into objects and uses a FileManager to serialize them.

        :param dirpath: The path to the output directory.
        :type dirpath: str
        """
        datastore = FileManager()
        datastore.students = {s.student_id: s for s in DatabaseDataManager.get_students()}
        datastore.instructors = {i.instructor_id: i for i in DatabaseDataManager.get_instructors()}
        datastore.courses = {c.course_id: c for c in DatabaseDataManager.get_courses()}
        datastore.save_to_csv(dirpath)

    @staticmethod
    def data_from_csv(dirpath: str) -> None:
        """
        Imports data from CSV files into the database, overwriting existing data.

        The process involves clearing all tables, loading CSVs into temporary
        in-memory objects, and then populating the database from these objects.

        :param dirpath: The path to the input directory.
        :type dirpath: str
        :raises DataError: If loading or populating fails.
        """
        try:
            dbm.clear_all_tables()

            datastore = FileManager()
            datastore.load_from_csv(dirpath)

            DatabaseDataManager._populate_db_from_file_manager(datastore)
        except (FileNotFoundError, sqlite3.Error) as e:
            raise DataError(f"Failed to load data from CSV: {e}")

    @staticmethod
    def _populate_db_from_file_manager(file_manager: FileManager):
        """
        Helper method to populate the database from a FileManager instance.

        Iterates through the objects held by the FileManager and inserts them
        into the corresponding database tables.

        :param file_manager: A FileManager instance preloaded with data.
        :type file_manager: FileManager
        """
        for i in file_manager.instructors.values():
            dbm.add_instructor(instructor_id=i.instructor_id, name=i.name, age=i.age, email=i._email)

        for s in file_manager.students.values():
            dbm.add_student(student_id=s.student_id, name=s.name, age=s.age, email=s._email)

        for c in file_manager.courses.values():
            dbm.add_course(course_id=c.course_id, course_name=c.course_name, instructor_id=c.instructor.instructor_id)

        for s in file_manager.students.values():
            for c in s.registered_courses:
                dbm.enroll_student(student_id=s.student_id, course_id=c.course_id)
