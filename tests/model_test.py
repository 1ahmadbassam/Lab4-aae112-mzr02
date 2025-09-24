import logging
import os

from src.sms.data.dm.file import FileManager as dm
from src.sms.models.course import Course
from src.sms.models.instructor import Instructor
from src.sms.models.student import Student

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    print("\n--- School Management System Test Program ---\n")

    output_dir = "school_data_output"
    os.makedirs(output_dir, exist_ok=True)
    json_file_path = os.path.join(output_dir, "school_data.json")
    csv_dir_path = os.path.join(output_dir, "csv_data")
    os.makedirs(csv_dir_path, exist_ok=True)

    print("--- Phase 1: Creating objects and demonstrating validation ---\n")

    prof_smith = Instructor("Dr. Emily Smith", 45, "e.smith@university.edu", "199801234")
    prof_jones = Instructor("Dr. Alan Jones", 52, "a.jones@university.edu", "199505678")

    student_john = Student("John Doe", 20, "john.doe@lau.edu", "202401111")
    student_jane = Student("Jane Dane", 21, "jane.dane@lau.edu", "202302222")
    student_ali = Student("Ali Hassan", 22, "ali.hassan@lau.edu", "202203333")

    print("Successfully created instructors and students.")

    try:
        print("\nAttempting to create a student with an invalid ID (should fail)...")
        invalid_student = Student("Invalid Person", 25, "invalid@email.com", "123")
    except ValueError as e:
        print(f"SUCCESS: Caught expected error as planned: {e}")

    print("\n--- Phase 2: Registering students for courses ---\n")

    # Create courses, which automatically assign themselves to the instructor
    course_eece230 = Course("EECE230", "Software Engineering", prof_smith)
    course_math201 = Course("MATH201", "Calculus III", prof_jones)

    student_john.register_course(course_eece230)
    student_jane.register_course(course_eece230)
    student_jane.register_course(course_math201)
    student_ali.register_course(course_math201)

    print("Initial state of objects:")
    print(repr(student_jane))
    print(repr(course_eece230))
    print("-" * 20)

    print("\n--- Phase 3: Saving data to JSON and CSV ---\n")

    data_manager = dm()
    data_manager.instructors = {i.instructor_id: i for i in [prof_smith, prof_jones]}
    data_manager.students = {s.student_id: s for s in [student_john, student_jane, student_ali]}
    data_manager.courses = {c.course_id: c for c in [course_eece230, course_math201]}

    data_manager.save_to_json(json_file_path)
    data_manager.save_to_csv(csv_dir_path)

    print("\n--- Phase 4: Loading data from JSON and verifying ---\n")

    new_data_manager = dm()
    new_data_manager.load_from_json(json_file_path)

    print("Data loaded into new DataManager. Verifying content...")

    if len(new_data_manager.students) == 3 and len(new_data_manager.courses) == 2:
        print("SUCCESS: Correct number of students and courses loaded.")
    else:
        print("FAILURE: Incorrect number of items loaded.")

    print("\nVerifying re-linked data for Jane (ID: 202302222):")
    loaded_jane = new_data_manager.students.get("202302222")
    if loaded_jane:
        print(repr(loaded_jane))
        if len(loaded_jane.registered_courses) == 2:
            print("SUCCESS: Jane's course registrations were loaded correctly.")
        else:
            print("FAILURE: Jane's course registration data is incorrect.")
    else:
        print("FAILURE: Could not find Jane in the loaded data.")

    print("\n--- Test Program Finished ---")


if __name__ == "__main__":
    main()
