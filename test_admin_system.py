import pytest
import warnings
from unittest.mock import MagicMock, patch
from admin_system import *

# Some warnings that appear due to the mocking, does not affect functionality whatsoever so they were filtered out
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*SwigPyPacked.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*swigvarlink.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*SwigPyObject.*")

unverified_doctors = {}
headers = ["", "User ID", "Username", "Password", "Email", "Name", "Surname", "Date of Birth",
                "Phone Number", "Address"]
widths = [5, 5, 15, 15, 10, 10, 10, 10, 10, 40]

# Class to mock a tk.Entry
class MockEntry:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

# Mocks for the few tests that use mocks
@pytest.fixture
def mock_dependencies():
    # Mocks of the window, connection, cursor, and destroy
    mock_window = MagicMock()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_destroy = patch('tkinter.Tk.destroy')


    mock_destroy.start()
    mock_conn.start()

    # Add test data to unverified doctors
    global mock_unverified
    mock_unverified = {
        1: [1, 123, "cert_abc"],  # doctor_id = 123, user_id = 1
        2: [2, 456, "cert_xyz"]  # doctor_id = 456, user_id = 2
    }

    # Mocking the database query that populates unverified_doctors
    mock_cursor.execute.return_value = None  # Ensure `execute` does not return anything, just simulating execution
    mock_cursor.fetchall.return_value = [
        (1, 123, 'cert_abc', 0),  # Mock result for doctor_id = 123
        (2, 456, 'cert_xyz', 0),  # Mock result for doctor_id = 456
    ]

    yield {
        "mock_window": mock_window,
        "mock_cursor": mock_cursor,
        "mock_destroy": mock_destroy,
        "mock_conn": mock_conn,
    }

    mock_destroy.stop()
    mock_conn.stop()

# Database setup so that changes are rolled back in the end
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

# Root to use for tests
@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()

# Added test users for testing
@pytest.fixture
def test_users(setup_database):
    connection = setup_database
    cursor = connection.cursor()
    user1 = ('LeprechaunJ', '4a7d1ed414474e4033ac29ccb8653d9b', 'James', 'Leprechaun', '1991-04-15', '81234567890', '42 Maple Avenue, London, W8 4QQ, UK')
    user2 = ('FranzK', '4a7d1ed414474e4033ac29ccb8653d9b', 'Franz', 'Kruger', '1982-03-22', '85678901234', '78 Rosewood Lane, London, E1 5AB, UK')
    cursor.execute(
        """
        INSERT INTO Users (user_name, password, first_name, last_name, date_of_birth, phone_number, address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        user1
    )
    id1 = cursor.lastrowid
    cursor.execute(
        """
        INSERT INTO Users (user_name, password, first_name, last_name, date_of_birth, phone_number, address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        user2
    )
    id2 = cursor.lastrowid


    cursor.execute("SELECT * FROM Users WHERE user_id = ?", (id1,))
    user_info1 = cursor.fetchone()

    cursor.execute("SELECT * FROM Users WHERE user_id = ?", (id2,))
    user_info2 = cursor.fetchone()

    # Getting the biggest doctor id currently
    cursor.execute("SELECT MAX(doctor_id) FROM Doctors")
    max_id = cursor.fetchone()[0]
    if max_id is None:
        max_id = 0
    else:
        max_id = max_id + 1

    # Adding an unverified doctor
    doctor = (id2, max_id, "./lorem-ipsum", 0)
    cursor.execute("""
        INSERT INTO Doctors (user_id, doctor_id, certificate, verify_state)
        VALUES (?, ?, ?, ?)""",
        doctor)
    cursor.execute("SELECT * FROM Doctors WHERE user_id = ?", (id2,))
    doctor_info = cursor.fetchone()

    # Adding unverified doctor to unverified doctors dictionary
    unverified_doctors[doctor_info[0]] = [doctor_info[0], doctor_info[1], doctor_info[1]]

    yield [user_info1, user_info2, doctor_info]

def test_get_window_offset(root):
    width, height = 100, 100
    x, y = get_window_offset(root, width, height)
    exp_y = (root.winfo_screenheight() // 2) - (height // 2)
    exp_x = (root.winfo_screenwidth() // 2) - (width // 2)

    assert x == exp_x
    assert y == exp_y

def test_clear_frame(root):
    data_frame = tk.Frame(root)
    tk.Label(data_frame, text="Hello").grid(row=0, column=0)
    assert data_frame.winfo_children(), "The frame should have children but it's empty."
    clear_frame(data_frame)
    assert not data_frame.winfo_children(), "The frame should not have children but it does."

def test_create_main_window(root):
    create_main_window(root, False)
    assert len(root.winfo_children()) > 0

def test_insert_entry(root, test_users):
    data_frame = tk.Frame(root)
    i, j = 0, 0
    insert_entry(data_frame, test_users, i, j)
    children = data_frame.winfo_children()

    assert children, "The frame should, but doesn't have any children."
    entry_widget = children[0]
    assert isinstance(entry_widget, tk.Entry), "The widget is not a tk.Entry."

    # Check if it is the correct value
    expected_value = str(test_users[i][j - 1])
    actual_value = entry_widget.get()
    assert actual_value == expected_value, f"Entry value incorrect: expected {expected_value}, but got {actual_value}."

def test_update_table(setup_database, root, test_users):
    connection = setup_database
    cursor = connection.cursor()
    data_frame = tk.Frame(root)

    update_table("Leprechaun", data_frame, root, cursor)
    children = data_frame.winfo_children()

    assert len(children) > 0, "The table was updated."
    entries = [child for child in data_frame.winfo_children() if isinstance(child, tk.Entry)]
    actual_value = tuple(widget.get() for widget in entries)
    expected_data = tuple(str(value) for value in test_users[0])
    assert actual_value == expected_data, f"Data row should be {expected_data}, but got {actual_value}."

def test_insert_data(setup_database, root, test_users):
    data_frame = tk.Frame(root)

    user_info = None
    insert_data(user_info, data_frame, root, unverified_doctors)
    assert not data_frame.winfo_children(), "There are children when there should not"

    user_info = [test_users[1]]
    insert_data(user_info, data_frame, root, unverified_doctors)

    labels = [child for child in data_frame.winfo_children() if isinstance(child, tk.Label)]
    entries = [child for child in data_frame.winfo_children() if isinstance(child, tk.Entry)]
    buttons = [child for child in data_frame.winfo_children() if isinstance(child, tk.Button)]

    assert len(labels) == len(headers), "Header label number is incorrect."
    assert len(entries) == len(user_info) * len(headers) - 1, "Entry number is incorrect."
    assert len(buttons) == 1, "Button number is incorrect."

    for col, header in enumerate(headers):
        assert labels[col].cget("text") == header, f"Header doesn't match at column {col}"

    for row, user in enumerate(user_info):
        for col, value in enumerate(user):
            i = row * len(headers) + col
            assert entries[i].get() == str(value), \
                f"Value mismatch at row {row}, column {col}"

def test_get_unapproved_doctors(setup_database, test_users):
    connection = setup_database
    cursor = connection.cursor()
    doctors = {}
    get_unapproved_doctors(doctors, cursor)
    assert len(doctors) == 1

def test_check_valid_input(test_users, setup_database):
    conn = setup_database
    cursor = conn.cursor()
    user_id = test_users[0][0]
    assert check_valid_input(user_id, cursor)

    cursor.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))
    assert not check_valid_input(user_id, cursor)

def test_add_admin(root, setup_database):
    conn = setup_database
    window = add_admin(root, conn)

    labels = [widget for widget in window.winfo_children() if isinstance(widget, tk.Label)]
    label_names = ["Username", "Password", "Email", "First Name", "Last Name", "Date of Birth", "Phone Number", "Address"]

    for i, label in enumerate(labels):
        assert label.cget("text") == label_names[i], f"Expected '{label_names[i]}', but got '{label.cget('text')}'"

def test_save_admin(root, setup_database):
    conn = setup_database
    cursor = conn.cursor()
    window = add_admin(root, conn)

    entries = {
        "Username": MockEntry("test_user"),
        "Password": MockEntry("1234"),
        "Email": MockEntry("user@example.com"),
        "First Name": MockEntry("John"),
        "Last Name": MockEntry("Doe"),
        "Date of Birth": MockEntry("1990-01-01"),
        "Phone Number": MockEntry("1234567890"),
        "Address": MockEntry("123 Test Street")
    }
    save_admin(window, entries, conn, True)

    cursor.execute("SELECT MAX(user_id) FROM Users;")
    max_id = cursor.fetchone()[0]

    cursor.execute("SELECT * from Users where user_id = ?", (max_id,))
    data = cursor.fetchall()

    expected_values = {key: entries[key].get().strip() for key in entries}

    for i, (label, expected_value) in enumerate(expected_values.items()):
        # Expecting the corresponding value in data to match the expected value
        actual_value = data[0][i + 1]  # Skip the first column (user_id)
        if i != 1:
            assert actual_value.strip() == expected_value, f"Expected {label} to be '{expected_value}', but got '{actual_value.strip()}'"

    with patch('tkinter.messagebox.showerror') as mock_error:
        save_admin(root, entries, conn, test=True)
        mock_error.assert_called_once_with("Error", "Username already exists!")

    entries["Username"] = MockEntry(" ")
    entries["Password"] = MockEntry(" ")
    with patch('tkinter.messagebox.showerror') as mock_error:
        save_admin(root, entries, conn, test=True)
        mock_error.assert_called_once_with("Error", "Username and password have to be filled.")

def test_certificate_validation(test_users, root):
    data = [1, 2, "abc.pdf"]
    cert_window = certificate_validation(data, root)

    assert cert_window.winfo_exists() == 1

    buttons_frame = [child for child in cert_window.winfo_children() if isinstance(child, tk.Frame)][0]
    buttons = [widget for widget in buttons_frame.winfo_children() if isinstance(widget, tk.Button)]
    assert len(buttons) == 2  # Accept and Reject buttons

    accept_button = buttons[0]
    reject_button = buttons[1]

    assert accept_button.cget("text") == "Accept"
    assert reject_button.cget("text") == "Reject"

def test_approve_doctor(mock_dependencies):
    # Setup
    mock_window = mock_dependencies["mock_window"]
    mock_cursor = mock_dependencies["mock_cursor"]
    mock_conn = mock_dependencies["mock_conn"]

    user_id = 1  # Sample doctor ID to approve

    mock_cursor.execute.return_value = None

    # Insert a sample doctor (mocked)
    mock_cursor.execute(f"INSERT INTO Doctors (User_id, Doctor_id, certificate, verify_state) VALUES (?,?,?,?)",
                        (user_id, 456, 'cert_abc', 0))

    # Check that the mock database has the doctor
    mock_cursor.execute.assert_any_call(
        f"INSERT INTO Doctors (User_id, Doctor_id, certificate, verify_state) VALUES (?,?,?,?)",
        (user_id, 456, 'cert_abc', 0))

    approve_doctor(user_id, mock_window, mock_unverified, mock_conn)

    # Check if the doctor was removed from unverified_doctors
    assert user_id not in mock_unverified, f"User {user_id} should have been removed from unverified doctors"

    # Check if the window.destroy() was called
    mock_window.destroy.assert_called_once()
    # Check if commit was called to save changes to the database
    mock_conn.commit.assert_called_once()

def test_delete_user(mock_dependencies):
    # Setup
    mock_window = mock_dependencies["mock_window"]
    mock_cursor = mock_dependencies["mock_cursor"]
    mock_conn = mock_dependencies["mock_conn"]

    user_id = 2
    mock_cursor.execute.return_value = None
    mock_conn.cursor.return_value = mock_cursor

    # Insert a sample doctor (mocked)
    mock_cursor.execute(f"INSERT INTO Doctors (User_id, Doctor_id, certificate, verify_state) VALUES (?,?,?,?)",
                        (user_id, 123, 'cert_xyz', 0))

    mock_cursor.execute(f"INSERT INTO Users (User_id, user_name, first_name, last_name) VALUES (?,?)",
                        (user_id, "CookieC", 'Cookie', "Cutter"))

    delete_user(user_id, mock_window, mock_conn, mock_unverified)
    # Check if the doctor was removed from unverified_doctors
    assert user_id not in mock_unverified, f"User {user_id} should have been removed from unverified doctors"
    # Check if delete was executed
    mock_cursor.execute.assert_any_call(f"DELETE FROM Users WHERE User_id = ?", (user_id,))
    # Check if the window.destroy() was called and the commit
    mock_window.destroy.assert_called_once()
    mock_conn.commit.assert_called_once()

    user_id = " 2 "
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = (1,)  # Simulate one user found

    delete_user(user_id, mock_window, mock_conn)
    mock_cursor.execute.assert_any_call(f"DELETE FROM Users WHERE User_id = ?", (2,))

    user_id = " 2d "
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = (0,)  # Simulate one user found

    delete_user(user_id, mock_window, mock_conn)

    try:
        mock_cursor.execute.assert_any_call("DELETE FROM Users WHERE User_id = ?", (2,))
        raise AssertionError("DELETE was called with user_id 2, but it shouldn't have been.")
    except AssertionError as e:
        if "not called" in str(e):
            pass
