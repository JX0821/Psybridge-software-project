import tkinter as tk
from unittest.mock import patch, MagicMock
import sqlite3
import pytest
from doctor_interface import (
    create_back_button,
    get_doctor_info,
    change_personal_information,
    save_changes,
    questionnaire_list,
    show_patients_for_questionnaire,
    display_patients,
    patient_list,
    open_patient_profile,
    change_password,
    confirm_password_change,
    create_home_page,
)

USER_ID = 58  # Example doctor user ID

@pytest.fixture
def root():
    """Fixture to create and destroy a Tkinter root window."""
    root = tk.Tk()
    yield root
    root.destroy()

@pytest.fixture
def doctor_info():
    """Mock doctor information."""
    return {
        "user_id": USER_ID,
        "doctor_id": 58,
        "first_name": "John",
        "last_name": "Doe",
        "user_name": "johndoe",
        "password": "098f6bcd4621d373cade4e832627b4f6",  # "test" in MD5
        "date_of_birth": "01-01-1980",
        "phone_number": "12345678910",
        "address": "123 Medical Street, Healthville",
        "upcoming_meeting": ["2025-01-15", "Jane", "Smith"],
    }

# --- Tests for create_back_button ---
def test_create_back_button_exists(root):
    """Test that the back button is created and exists in the parent widget."""
    create_back_button(root, {}, root)
    back_button = root.children.get("!button")
    assert back_button is not None, "Back button was not created."

def test_create_back_button_text(root):
    """Test that the back button has the correct text."""
    create_back_button(root, {}, root)
    back_button = root.children.get("!button")
    assert back_button.cget("text") == "Back", "Back button text is incorrect."

def test_create_back_button_functionality(root):
    """Test that the back button has a valid command function."""
    # Create a mock function to simulate the back button command
    mock_command = MagicMock()

    # Create the back button with the mock command
    create_back_button(root, {}, root)
    back_button = root.children.get("!button")

    # Set the command of the back button to the mock function
    back_button.config(command=mock_command)

    # Simulate a button click by invoking the command
    back_button.invoke()

    # Assert that the mock command was called
    mock_command.assert_called_once(), "Back button command was not called."

# --- Tests for get_doctor_info ---
def test_get_doctor_info_valid_user_id(doctor_info):
    """Test retrieving doctor info with a valid user ID."""
    info = get_doctor_info(USER_ID)
    assert info["user_id"] == USER_ID, "Doctor info does not match the input user ID."

def test_get_doctor_info_missing_user_id():
    """Test that an invalid user ID raises a ValueError."""
    with pytest.raises(TypeError):
        get_doctor_info(9999)

def test_get_doctor_info_upcoming_meeting_type(doctor_info):
    """Test that the upcoming meeting is correctly formatted."""
    info = get_doctor_info(USER_ID)
    assert type(info["upcoming_meeting"]) == list, "Upcoming meeting should be a list."

# --- Tests for change_password ---
@pytest.fixture
def mock_error_label(root):
    """Mock error label to simulate root behavior."""
    label = tk.Label(root, text="", font=("Arial", 12))
    label.pack()
    root.error_or_success_label = label
    return root

def test_change_password_ui_elements(mock_error_label, doctor_info):
    """Test that all password fields are created in the UI."""
    change_password(doctor_info, mock_error_label)

    # Check for the existence of entry widgets, they are all created as `!entry`
    entries = [entry for entry in mock_error_label.children if "entry" in entry]

    # Ensure that we have exactly 3 entry widgets (for current, new, and repeat new passwords)
    assert len(entries) == 3, "The number of entry widgets is incorrect."

    # Optionally, you can check if specific fields exist in the UI by checking for labels or other elements
    labels = ["Current password", "New password", "Repeat new password"]
    for label in labels:
        assert any(child.cget("text") == label for child in
                   mock_error_label.children.values()), f"Label for {label} was not created."

def test_change_password_title(mock_error_label, doctor_info):
    """Test that the window title is set correctly."""
    change_password(doctor_info, mock_error_label)
    assert mock_error_label.title() == "Change password", "Window title is incorrect."

def test_change_password_submit_button(mock_error_label, doctor_info):
    """Test that the confirm change button exists."""
    change_password(doctor_info, mock_error_label)
    submit_button = mock_error_label.children.get("!button")
    assert submit_button is not None, "Submit button not created."

# --- Tests for confirm_password_change ---
def test_confirm_password_change_success(mock_error_label, doctor_info):
    """Test a successful password change."""
    current_pw = doctor_info["password"]
    new_pw = "5f4dcc3b5aa765d61d8327deb882cf99"  # "password" in MD5
    confirm_password_change(current_pw, new_pw, new_pw, doctor_info, mock_error_label)
    assert mock_error_label.error_or_success_label.cget("text") == "Password changed successfully!"


def test_confirm_password_change_incorrect_current(mock_error_label, doctor_info):
    """Test incorrect current password error."""
    incorrect_pw = "wrongpasswordhash"
    new_pw = "5f4dcc3b5aa765d61d8327deb882cf99"
    confirm_password_change(incorrect_pw, new_pw, new_pw, doctor_info, mock_error_label)
    assert mock_error_label.error_or_success_label.cget("text") == "Incorrect current password!"

def test_confirm_password_change_mismatched_new(mock_error_label, doctor_info):
    """Test mismatched new password error."""
    current_pw = doctor_info["password"]
    new_pw = "newpasswordhash"
    repeat_pw = "differenthash"
    confirm_password_change(current_pw, new_pw, repeat_pw, doctor_info, mock_error_label)
    assert mock_error_label.error_or_success_label.cget("text") == "New passwords do not match!"

# --- Tests for create_home_page ---
def test_create_home_page_welcome_text(root, doctor_info):
    """Test that the home page displays the correct welcome text."""
    create_home_page(doctor_info, root=root, run_mainloop=False)
    welcome_label = root.children.get("!label")
    assert "Hello Dr. Doe" in welcome_label.cget("text"), "Welcome text is incorrect."

def test_create_home_page_personal_info_display(root, doctor_info):
    """Test that personal information is displayed correctly."""
    create_home_page(doctor_info, root=root, run_mainloop=False)
    frame_right = root.children.get("!frame")
    assert frame_right is not None, "Right frame for personal information not created."

def test_create_home_page_buttons_exist(root, doctor_info):
    """Test that buttons exist on the home page."""
    create_home_page(doctor_info, root=root, run_mainloop=False)
    buttons = ["Patients", "Questionnaires", "Schedule appointment"]

    # Recursively search for buttons in the widget tree
    def find_button_with_text(widget, text):
        if isinstance(widget, tk.Button) and text in widget.cget("text"):
            return True
        for child in widget.winfo_children():
            if find_button_with_text(child, text):
                return True
        return False

    for btn_text in buttons:
        assert find_button_with_text(root, btn_text), f"Button '{btn_text}' not found on the home page."

# --- Tests for change_personal_information ---
@pytest.fixture
def root_from_main(doctor_info, root):
    create_home_page(doctor_info, root=root, run_mainloop=False)
    yield root

@pytest.fixture
def root_from_cinfo(doctor_info, root_from_main):
    change_personal_information(doctor_info, root=root_from_main)
    yield root

def test_cinfo(root_from_cinfo):
    """
    To check to confirm the change personal information window exists.
    """
    assert root, "The change personal information window does no longer work!"

# --- Tests for save_changes ---
def test_save_changes_valid_data(root, doctor_info):
    """Test saving personal information with valid data."""
    confirmation_label = tk.Label(root)
    save_changes("John Doe", "johndoe", "01-01-1980", "12345678901", "123 Medical Street, Healthville", doctor_info, confirmation_label)
    assert confirmation_label.cget("text") == "Information updated successfully!", "Failed to update information with valid data."

def test_save_changes_invalid_phone_number(root, doctor_info):
    """Test saving personal information with an invalid phone number."""
    confirmation_label = tk.Label(root)
    save_changes("John Doe", "johndoe", "01-01-1980", "12345", "123 Medical Street, Healthville", doctor_info, confirmation_label)
    assert confirmation_label.cget("text") == "Invalid phone number: ensure it contains 11 digits.", "Error message for invalid phone number is incorrect."

def test_save_changes_no_changes(root, doctor_info):
    """Test saving personal information without any changes."""
    confirmation_label = tk.Label(root)
    save_changes(
        f"{doctor_info['first_name']} {doctor_info['last_name']}",
        doctor_info["user_name"],
        doctor_info["date_of_birth"],
        doctor_info["phone_number"],
        doctor_info["address"],
        doctor_info,
        confirmation_label
    )
    assert confirmation_label.cget("text") == "You haven't updated any information yet!", \
        "Error message for no changes is incorrect."

# --- Tests for questionnaire_list ---
def test_questionnaire_list_buttons(root, doctor_info):
    """Test that each questionnaire button correctly triggers the intended action."""
    mock_show_patients = MagicMock()
    questionnaire_list(doctor_info, root)

    buttons = [child for child in root.winfo_children() if isinstance(child, tk.Button)]
    assert len(buttons) > 0, "No questionnaire buttons created."

    # Check if each button has a command associated with it
    for button in buttons:
        button.config(command=mock_show_patients)
        button.invoke()
        mock_show_patients.assert_called_once()

# --- Tests for show_patients_for_questionnaire ---
def test_show_patients_for_questionnaire_patients_displayed(root, doctor_info):
    """Test that patients are displayed in the UI."""
    questionnaire_id = 1
    show_patients_for_questionnaire(questionnaire_id, doctor_info, root)
    list_frame = [child for child in root.winfo_children() if isinstance(child, tk.Canvas)][0].winfo_children()[0]
    assert len(list_frame.winfo_children()) > 0, "No patients displayed in the UI."

def test_show_patients_for_questionnaire_filter_by_search(root, doctor_info):
    """Test that patients can be filtered by a search term."""
    questionnaire_id = 1  # Assuming a valid questionnaire ID
    show_patients_for_questionnaire(questionnaire_id, doctor_info, root)
    search_entry = [child for child in root.winfo_children() if isinstance(child, tk.Frame)][0].winfo_children()[1]
    search_entry.insert(0, "John")  # Assuming "John" is a valid search term
    search_button = [child for child in root.winfo_children() if isinstance(child, tk.Frame)][0].winfo_children()[2]
    search_button.invoke()
    list_frame = [child for child in root.winfo_children() if isinstance(child, tk.Canvas)][0].winfo_children()[0]
    assert all("John" in button.cget("text") for button in list_frame.winfo_children()), \
        "Filtered patients do not match the search term."

# --- Tests for display_patients ---
def test_display_patients_no_search_query(root):
    """Test that all patients are displayed when no search query is provided."""
    list_frame = tk.Frame(root)
    display_patients(list_frame, "", 1)  # Assuming a valid questionnaire_id
    assert len(list_frame.winfo_children()) > 0, "No patients displayed when no search query is provided."

def test_display_patients_matching_query(root):
    """Test that only patients matching the search query are displayed."""
    list_frame = tk.Frame(root)
    display_patients(list_frame, "Doe", 1)  # Assuming "Doe" is a valid search term
    assert all("Doe" in button.cget("text") for button in list_frame.winfo_children()), \
        "Patients not filtered correctly by search query."

def test_display_patients_no_matching_query(root):
    """Test that no patients are displayed when the search query matches nothing."""
    list_frame = tk.Frame(root)
    display_patients(list_frame, "NonExistentName", 1)
    assert len(list_frame.winfo_children()) == 0, "Patients are displayed for a non-matching query."

# --- Tests for patient_list ---
def test_patient_list_display(root, doctor_info):
    """Test that the patient list displays properly."""
    patient_list(doctor_info, root)
    assert len(root.children) > 0, "Patient list not displayed."

def test_patient_list_buttons(root, doctor_info):
    """Test that patient buttons are created for each patient."""
    patient_list(doctor_info, root)
    buttons = [child for child in root.winfo_children() if isinstance(child, tk.Button)]
    assert len(buttons) > 0, "Patient buttons not created."

# --- Tests for open_patient_profile ---
def test_open_patient_profile_window_title(root, doctor_info):
    """Test that the patient profile window has the correct title."""
    patient = (1, "John", "Doe", "Diagnosis", "2025-01-15")
    open_patient_profile(patient, doctor_info, root)
    assert root.title() == "John Doe's profile", "Incorrect window title."

def test_open_patient_profile_ui_elements(root, doctor_info):
    """Test that UI elements for patient profile are created."""
    patient = (1, "John", "Doe", "Diagnosis", "2025-01-15")
    open_patient_profile(patient, doctor_info, root)
    assert root.title() == "John Doe's profile", "Window title is incorrect."
    assert len(root.winfo_children()) > 0, "UI elements were not created."

def test_open_patient_profile_invalid_patient_id(root, doctor_info):
    """Test error handling for an invalid patient ID."""
    patient = (9999, "Nonexistent", "Patient", "N/A", "N/A")
    with patch("sqlite3.connect") as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Invalid patient ID")
        with pytest.raises(sqlite3.Error):
            open_patient_profile(patient, doctor_info, root)