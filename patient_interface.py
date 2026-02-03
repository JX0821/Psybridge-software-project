"""
Authors:
Joris Nouwens (database connection, change personal information interface, questionaire interface, change password interface, docstrings),
Jingbo Li (general patient interface),
Piotr Lichota (treatment notes interface)
Jixuan Yao (open AI assistant chat)

About this python file:
This document contains the patient interface. The document starts by collection information about the patient from the database.
Then the patient interface is initialized and from there you can click to "change personal information", "Treatment notes", "change password", and "questionaires".
All of these interfaces are also in this document.

Parameters:
    User_id (int) To load the correct patient information.
"""

import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
import hashlib
import scheduling_system as ss
import openai
from tkinter import simpledialog
import os


# This user_id will be used when this page is tested without the log_in page to initialise this page.
user_id = 2

def get_user_info(user_id):
    """
    This function takes the user_id and returns a dictionary with information about the patient.

    Parameters:
        User_id (int) The ID which corresponds to a user_id in the database.

    Returns:
        dict: {
                "first_name": str(first name of the patient),
                "last_name": str(last name of the patient),
                "date_of_birth": str(birthday of the patient),
                "phone_number": str(phone number of the patient),
                "address": str(address of the patient),
                "doctor_name": (str(first name of doctor), str(last name of doctor)),
                "patient_id": int(patient_id of the patient,
                "upcoming_meeting": [tuple(date of next meeting stored as (datetime.datetime(YYYY, MM, DD, 0, 0)), str(first name of doctor), str(last name of doctor), str(time of meeting stored as HH:MM)],
                "appointments": [[tuple(date of last modification stored as (datetime.datetime(YYYY, MM, DD, 0, 0)), tuple(date of meeting stored as (datetime.datetime(YYYY, MM, DD, 0, 0)), str(treatment notes), str(first name of doctor), str(last name of doctor), str(time of meeting stored as HH:MM)],
                                    ... and so on for all past, present and future appointments, each appointment stored in a list ...],
                "questionaires": [
                                    (
                                        str(name of the questionaire),
                                        [
                                            (str(question text), [str(answer1), str(answer2), ...]),
                                            ... a tuple for each question and a list of answers ...
                                        ]
                                    ),
                                    ... a tuple for each questionaire, containing the questionaire name and a list with questions and answers ...
                                ],
                "user_id": user_id of the patient,
                "password": A md5 hash of the password the patient uses for PsyBridge,
                "upcoming_appointments_patient": [(tuple(date of next meeting stored as (datetime.datetime(YYYY, MM, DD, 0, 0)), str(first name of doctor), str(last name of doctor), str(time of meeting) stored as HH:MM, int(Appointment_id) in the database saved as Examination_id, str(Location) contains the street + number - city, int(confirmed) this is a boolean value saved as an integer, because SQL lite doesn't support boolean values),...
                                        ... and so on for all upcoming appointments, with all information inside a tuple in this list ...]
                "upcoming_appointments_doctor": [(tuple(date of next meeting stored as (datetime.datetime(YYYY, MM, DD, 0, 0)), str(first name of doctor), str(last name of doctor), str(time of meeting) stored as HH:MM, int(Appointment_id) in the database saved as Examination_id, str(Location) contains the street + number - city, int(confirmed) this is a boolean value saved as an integer, because SQL lite doesn't support boolean values),...
                                        ... and so on for all upcoming appointments, with all information inside a tuple in this list ...]
            }
    """
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()
    #Get information about the user in the user table
    cursor.execute("SELECT First_name, Last_name, Date_of_birth, Phone_number, Address FROM Users WHERE User_id = ?", (user_id,))
    first_name, last_name, date_of_birth, phone_number, address = cursor.fetchone()
    cursor.execute("SELECT Patient_id FROM Patients p WHERE p.User_id = ?",(user_id,))
    patient_id = cursor.fetchone()[0]
    #Find out which doctor is currently treating the patient (if no doctor is assigned, this returns NONE)
    cursor.execute("""
        SELECT u.First_name, u.Last_name, d.Doctor_id, u.Password
        FROM Users u
        JOIN Doctors d ON u.User_id = d.User_id
        JOIN Treats t ON d.Doctor_id = t.Doctor_id
        JOIN Patients p ON t.Patient_id = p.Patient_id
        WHERE p.User_id = ?
    """, (user_id,))
    try:
        doctor_first_name, doctor_last_name, doctor_id, password = cursor.fetchone()
    except:
        doctor_first_name, doctor_last_name, doctor_id, password = None, None, None, None
    doctor_name = (doctor_first_name, doctor_last_name)
    #Find all appointments, both previous appointments and appointments in future + With which doctor the appointment was
    cursor.execute("""
        SELECT a.Date_last_modified, a.Date_of_meeting, a.Treatment_notes, u.First_name AS Doctor_first_name, u.Last_name AS Doctor_last_name, a.Time_of_meeting, a.Examination_id, a.Location, a.Confirmed
        FROM Meets m
        JOIN Appointment_details a ON m.Examination_id = a.Examination_id
        JOIN Doctors d ON m.Doctor_id = d.Doctor_id
        JOIN Users u ON d.User_id = u.User_id
        WHERE m.Patient_id = ?;
    """, (patient_id,))
    appointments = cursor.fetchall()
    # List to store the next upcoming meeting details: [date, doctor's first name, doctor's last name]
    upcoming_meeting = []
    # Filter appointments to include only future dates
    upcoming_dates = [
        (datetime.strptime(appointment[1], '%Y-%m-%d'), appointment[3], appointment[4], appointment[5], appointment[6], appointment[7], appointment[8])
        for appointment in appointments if appointment[1] >= datetime.now().strftime('%Y-%m-%d')
    ]
    # Find the closest appointment date manually
    if upcoming_dates:
        # Set the first appointment as the closest one initially
        closest_appointment = upcoming_dates[0]
        # Iterate through the upcoming_dates to find the earliest date
        for appointment in upcoming_dates[1:]:
            if appointment[0] < closest_appointment[0]:
                closest_appointment = appointment
        # Store the closest appointment details in upcoming_meeting
        upcoming_meeting = [
            closest_appointment[0].strftime('%Y-%m-%d'),
            closest_appointment[1],
            closest_appointment[2],
            closest_appointment[3]
        ]
    # find all diagnoses
    cursor.execute("""
        SELECT d.Diagnose_date, d.Diagnose
        FROM Diagnoses diag
        JOIN Diagnosis d ON diag.Diagnose_id = d.Diagnose_id
        WHERE diag.Patient_id = ?;
    """, (patient_id,))
    diagnoses = cursor.fetchall()
    # Convert diagnoses to a dictionary for quick lookup by date
    diagnoses_dict = {diagnose[0]: diagnose[1] for diagnose in diagnoses}
    # Add diagnoses to appointments
    appointments_with_diagnoses = []
    for appointment in appointments:
        date_of_meeting = appointment[1]  # This is the appointment date
        # Look up the diagnosis by date or use an empty string if no diagnosis is found
        matching_diagnose = diagnoses_dict.get(date_of_meeting, "")
        # Append the appointment along with the diagnosis to the list
        appointments_with_diagnoses.append(appointment + (matching_diagnose,))
    # Find all appointments the doctor has
    cursor.execute("""
        SELECT a.Date_of_meeting, u.First_name AS Doctor_first_name, u.Last_name AS Doctor_last_name, a.Time_of_meeting, a.Examination_id, a.Location, a.Confirmed
        FROM Meets m
        JOIN Appointment_details a ON m.Examination_id = a.Examination_id
        JOIN Doctors d ON m.Doctor_id = d.Doctor_id
        JOIN Users u ON d.User_id = u.User_id
        WHERE m.doctor_id = ?;
    """, (doctor_id,))
    appointments_from_treating_doctor = cursor.fetchall()
    upcoming_dates_from_treating_doctor = [
        (datetime.strptime(appointment[0], '%Y-%m-%d'), appointment[1], appointment[2], appointment[3], appointment[4], appointment[5], appointment[6])
        for appointment in appointments_from_treating_doctor if appointment[0] >= datetime.now().strftime('%Y-%m-%d')
    ]
    # Get available questionaires
    cursor.execute("""
            SELECT q.Questionaire_name, qs.Question, qo.Answer
            FROM has_access_to AS ha
            JOIN Questionaire AS q ON ha.Questionaire_id = q.Questionaire_id
            JOIN Questions AS qs ON q.Questionaire_id = qs.Questionaire_id
            JOIN Question_options AS qo ON qs.Question_number = qo.Question_number
            WHERE ha.Patient_id = ?
            ORDER BY q.Questionaire_name, qs.Question_number;
    """, (patient_id,))
    results = cursor.fetchall()
    # Organize the results into a list
    questionaires = []
    current_questionaire = None
    current_questions = {}
    # Organize the questionaire data to be saved in one variable, in a way that makes sense to me:
    for questionaire_name, question, answer in results:
        # Check if we have a new questionaire
        if current_questionaire != questionaire_name:
            # If we had a previous questionaire, append it to the list
            if current_questionaire is not None:
                # Append the current questionaire with its questions and answers
                questionaires.append((current_questionaire, [(q, a) for q, a in current_questions.items()]))
            # Reset for the new questionaire
            current_questionaire = questionaire_name
            current_questions = {}
        # Add the question and answer
        if question not in current_questions:
            current_questions[question] = []
        current_questions[question].append(answer)
    # Append the last questionaire if needed
    if current_questionaire is not None:
        questionaires.append((current_questionaire, [(q, a) for q, a in current_questions.items()]))
    cursor.close()
    conn.close()
    # Now, `upcoming_meeting` contains [date of meeting, doctor's first name, doctor's last name]
    return {
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": date_of_birth,
        "phone_number": phone_number,
        "address": address,
        "doctor_name": doctor_name,
        "patient_id": patient_id,
        "upcoming_meeting": upcoming_meeting,
        "appointments": appointments_with_diagnoses,
        "questionaires": questionaires,
        "user_id": user_id,
        "password": password,
        "upcoming_appointments_patient": upcoming_dates,
        "upcoming_appointments_doctor": upcoming_dates_from_treating_doctor
    }


# The treatment notes interface
def show_treatment_notes(user_info, root):
    """
    Changes the window to display the diagnosis, the date of the meeting in which the diagnosis was established and the treatment plan as submitted by the doctor.

    Parameters:
        user_info (dict):  A dictionary with all the information about the user, created by the function get_user_info
        root (tkinter.Tk): Contains the information about the window as it is currently displayed, this variable is used to change the current window to display something new.
    """
    # Clear all widgets in the root window
    for widget in root.winfo_children():
        widget.destroy()
    root.geometry("600x400")
    root.title("PsyBridge - Treatment notes")

    # Title of page
    label = tk.Label(root, text="Treatment notes", font=("Arial", 18))
    label.pack(padx=20, pady=10, anchor="n")

    # Frame to contain the Treeview and back button
    frame_main = tk.Frame(root)
    frame_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Setup Treeview for dynamic table display
    columns = ("Diagnosis", "Date", "Treatment Plan")
    tree = ttk.Treeview(frame_main, columns=columns, show="headings")
    tree.heading("Diagnosis", text="Diagnosis")
    tree.heading("Date", text="Date")
    tree.heading("Treatment Plan", text="Treatment Plan")

    # Configure column widths to adjust dynamically
    tree.column("Diagnosis", anchor="w", width=200)
    tree.column("Date", anchor="center", width=100)
    tree.column("Treatment Plan", anchor="w", width=300)

    # Insert data into the Treeview
    for item in user_info['appointments']:
        diagnosis = str(item[9]) if item[9] is not None else ''
        date_of_meeting = str(item[1]) if item[1] is not None else ''
        treatment_plan = str(item[2]) if item[2] is not None else ''
        tree.insert("", "end", values=(diagnosis, date_of_meeting, treatment_plan))

    # Pack the Treeview to expand dynamically
    tree.pack(fill=tk.BOTH, expand=True)

    # Back button in the bottom right
    back_button = tk.Button(root, text="Back", font=('Arial', 12), command=lambda: create_main_window(user_info, root))
    back_button.pack(anchor="se", side="bottom", padx=10, pady=10)

# This function shows the selected questionaire (selected in questionaire interface)
def open_questionaire(questionaire_id, questionaire_name, questionaire_data, user_info, root):
    """
    Changes the window to show the selected questionaire, question by question.

    Parameters:
        questionaire_id (int): The ID which corresponds with the questionaire_id in the database, this is necessery to store the answers in the database
        questionaire_name (str): The name of the questionaire, which is displayed in the window title
        questionaire_data (lst): A list in which each entry contains all information about a question. This information is stored as a tuple, containing the question on position 0 and the answers in a list on postion 1. Like this:
                                    [
                                            (str(question text), [str(answer1), str(answer2), ...]),
                                            ... a tuple for each question and a list of answers ...
                                    ]
        user_info (dict):  A dictionary with all the information about the user, created by the function get_user_info
        root (tkinter.Tk): Contains the information about the window as it is currently displayed, this variable is used to change the current window to display something new.
    """
    # Clear all widgets in the root window
    for widget in root.winfo_children():
        widget.destroy()
    root.title(f"PsyBridge - {questionaire_name}")
    # Initialize list to store answers
    user_answers = []
    question_index = 0  # To track which question we're on

    def display_question(index):
        """
        Changes the window the display the current question.

        parameters:
            index(int): Starts with 0 for the first question and for each question index+=1, changing question is done in submit_question.
        """
        # Clear previous widgets (if any)
        for widget in root.winfo_children():
            widget.destroy()

        # Back button
        back_button = tk.Button(root, text="Back", font=('Arial', 12),
                                command=lambda: create_main_window(user_info, root))
        back_button.pack(anchor="se", side="bottom", padx=10, pady=10)

        if index < len(questionaire_data):
            question, options = questionaire_data[index]
            question_label = tk.Label(root, text=question, font=("Arial", 14),
                                      wraplength=580)  # Set wraplength to fit within the window
            question_label.pack(pady=20)

            for option in options:
                # Create a button for each answer option
                answer_button = tk.Button(root, text=option, font=('Arial', 12),
                                          command=lambda ans=option: submit_answer(question, ans, index))
                answer_button.pack(pady=5)
        else:
            # All questions answered, show score or next steps here
            show_score(user_answers)

    def submit_answer(question, answer, index):
        """
        Stores the current question and the given answer as a tuple and appends them to a list with given answers and adds one to the index to move to the next question.

        parameters:
            question (str): The current question as a string
            answer (str): The answer given by the patient as a string
            index (int): An index to keep track of which is the current question. index = 0 for the first question.
        """
        # Store the question and the user's answer as a tuple
        user_answers.append((question, answer))
        index += 1
        display_question(index)  # Move to the next question

    def show_score(answers):
        """
        Displays all questions and for each question the given answer and a submit button to submit the given answers.

        parameters:
            answers (lst): A list of tuples, each tuple contains a question (str) and an answer to that question (str).
        """
        # Clear all widgets in the root window
        for widget in root.winfo_children():
            widget.destroy()

        # Display the thank-you message above the canvas
        result_label = tk.Label(root, text="Thank you for completing the questionnaire!", font=("Arial", 14))
        result_label.pack(pady=20, anchor="n")
        # Create a frame for the canvas and scrollbar
        frame = tk.Frame(root)
        frame.pack(padx=20, pady=10, anchor="n")
        # Create a canvas with limited height to leave space for buttons
        canvas = tk.Canvas(frame, height=210, width=500)  # Set canvas width to 500
        canvas.pack(side="left", fill="both", expand=True)
        # Add a scrollbar to the canvas and make it stay on the right side of the canvas
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        # Configure the canvas to work with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        # Create a frame inside the canvas to hold the content
        content_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        # Display the questions and answers in the content frame
        for idx, (question, ans) in enumerate(answers):
            # Display the question followed by the answer, centering both
            question_label = tk.Label(content_frame, text=f"{question}", font=("Arial", 12), wraplength=480,
                                      justify="left")
            question_label.pack(anchor="w")
            answer_label = tk.Label(content_frame, text=f"{ans} \n", font=("Arial", 12), wraplength=480, justify="center")
            answer_label.pack(anchor="center")  # Center the answer text
        # Add the submit button below the canvas
        submit_button = tk.Button(root, text='Submit', font=('Arial', 12),
                                  command=lambda: to_database(answers, user_info, root))
        submit_button.pack(pady=10)
        # Add the back button at the bottom
        back_button = tk.Button(root, text="Back", font=('Arial', 12),
                                command=lambda: create_main_window(user_info, root))
        back_button.pack(anchor="se", side="bottom", padx=10, pady=10)
    # Start displaying questions
    display_question(question_index)
    def to_database(answers, user_info, root):
        """
        Stores the answers given in a questionaire to the database, when the submit button is clicked.

        parameters:
            answers (lst): A list of tuples, each tuple contains a question (str) and an answer to that question (str).
            user_info (dict):  A dictionary with all the information about the user, created by the function get_user_info
            root (tkinter.Tk): Contains the information about the window as it is currently displayed, this variable is used to change the current window to display something new.
        """

        patient_id = user_info['patient_id']
        today = str(datetime.now().date())
        conn = sqlite3.connect('Database.db')
        cursor = conn.cursor()
        cursor.execute("""
           INSERT INTO Questionaire_responses (Questionaire_id, Questionaire_date) VALUES
           (?,?)
           """, (questionaire_id, today))
        attempt_id = cursor.lastrowid
        cursor.execute("""
           INSERT INTO Fills_in (Patient_id, Questionaire_id, Attempt_id) VALUES
           (?,?,?)
           """, (patient_id,questionaire_id,attempt_id))
        q_nr = 1
        for answer in answers:
            cursor.execute("""
               INSERT INTO Question_answers (Attempt_id, Answer, Question_id) VALUES
               (?,?,?)
               """, (attempt_id, answer[1], q_nr))
            q_nr+=1
        # Commit the changes
        conn.commit()
        cursor.close()
        conn.close()
        create_main_window(user_info, root)

# The questionaire interface with an overview of all available questionaires
def questionaires(user_info, root):
    """
    Changes the window to display a button for each available questionaire, to enable the patient to select a questionare.

    parameters:
        user_info (dict):  A dictionary with all the information about the user, created by the function get_user_info
        root (tkinter.Tk): Contains the information about the window as it is currently displayed, this variable is used to change the current window to display something new.
    """
    # Clear all widgets in the root window
    for widget in root.winfo_children():
        widget.destroy()
    root.title("PsyBridge - Questionaires")
    root.geometry("600x400")
    # Button to go back to patient interface
    back_button = tk.Button(root, text="Back", font=('Arial', 12), command=lambda: create_main_window(user_info, root))
    back_button.pack(anchor="se", side="bottom", padx=10, pady=10)
    label = tk.Label(root, text="Available questionaires", font=("Arial", 18))
    label.pack(padx=20, pady=10, anchor="n")
    # Frame to hold the questionnaire buttons
    button_frame = tk.Frame(root)
    button_frame.pack(expand=True)
    # Loop through the available questionaires and create a button for each
    q_id = 1
    for questionaire in user_info['questionaires']:
        button = tk.Button(button_frame, text=questionaire[0], font=('Arial', 12), command=lambda id=q_id, questionaire_name=questionaire[0], questions = questionaire[1]: open_questionaire(id, questionaire_name, questions, user_info, root))
        button.pack(pady=5)
        q_id+=1



def change_information(user_info, root):
    """
    Changes the window to display information about the patient in field to allow patients to change their information.

    parameters:
        user_info (dict):  A dictionary with all the information about the user, created by the function get_user_info
        root (tkinter.Tk): Contains the information about the window as it is currently displayed, this variable is used to change the current window to display something new.
    """
    # Clear all widgets in the root window
    for widget in root.winfo_children():
        widget.destroy()
    root.title("PsyBridge - Change Personal Information")
    root.geometry("600x400")
    # Back button
    back_button = tk.Button(root, text="Back", font=('Arial', 12),
                            command=lambda: create_main_window(user_info, root))
    back_button.pack(anchor="se", side="bottom", padx=10, pady=10)
    # Title label
    title_label = tk.Label(root, text="Update Your Information", font=("Arial", 18))
    title_label.pack(pady=10)
    # Create a frame for the personal information
    info_frame = tk.Frame(root)
    info_frame.pack(pady=10, fill="both", expand=True)
    # Configure the grid columns to expand
    info_frame.columnconfigure(0, weight=1)  # Column for labels
    info_frame.columnconfigure(1, weight=2)  # Column for entry fields
    # Column 1: Labels
    tk.Label(info_frame, text="Phone Number:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5, padx=10)
    tk.Label(info_frame, text="Date of Birth (DD-MM-YYYY):", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5, padx=10)
    tk.Label(info_frame, text="Street Address:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", pady=5, padx=10)
    tk.Label(info_frame, text="City:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", pady=5, padx=10)
    tk.Label(info_frame, text="Postal Code:", font=("Arial", 12)).grid(row=5, column=0, sticky="w", pady=5, padx=10)
    tk.Label(info_frame, text="Country:", font=("Arial", 12)).grid(row=6, column=0, sticky="w", pady=5, padx=10)
    # Column 2: Entry fields
    phone_entry = tk.Entry(info_frame, font=('Arial', 12))
    try:
        phone_entry.insert(0, user_info['phone_number'])  # Pre-fill with current number
    except:
        phone_entry.insert(0, '')
    phone_entry.grid(row=0, column=1, pady=5, sticky="ew")
    # Split date of birth into three fields
    dob_frame = tk.Frame(info_frame)  # Frame for DOB inputs
    dob_frame.grid(row=1, column=1, pady=5, sticky="ew")
    day_entry = tk.Entry(dob_frame, width=3, font=('Arial', 12))
    day_entry.grid(row=0, column=0, padx=(0, 5))
    try:
        day_entry.insert(0, user_info['date_of_birth'].split('-')[0])  # Fill with day
    except:
        pass
    day_separator = tk.Label(dob_frame, text="-", font=('Arial', 12))
    day_separator.grid(row=0, column=1)
    month_entry = tk.Entry(dob_frame, width=3, font=('Arial', 12))
    month_entry.grid(row=0, column=2, padx=(0, 5))
    try:
        month_entry.insert(0, user_info['date_of_birth'].split('-')[1])  # Fill with month
    except:
        pass
    month_separator = tk.Label(dob_frame, text="-", font=('Arial', 12))
    month_separator.grid(row=0, column=3)
    year_entry = tk.Entry(dob_frame, width=5, font=('Arial', 12))
    year_entry.grid(row=0, column=4)
    try:
        year_entry.insert(0, user_info['date_of_birth'].split('-')[2])  # Fill with year
    except:
        pass
    # Street address
    street_entry = tk.Entry(info_frame, font=('Arial', 12))
    try:
        street_entry.insert(0, user_info['address'].split(", ")[0])  # Street address
    except:
        pass
    street_entry.grid(row=3, column=1, pady=5, sticky="ew")
    # City
    city_entry = tk.Entry(info_frame, font=('Arial', 12))
    try:
        city_entry.insert(0, user_info['address'].split(", ")[1])  # City
    except:
        pass
    city_entry.grid(row=4, column=1, pady=5, sticky="ew")
    # Postal code
    postal_code_entry = tk.Entry(info_frame, font=('Arial', 12))
    try:
        postal_code_entry.insert(0, user_info['address'].split(", ")[2])  # Postal code
    except:
        pass
    postal_code_entry.grid(row=5, column=1, pady=5, sticky="ew")
    # Country
    country_entry = tk.Entry(info_frame, font=('Arial', 12))
    try:
        country_entry.insert(0, user_info['address'].split(", ")[3])  # Country
    except:
        pass
    country_entry.grid(row=6, column=1, pady=5, sticky="ew")
    # Save button
    save_button = tk.Button(root, text="Save Changes", font=('Arial', 12),
                            command=lambda: save_changes(phone_entry.get(),
                                                          f"{int(day_entry.get())}-{int(month_entry.get())}-{int(year_entry.get())}",
                                                          street_entry.get(), city_entry.get(),
                                                          postal_code_entry.get(), country_entry.get(),
                                                          user_info, confirmation_label))
    save_button.pack(pady=5)
    # Confirmation label, initially empty
    confirmation_label = tk.Label(root, text="", font=("Arial", 12))
    confirmation_label.pack(pady=0)

def save_changes(phone, dob, street, city, postal_code, country, user_info, confirmation_label):
    """
    This function is activated when the patient selects 'save changes', it takes all values form the fields in the 'change personal information' interface, and stores it in the database.

    Parameters:
        Phone (str): The phone number of the patient.
        dob (str): The date of birth of the patient.
        Street (str): The street in which the patient lives (this is combined with city, postal code and country and stored in the database as adress. It may not contain '-')
        city (str): The city in which the patient lives (this is combined with street, postal code and country and stored in the database as adress. It may not contain '-')
        postal_code (str): The postal code of the place in which the patient lives (this is combined with street, city and country and stored in the database as adress. It may not contain '-')
        country (str): The country in which the patient lives (this is combined with street, city and postal code and stored in the database as adress. It may not contain '-')
        user_info (dict): A dictionary with all the information about the user, created by the function get_user_info. In this function this is used to get the user_id.
        confirmation_label (tkinter.Label): This object is changed in this function.
    """
    # Update user_info with new values
    user_info['phone_number'] = phone
    user_info['date_of_birth'] = dob
    user_info['address'] = f"{street}, {city}, {postal_code}, {country}"
    # Construct the full address
    full_address = f"{street}, {city}, {postal_code}, {country}"
    # Get the user_id from user_info
    user_id = user_info['user_id']
    # Update the confirmation label with success message
    confirmation_label.config(text="Information updated successfully!")
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()
    cursor.execute("""
            UPDATE Users 
            SET 
                Date_of_birth = ?, 
                Phone_number = ?, 
                Address = ? 
            WHERE 
                User_id = ?;
        """, (dob, phone, full_address, user_id))

    # Commit the changes
    conn.commit()
    cursor.close()
    conn.close()

def change_password(user_info, root):
    """
    Changes the window to display three field to allow the patient to change their password.

    parameters:
        user_info (dict):  A dictionary with all the information about the user, created by the function get_user_info
        root (tkinter.Tk): Contains the information about the window as it is currently displayed, this variable is used to change the current window to display something new.
    """
    # Clear all widgets in the root window
    for widget in root.winfo_children():
        widget.destroy()
    root.title("PsyBridge - Change Password")
    root.geometry("600x400")
    # Back button
    back_button = tk.Button(root, text="Back", font=('Arial', 12),
                            command=lambda: create_main_window(user_info, root))
    back_button.pack(anchor="se", side="bottom", padx=10, pady=10)
    # Title label
    title_label = tk.Label(root, text="Change password", font=("Arial", 18))
    title_label.pack(pady=10)
    # Current password label and entry
    current_password_label = tk.Label(root, text="Current Password", font=("Arial", 12))
    current_password_label.pack(pady=5)
    current_password_entry = tk.Entry(root, font=("Arial", 12), show="*")
    current_password_entry.pack(pady=5)

    # New password label and entry
    new_password_label = tk.Label(root, text="New Password", font=("Arial", 12))
    new_password_label.pack(pady=5)
    new_password_entry = tk.Entry(root, font=("Arial", 12), show="*")
    new_password_entry.pack(pady=5)

    # Repeat new password label and entry
    repeat_new_password_label = tk.Label(root, text="Repeat New Password", font=("Arial", 12))
    repeat_new_password_label.pack(pady=5)
    repeat_new_password_entry = tk.Entry(root, font=("Arial", 12), show="*")
    repeat_new_password_entry.pack(pady=5)

    error_or_success_label = tk.Label(root, text="", font=("Arial", 12), fg="red")
    error_or_success_label.pack(pady=5)
    root.error_or_success_label = error_or_success_label

    # Submit button
    submit_button = tk.Button(root, text="Confirm Change", font=('Arial', 12),
                              command=lambda: confirm_password_change(hashlib.md5(current_password_entry.get().encode()).hexdigest(),
                                                                      hashlib.md5(new_password_entry.get().encode()).hexdigest(),
                                                                      hashlib.md5(repeat_new_password_entry.get().encode()).hexdigest(),
                                                                      user_info, root))
    submit_button.pack(pady=20)


def confirm_password_change(current_password, new_password, repeat_new_password, user_info, root):
    """
    After clicking the confirm change button, this function checks to see if the current password is the same as the user typed, and whether the new password matches the second time the new password was typed.
    If the new password is valid, it is changed in the database and in the user_info variable.

    Parameters:
        current_password (str): contains a md5 hash of what was entered in the current password field.
        new_password (str): Contains an md5 hash of what was entered in the new password field.
        repeat_new_password (str): Contains an md5 hash of what was entered in the new repeat password field.
        user_info (dict):  A dictionary with all the information about the user, created by the function get_user_info
        root (tkinter.Tk): Contains the information about the window as it is currently displayed, this variable is used to change the current window to display something new.
    """
    # Check if the passwords match
    if new_password != repeat_new_password:
        root.error_or_success_label.config(text="New passwords do not match!", fg="red")
        return

    # Check if the current password is correct
    if current_password != user_info['password']:  # This assumes user_info contains the current password
        root.error_or_success_label.config(text="Incorrect current password!", fg="red")
        return

    # If passwords match, update the password
    user_info['password'] = new_password  # Update the user_info dictionary with the new password
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()
    cursor.execute("""
                UPDATE Users 
                SET 
                    Password = ? 
                WHERE 
                    User_id = ?;
            """, (new_password, user_id))

    # Commit the changes
    conn.commit()
    cursor.close()

    root.error_or_success_label.config(text="Password changed successfully!", fg="green")


# The main interface
def create_main_window(user_info, root=None, run_mainloop=True):
    """
    The window is changed to be the patient interface, if (for test purposes) no window exists, it is created.

    Parameters:
        user_info (dict):  A dictionary with all the information about the user, created by the function get_user_info
        root (tkinter.Tk): Contains the information about the window as it is currently displayed, this variable is used to change the current window to display something new.
        run_mainloop (bool): Can be set to FALSE to allow testing.
    """
    # Check if root is None, if so create the main Tk window
    if root is None:
        root = tk.Tk()

    # Clear the root window for reloading the main page
    for widget in root.winfo_children():
        widget.destroy()
    root.title("PsyBridge - Patient Interface")
    root.geometry("600x500")

    # Welcome text
    welcome_text = f"Hello {user_info.get('first_name', '[name]')} {user_info.get('last_name', '')},\nWelcome to your personal Psybridge page."
    if user_info.get('upcoming_meeting'):
        # Convert the appointment date to a datetime object
        upcoming_date = datetime.strptime(user_info['upcoming_meeting'][0], '%Y-%m-%d')
        # Format the date as 'dd-month-yyyy'
        formatted_date = upcoming_date.strftime('%d %B %Y')
        # Add the formatted date to the welcome text
        welcome_text += f"\n\nYour next appointment is {formatted_date} at {user_info['upcoming_meeting'][3]}, \nwith doctor {user_info['upcoming_meeting'][1]} {user_info['upcoming_meeting'][2]}."
    label_welcome = tk.Label(root, text=welcome_text, font=("Arial", 12))
    label_welcome.pack(anchor="n", pady=10)

    # Button setup
    frame_left = tk.Frame(root)
    frame_left.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.BOTH, expand=True)

    # btn_set_api_key = tk.Button(root, text="Set API Key", command=set_api_key, bg="pink", fg="black", width=20,
    #                             height=2)
    # btn_set_api_key.pack(pady=10)

    btn_ai_chat = tk.Button(frame_left, text="Chat with AI helper", bg="lightpink", fg="white", width=20, height=2,
                            command=lambda: show_ai_chat(root))
    btn_ai_chat.pack(pady=10, fill=tk.X)

    # Button to treatment notes and questionnaires
    btn_treatment_notes = tk.Button(frame_left, text="Treatment notes", bg="red", fg="white", width=20, height=2,
                                    command=lambda: show_treatment_notes(user_info, root))
    btn_treatment_notes.pack(pady=10, fill=tk.X)
    btn_questionnaires = tk.Button(frame_left, text="Questionnaires", bg="red", fg="white", width=20, height=2,
                                   command=lambda: questionaires(user_info, root))
    btn_questionnaires.pack(pady=10, fill=tk.X)
    btn_questionnaires = tk.Button(frame_left, text="Schedule appointment", bg="red", fg="white", width=20, height=2,
                                    command = lambda: ss.main(user_info, root, role=0))
    btn_questionnaires.pack(pady=10, fill=tk.X)
    btn_questionnaires = tk.Button(frame_left, text="Change password", bg="red", fg="white", width=20, height=2,
                                    command = lambda: change_password(user_info, root))
    btn_questionnaires.pack(pady=10, fill=tk.X)



    # Personal information (frame)
    frame_right = tk.Frame(root, bg="lightgrey")
    frame_right.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.BOTH, expand=True)

    label_personal_info = tk.Label(frame_right, text="Personal information:", font=("Arial", 12), bg="lightgrey")
    label_personal_info.pack(anchor="nw", padx=10, pady=(10, 5))
    label_birthday = tk.Label(frame_right, text=f"Date of birth: {user_info.get('date_of_birth', '[Date_of_birth]')}",
                              font=("Arial", 10), bg="lightgrey")
    label_birthday.pack(anchor="nw", padx=10, pady=5)
    label_address = tk.Label(frame_right, text=f"Address: {user_info.get('address', '[address]')}", font=("Arial", 10),
                             bg="lightgrey", wraplength=350)
    label_address.pack(anchor="nw", padx=10, pady=5)
    label_phone = tk.Label(frame_right, text=f"Phone number: {user_info.get('phone_number', '[phone number]')}",
                           font=("Arial", 10), bg="lightgrey")
    label_phone.pack(anchor="nw", padx=10, pady=5)

    # “Change personal information” button
    btn_change_info = tk.Button(frame_right, text="Change personal information", bg="red", fg="white",
                                command=lambda: change_information(user_info, root))
    btn_change_info.pack(anchor="s", pady=20, padx=10)

    if run_mainloop:
        root.mainloop()


#
# def set_api_key():
#     """
#     Helper function to prompt the user to input their OpenAI API key.
#     """
#     api_key = simpledialog.askstring("OpenAI API Key", "Please enter your OpenAI API key:", show='*')
#     if not api_key:
#         raise ValueError("OpenAI API key is required to proceed.")
#     openai.api_key = api_key

def show_ai_chat(root):
    """
    Opens a new window for AI chat and interacts with OpenAI GPT-4 using the latest OpenAI API interface.

    This function is triggered when the user submits a message in the AI chat interface.
    It performs the following steps:
    1. Retrieves the user's input from the input field.
    2. Displays the user's message in the conversation display area.
    3. Sends the user's message to OpenAI's GPT-4 model using the chat.completion API.
    4. Displays the AI's response or an error message in the conversation display.

    Parameters: root (tk. Tk())
    Root is the first window of patient interface

    Returns:
        None
    """
    openai.api_key = "sk-proj-xyBYtG85hwyGHCyp_2zGrkPetl4Ls86QR-BSPj8K2LNKNewhWR4LGeEWio" \
                     "hvbJbdpbec9qLwl7T3BlbkFJ_Xx8-PWyjAo2mvLiWB9YYWyEWP5bDyvpqtyQY_rZRh08SOdS3BLkJeaHf8IUarBgg8uf6WUlUA"

    # Create a new chat window
    ai_chat_window = tk.Toplevel(root)
    ai_chat_window.title("AI Chat")
    ai_chat_window.geometry("600x600")

    disclaimer = (
        "You can share your worries with the AI. Our version supports English conversations only.\n"
        "We do not retain your private information. Please note, AI cannot replace a psychologist.\n"
        "For serious situations, please seek help from a doctor."
    )
    message_label = tk.Label(ai_chat_window, text=disclaimer, font=("Arial", 10), wraplength=550, justify="left",
                             fg="red")
    message_label.pack(padx=20, pady=10)

    # Text box for displaying conversation
    conversation_display = tk.Text(ai_chat_window, wrap="word", state="disabled", height=15, width=50)
    conversation_display.pack(padx=20, pady=10)


    # Input field for user messages
    user_input = tk.Entry(ai_chat_window, font=("Arial", 12), width=40)
    user_input.pack(padx=20, pady=5)

    # Function to handle message sending
    def send_message():
        user_message = user_input.get()
        if not user_message.strip():  # strip the blank area
            return

        # Display the user's message
        conversation_display.config(state="normal") # Enable editing in the conversation display widget

        # display communication message as the form: "You: " prefix
        conversation_display.insert("end", f"You: {user_message}\n")

        # sisable editing in the conversation display widget to prevent user modifications
        conversation_display.config(state="disabled")

        # scroll the conversation display to the most recent message automatically
        conversation_display.see("end")

        # after sending the message, delete the user's input
        user_input.delete(0, "end")

        # Get response from openai 4.0 version
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful mental assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        ai_response = response.choices[0].message.content

        # display response from ai
        conversation_display.config(state="normal")
        conversation_display.insert("end", f"AI: {ai_response}\n")
        conversation_display.config(state="disabled")
        conversation_display.see("end")

            # commends below are for testing (with try)
        # except Exception as e:
        #     # Display error message
        #     conversation_display.config(state="normal")
        #     conversation_display.insert("end", f"AI: Sorry, an error occurred. ({e})\n")
        #     conversation_display.config(state="disabled")
        #     conversation_display.see("end")

    # Send button
    send_button = tk.Button(ai_chat_window, text="Send", font=("Arial", 12), command=send_message)
    send_button.pack(pady=5)

    # Close button
    close_button = tk.Button(ai_chat_window, text="Close", font=("Arial", 12), command=ai_chat_window.destroy)
    close_button.pack(pady=10)

# main
def main(user_id, root):
    """
    Calls the function to get patient information from the database and calls the function to change the window to be patient interface.

    Parameters:
        user_id (int): Corresponds with the user_id of the patient in the database. This ID is obtained during the login.
        root (tkinter.Tk): Contains the information about the window as it is currently displayed, this variable is used to change the current window to display something new.
    """
    user_info = get_user_info(user_id)
    create_main_window(user_info, root)

if __name__ == "__main__":
    main(user_id, None)

