# School Management System (SMS)

## Project Description

The School Management System (SMS) is a robust desktop application designed to manage students, instructors, and courses. It is built with a clean, decoupled architecture that separates the core business logic (models), data persistence, and user interface into distinct layers.

This project emphasizes a flexible data backend, allowing the application to run using either an in-memory/file-based datastore or a persistent SQLite database. The system is designed to be scalable and maintainable, with a clear separation of concerns between different modules.

### Core Features (Backend & Data Layer)
* **Object-Oriented Design:** Core entities like `Student`, `Instructor`, and `Course` are modeled as Python classes with well-defined attributes and methods.
* **Data Validation:** A dedicated validation module ensures data integrity for inputs like names, IDs, and email addresses before they are entered into the system.
* **Abstracted Data Layer:** An abstract base class defines a common interface for data operations, allowing the application to seamlessly switch between different storage backends (e.g., in-memory or database).
* **SQLite Database Integration:** Includes a persistent storage option using a relational SQLite database with a well-defined schema.
* **Data Export/Import:** Functionality to export the current data to JSON or CSV formats, and import data from those files into the database.
* **Database Backup:** A simple utility to back up the live SQLite database file to a safe location.

## Project Structure

The project is organized into a standard Python package structure to ensure maintainability and clarity.

```
.
|-- docs/                 # Sphinx documentation files
|-- src/                  # Main source code for the application
|   |-- sms/              # The core Python package for the system
|   |   |-- data/         # Handles all data persistence (database, files)
|   |   |   |-- db/       # Low-level SQLite database logic
|   |   |   -- dm/        # High-level data manager interfaces (abstract and concrete)
|   |   |-- models/       # Core data models (Person, Student, etc.) 
|   |   |-- utils/        # Utility modules like the validator 
|   |-- main.py           # Main entry point to run the application
|   -- config.py          # Configuration settings 
|-- tests/                # Tests for models 
|-- .gitignore            # Specifies files to be ignored by Git 
|-- requirements.txt      # Lists project dependencies for pip 
-- README.md              # This file
```

## Setup and Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The primary way to run the application is through the main entry point.

* **To run the application**
    ```bash
    python src/main.py
    ```

* **To initialize the database schema directly (if needed):**
    ```bash
    python src/sms/data/db/manager.py
    ```
