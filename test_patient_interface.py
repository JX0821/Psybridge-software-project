import datetime
import tkinter as tk

from patient_interface import get_user_info as getui
from patient_interface import create_main_window as main
from patient_interface import show_treatment_notes as tnotes
from patient_interface import questionaires as q
from patient_interface import change_information as cinfo
from patient_interface import change_password as cpass
import pytest

USER_ID = 1

def test_get_user_info_wrong_input_type():
    """
    Test to see if inputting a string instead of a integer as user_id in get_user_info raises an error.
    """
    with pytest.raises(TypeError):
        getui('string')

def test_get_user_info_user_id_same_in_dict():
    """
    Test to see if the inputted user_id remains the same in the outputted dictionary.
    """
    assert getui(USER_ID)["user_id"] == USER_ID

def test_get_user_info_unknow_user_id():
    """
    Test to confirm that an unknown user_id raises an error
    """
    invalid_user_id = 99999
    with pytest.raises(TypeError):
        getui(invalid_user_id)

def test_get_user_info_output_type():
    """
    Check to see if get_user_info returns a dictionary
    """
    assert type(getui(USER_ID)) == dict

def test_get_user_info_password_type():
    """
    Test to confirm that password is stored as md5 hash.
    """
    assert len(getui(USER_ID)["password"]) == 32, "The password needs to be stored as an md5 hash."

def test_get_user_info_output_typs_in_dict():
    """
    Test the types outputted in the dictionary
    """
    data = getui(USER_ID)

    # Check if all required variables exist in the dictionary
    required_variables = [
        "first_name", "last_name", "date_of_birth", "phone_number", "address",
        "doctor_name", "patient_id", "upcoming_meeting", "appointments",
        "questionaires", "user_id", "password",
        "upcoming_appointments_patient", "upcoming_appointments_doctor"
    ]
    for variable in required_variables:
        assert variable in data, f"The key '{variable}' is missing from the dictionary."


    # Check fields from the user table
    assert type(data["first_name"]) in (str, None), "The 'first_name' must be a string or None."
    assert type(data["last_name"]) in (str, None), "The 'last_name' must be a string or None."
    assert type(data["date_of_birth"]) in (str, None), "The 'date_of_birth' must be a string or None."
    assert type(data["phone_number"]) in (str, None), "The 'phone_number' must be a string or None."
    assert type(data["address"]) in (str, None), "The 'address' must be a string or None."

    # Check the doctor name tuple
    assert type(data["doctor_name"]) == tuple and len(data["doctor_name"]) == 2, "The 'doctor_name' must be a tuple with two elements."
    assert type(data["doctor_name"][0]) in (str, None), "The 'first_name' of the doctor must be a string or None."
    assert type(data["doctor_name"][1]) in (str, None), "The 'last_name' of the doctor must be a string or None."

    # Check patient ID
    assert type(data["patient_id"]) == int, "The 'patient_id' must be an integer."

    # Check upcoming meeting
    assert type(data["upcoming_meeting"]) == list and len(data["upcoming_meeting"]) <= 4, "The 'upcoming_meeting' must be a list with at most four elements."
    assert all(type(item) == str for item in data["upcoming_meeting"]), "Each element in 'upcoming_meeting' must be a string."

    # Check appointments
    assert type(data["appointments"]) == list, "The 'appointments' must be a list."
    for appointment in data["appointments"]:
        assert type(appointment) == tuple, "Each appointment must be a tuple."
        assert len(appointment) >= 7, "Each appointment tuple must have at least 7 elements."

    # Check questionnaires
    assert type(data["questionaires"]) == list, "The 'questionaires' must be a list."
    for questionaire in data["questionaires"]:
        assert type(questionaire) == tuple and len(questionaire) == 2, "Each questionnaire must be a tuple with two elements."
        assert type(questionaire[0]) == str, "The questionnaire name must be a string."
        assert type(questionaire[1]) == list, "The questions in a questionnaire must be a list."
        for question, answers in questionaire[1]:
            assert type(question) == str, "Each question must be a string."
            assert type(answers) == list, "The answers for a question must be a list."
            assert all(type(answer) == str for answer in answers), "Each answer in a list of answers must be a string."

    # Check user ID
    assert type(data["user_id"]) == int, "The 'user_id' must be an integer."

    # Check password
    assert type(data["password"]) == str, "The 'password' must be a string."

    # Check upcoming appointments for patients
    assert type(data["upcoming_appointments_patient"]) == list, "The 'upcoming_appointments_patient' must be a list."
    for appointment in data["upcoming_appointments_patient"]:
        assert type(appointment) == tuple, "Each appointment must be a tuple."
        assert len(appointment) == 7, "Each appointment tuple must have 7 elements."
        assert type(appointment[0]) == datetime.datetime, "The first element of an appointment must be a datetime."
        assert all(type(field) in (str, int) for field in appointment[1:]), "The remaining elements of an appointment must be strings or integers."

    # Check upcoming appointments for doctors
    assert type(data["upcoming_appointments_doctor"]) == list,"The 'upcoming_appointments_doctor' must be a list."
    for appointment in data["upcoming_appointments_doctor"]:
        assert type(appointment) == tuple, "Each appointment must be a tuple."
        assert len(appointment) == 7, "Each appointment tuple must have 7 elements."
        assert type(appointment[0]) == datetime.datetime, "The first element of an appointment must be a datetime."
        assert all(type(field) in (str, int) for field in appointment[1:]), "The remaining elements of an appointment must be strings or integers."

@pytest.fixture
def user_info():
    return {'first_name': 'Emily',
            'last_name': 'Johnson',
            'date_of_birth': '22-8-1985',
            'phone_number': '85678901234',
            'address': '78 Rosewood Lane, London, E1 5AB, UK',
            'doctor_name': ('Zoe', 'Harper'),
            'patient_id': 4002,
            'upcoming_meeting': ['2024-12-12', 'Zoe', 'Harper', '09:15'],
            'appointments': [('2024-01-03', '2024-01-03', 'Psychotherapy', 'Zoe', 'Harper', '09:15', 2, 'Einsteinweg 55 - Leiden', 1, 'Anxiety Disorder'), ('2024-03-06', '2024-03-06', 'Psychotherapy', 'Zoe', 'Harper', '14:30', 100, 'Einsteinweg 55 - Leiden', 1, 'Anxiety Disorder'), ('2024-10-15', '2024-12-12', None, 'Zoe', 'Harper', '09:15', 144, 'Einsteinweg 55 - Leiden', 1, '')],
            'questionaires': [('Daily SDS', [('Do you have little interest or pleasure in doing things today?', ['Yes', 'No']), ('Are you feeling down, depressed, or hopeless today?', ['Yes', 'No']), ('Have you had trouble falling asleep, staying asleep, or slept too much today?', ['Yes', 'No']), ('Do you feel tired or have little energy today?', ['Yes', 'No']), ('Do you have a poor appetite or are you overeating today?', ['Yes', 'No']), ('Do you feel bad about yourself today, like you are a failure or have let yourself or your family down?', ['Yes', 'No']), ('Are you having trouble concentrating on things today, such as reading or watching television?', ['Yes', 'No']), ('Have you been moving or speaking more slowly today than usual, or feeling so fidgety or restless that others could notice?', ['Yes', 'No']), ('Have you had thoughts today that you would be better off dead or thoughts of hurting yourself?', ['Yes', 'No'])]), ('HCL-32', [('I need less sleep than usual', ['Yes', 'No']), ('I feel more energetic and more active', ['Yes', 'No']), ('I am more self-confident', ['Yes', 'No']), ('I enjoy my work more', ['Yes', 'No']), ('I am more sociable (make more phone calls, go out more)', ['Yes', 'No']), ('I want to travel and/or do travel more', ['Yes', 'No']), ('I tend to drive faster or take more risks when driving', ['Yes', 'No']), ('I spend more money/too much money', ['Yes', 'No']), ('I take more risks in my daily life (in my work and/or other activities)', ['Yes', 'No']), ('I am physically more active (sport etc.)', ['Yes', 'No']), ('I plan more activities or projects', ['Yes', 'No']), ('I have more ideas, I am more creative', ['Yes', 'No']), ('I am less shy or inhibited', ['Yes', 'No']), ('I wear more colorful and more extravagant clothes/make-up', ['Yes', 'No']), ('I want to meet or actually do meet more people', ['Yes', 'No']), ('I am more interested in sex, and/or have increased sexual desire', ['Yes', 'No']), ('I am more flirtatious and/or am more sexually active', ['Yes', 'No']), ('I talk more', ['Yes', 'No']), ('I think faster', ['Yes', 'No']), ('I make more jokes or puns when I am talking', ['Yes', 'No']), ('I am more easily distracted', ['Yes', 'No']), ('I engage in lots of new things', ['Yes', 'No']), ('My thoughts jump from topic to topic', ['Yes', 'No']), ('I do things more quickly and/or more easily', ['Yes', 'No']), ('I am more impatient and/or get irritable more easily', ['Yes', 'No']), ('I can be exhausting or irritating for others', ['Yes', 'No']), ('I get into more quarrels', ['Yes', 'No']), ('My mood is higher, more optimistic', ['Yes', 'No']), ('I drink more coffee', ['Yes', 'No']), ('I smoke more cigarettes', ['Yes', 'No']), ('I drink more alcohol', ['Yes', 'No'])])],
            'user_id': 2,
            'password': '4a7d1ed414474e4033ac29ccb8653d9b',
            'upcoming_appointments_patient': [(datetime.datetime(2024, 12, 12, 0, 0), 'Zoe', 'Harper', '09:15', 144, 'Einsteinweg 55 - Leiden', 1)],
            'upcoming_appointments_doctor': [(datetime.datetime(2024, 12, 12, 0, 0), 'Zoe', 'Harper', '09:15', 144, 'Einsteinweg 55 - Leiden', 1), (datetime.datetime(2024, 12, 22, 0, 0), 'Zoe', 'Harper', '15:00', 150, 'Einsteinweg 55 - Leiden', 1), (datetime.datetime(2025, 1, 3, 0, 0), 'Zoe', 'Harper', '11:30', 156, 'Einsteinweg 55 - Leiden', 1), (datetime.datetime(2025, 1, 15, 0, 0), 'Zoe', 'Harper', '10:30', 162, 'Einsteinweg 55 - Leiden', 1), (datetime.datetime(2025, 1, 27, 0, 0), 'Zoe', 'Harper', '14:45', 168, 'Einsteinweg 55 - Leiden', 1), (datetime.datetime(2025, 2, 10, 0, 0), 'Zoe', 'Harper', '11:45', 174, 'Einsteinweg 55 - Leiden', 1), (datetime.datetime(2025, 2, 22, 0, 0), 'Zoe', 'Harper', '10:45', 180, 'Einsteinweg 55 - Leiden', 1), (datetime.datetime(2025, 3, 6, 0, 0), 'Zoe', 'Harper', '12:00', 186, 'Einsteinweg 55 - Leiden', 1)]
            }

@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()
@pytest.fixture
def root_from_main(user_info, root):
    main(user_info, root=root, run_mainloop=False)
    yield root

def test_main_welcome_text(root_from_main):
    """
    Test to confirm that the right welcome text is displayed
    """
    welcome_label = root_from_main.children['!label']  # Haal het eerste label op
    welcome_text = \
        """Hello Emily Johnson,
Welcome to your personal Psybridge page.

Your next appointment is 12 December 2024 at 09:15, 
with doctor Zoe Harper."""
    assert welcome_label.cget("text") == welcome_text, "Welcome text doesn't match or isn't found."

def test_main_personal_info_text(root_from_main):
    """
    Test to confirm that the personal information is displayed correctly.
    """
    personal_info_expected = ["Personal information:", "Date of birth: 22-8-1985", "Address: 78 Rosewood Lane, London, E1 5AB, UK", "Phone number: 85678901234"]

    labels = []

    # Zoek het rechterframe waar persoonlijke informatie wordt weergegeven
    for frame in root_from_main.winfo_children():
        if frame.winfo_class() == "Frame":
            for label in frame.winfo_children():
                if label.winfo_class() == "Label":
                    labels.append(str(label.cget('text')))

    for expected_text in personal_info_expected:
        assert expected_text in labels, f"'{expected_text}' not found in labels"

def test_main_buttons_exist(root_from_main):
    """
    Test to see if all buttons exist
    """
    button_texts = ["Treatment notes","Questionnaires","Schedule appointment","Change password","Change personal information"]
    buttons_found = []
    for frame in root_from_main.winfo_children():
        if frame.winfo_class() == "Frame":
            for button in frame.winfo_children():
                if button.winfo_class() == "Button":
                    buttons_found.append(str(button.cget('text')))

    for button_text in button_texts:
        assert button_text in buttons_found, f"Button '{button_text}' not found."

@pytest.fixture
def root_from_tnotes(user_info, root_from_main):
    tnotes(user_info, root=root_from_main)
    yield root

def test_tnotes(root_from_tnotes):
    """
    To check to confirm the treatment notes window exists.
    """
    assert root, "The treatment notes window does no longer work!"

@pytest.fixture
def root_from_q(user_info, root_from_main):
    q(user_info, root=root_from_main)
    yield root

def test_q(root_from_q):
    """
    To check to confirm the questionaire window exists.
    """
    assert root, "The questionaire window does no longer work!"

@pytest.fixture
def root_from_cinfo(user_info, root_from_main):
    cinfo(user_info, root=root_from_main)
    yield root

def test_cinfo(root_from_cinfo):
    """
    To check to confirm the change personal information window exists.
    """
    assert root, "The change personal information window does no longer work!"

@pytest.fixture
def root_from_cpass(user_info, root_from_main):
    cpass(user_info, root=root_from_main)
    yield root

def test_cpass(root_from_cpass):
    """
    To check to confirm the change password window exists.
    """
    assert root, "The change password window does no longer work!"