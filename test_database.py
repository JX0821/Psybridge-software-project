"""
Authors:
Joris Nouwens.

Tests done:
1. Do all tables exist?
2. In these tables, do all columns exist and no extra?
3. Does every table contain data? (to make sure no data is erased by accident)
4. Are all links to another table still working? (or is an entry in a table removed and does something still refer to the deleted entry)
5. Are the addresses formatted correctly in the user table?
5. Are the dates of birth formatted correctly in the user table?

Currently the test 'test_table_data_present' fails. This is on purpose.
Because no questionaire has been filled in at this stage. Only one patient needs to fill in a questionaire to turn the failed into a pass.
"""


import sqlite3
import pytest

TABLES = ["Admins",
          "Appointment_details",
          "Diagnoses",
          "Diagnosis",
          "Doctors",
          "Duration",
          "Employees",
          "Fills_in",
          "has_access_to",
          "Have",
          "Meets",
          "Patients",
          "Question_answers",
          "Question_options",
          "Questionaire",
          "Questionaire_responses",
          "Questions",
          "Treats",
          "Users"]

TABLE_COLUMNS = {
    "Users": ["User_id", "User_name", "Password", "Email", "First_name",
              "Last_name", "Date_of_birth", "Phone_number", "Address"],
    "Employees": ["User_id", "Employee_id"],
    "Admins": ["User_id", "Admin_id"],
    "Doctors": ["User_id", "Doctor_id", "certificate", "verify_state"],
    "Patients": ["User_id", "Patient_id"],
    "Duration": ["Duration_id", "Start_date", "End_date"],
    "Diagnosis": ["Diagnose_id", "Diagnose_date", "Diagnose"],
    "Appointment_details": ["Examination_id", "Date_last_modified", "Date_of_meeting",
                             "Location", "Confirmed", "Treatment_notes", "Time_of_meeting"],
    "Treats": ["Patient_id", "Doctor_id", "Duration_id"],
    "Diagnoses": ["Patient_id", "Doctor_id", "Diagnose_id"],
    "Meets": ["Patient_id", "Doctor_id", "Examination_id"],
    "Questionaire_responses": ["Questionaire_id", "Questionaire_date", "Attempt_id"],
    "Question_answers": ["Attempt_id", "Answer", "Question_id", "Answer_id"],
    "Questionaire": ["Questionaire_id", "Questionaire_name"],
    "Questions": ["Question_number", "Question", "Questionaire_id"],
    "Have": ["Question_number", "Option_id"],
    "Question_options": ["Option_id", "Answer", "Question_number"],
    "has_access_to": ["Patient_id", "Questionaire_id"],
    "Fills_in": ["Patient_id", "Questionaire_id", "Attempt_id"],
}

# relationships (child_table (table which contains the FOREIGN KEY), parent_table (table which is referred to by the FOREIGN KEY), foreign_key_child, foreign_key_parent)
RELATIONSHIPS = [
    ("Employees", "Users", "User_id", "User_id"),
    ("Admins", "Employees", "User_id", "User_id"),
    ("Doctors", "Employees", "User_id", "User_id"),
    ("Patients", "Users", "User_id", "User_id"),
    ("Treats", "Duration", "Duration_id", "Duration_id"),
    ("Treats", "Doctors", "Doctor_id", "Doctor_id"),
    ("Treats", "Patients", "Patient_id", "Patient_id"),
    ("Diagnoses", "Diagnosis", "Diagnose_id", "Diagnose_id"),
    ("Diagnoses", "Doctors", "Doctor_id", "Doctor_id"),
    ("Diagnoses", "Patients", "Patient_id", "Patient_id"),
    ("Meets", "Appointment_details", "Examination_id", "Examination_id"),
    ("Meets", "Doctors", "Doctor_id", "Doctor_id"),
    ("Meets", "Patients", "Patient_id", "Patient_id"),
    ("Question_answers", "Questionaire_responses", "Attempt_id", "Attempt_id"),
    ("Questions", "Questionaire", "Questionaire_id", "Questionaire_id"),
    ("Have", "Questions", "Question_number", "Question_number"),
    ("Have", "Question_options", "Option_id", "Option_id"),
    ("Question_options", "Questions", "Question_number", "Question_number"),
    ("has_access_to", "Patients", "Patient_id", "Patient_id"),
    ("has_access_to", "Questionaire", "Questionaire_id", "Questionaire_id"),
    ("Fills_in", "Patients", "Patient_id", "Patient_id"),
    ("Fills_in", "Questionaire", "Questionaire_id", "Questionaire_id"),
    ("Fills_in", "Questionaire_responses", "Attempt_id", "Attempt_id"),
]

@pytest.fixture
def setup_database():
    """
    This function creates a connection with the database for testing.
    There is a rollback at the end to prevent changes to the database induced by testing.
    """
    connection = sqlite3.connect("Database.db")
    # Turns off automatic commits, to make sure the changes can be reverted.
    connection.isolation_level = None
    cursor = connection.cursor()
    # Start a transaction which will never be committed.
    cursor.execute("BEGIN;")
    yield connection
    # Rollback to revert changes
    cursor.execute("ROLLBACK;")
    connection.close()

def test_tables_exist(setup_database):
    """
    This test checks whether all tables are present in the database.
    """
    cursor = setup_database.cursor()
    for table in TABLES:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
        assert cursor.fetchone() is not None, f"Table {table} does not exist"


def test_table_columns_exist(setup_database):
    """
    This test checks whether all tables have the expected columns.
    """
    connection = setup_database
    cursor = connection.cursor()
    for table_name, expected_columns in TABLE_COLUMNS.items():
        # Retreive all columns per table, currently in the database.
        cursor.execute(f"PRAGMA table_info({table_name});")
        actual_columns = [row[1] for row in cursor.fetchall()]
        # Find all missing columns
        missing_columns = set(expected_columns) - set(actual_columns)
        assert not missing_columns, f"Tabel {table_name} is missing these columns: {missing_columns}"
        # Find extra columns
        extra_columns = set(actual_columns) - set(expected_columns)
        assert not extra_columns, f"Tabel {table_name} has these columns extra: {extra_columns}"

def test_table_data_present(setup_database):
    """
    This test checks if there is data in all tables and returns a list of tables which are empty.

    Currently ['Fills_in', 'Question_answers', 'Questionaire_responses'] are empty,
    so right now this test is supposed to fail.
    Normally questionaires are filled out, so then this test shouldn't fail.
    Fill out one questionaire to make this fail a pass.
    """
    cursor = setup_database.cursor()
    empty_tables = []
    for table in TABLES:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        row_count = cursor.fetchone()[0]
        if row_count == 0:
            empty_tables.append(table)
    assert not empty_tables, f"The following tables are empty: {empty_tables}"

def test_orphan_rows(setup_database):
    """
    Test to see if every entry has the required relations.
    If for example an entry in one table is deleted, is there then an orphan which refers to the deleted entry (which of course would be a bad thing)
    """
    cursor = setup_database.cursor()
    for child_table, parent_table, foreign_key_child, foreign_key_parent in RELATIONSHIPS:
        # Check orphan rows in child pointing to parent
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM {child_table} AS c
            LEFT JOIN {parent_table} AS p ON c.{foreign_key_child} = p.{foreign_key_parent}
            WHERE p.{foreign_key_parent} IS NULL;
        """)
        orphan_count = cursor.fetchone()[0]
        assert orphan_count == 0, f"Orphan rows found in {child_table} pointing to {parent_table}"

def test_address_column_format(setup_database):
    """
    Data from address column in the user table has a specific format.
    Here is tested if all data has this format.

    Format:
    str(street, city, postal code, country)
    """
    cursor = setup_database.cursor()
    cursor.execute("SELECT Address FROM Users;")
    for row in cursor.fetchall():
        address = row[0]
        assert address.count(",") == 3, f"Invalid address format: {address}"

def test_date_of_birth_format(setup_database):
    """
    Checks if all dates of birth are valid
    """
    cursor = setup_database.cursor()
    cursor.execute("SELECT Date_of_birth FROM Users;")
    for row in cursor.fetchall():
        dob = row[0]
        parts = dob.split("-")

        assert len(parts) == 3, f"Invalid date format: {dob}"
        day, month, year = parts

        assert day.isdigit() and 1 <= int(day) <= 31, f"Invalid day in {dob}"
        assert month.isdigit() and 1 <= int(month) <= 12, f"Invalid month in {dob}"
        assert year.isdigit() and (year.startswith("19") or year.startswith("20")), f"Invalid year in {dob}"
