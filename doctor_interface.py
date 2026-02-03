import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import hashlib
import scheduling_system as ss

navigation_stack = []

def set_geometry(root, window_width=675, window_height=450):
    # Get the height and width of the screen
    screen_height = root.winfo_screenheight()
    screen_width = root.winfo_screenwidth()
    # Calculate the x- and y-coordinate to center window
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    # Centering the window on the screen
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

def go_back(user_info, root):
    if navigation_stack:
        # Get the previous frame
        previous_frame = navigation_stack.pop()
        # Go to the previous frame
        previous_frame(user_info, root)
    else:
        print('No previous frame to go back to')

def create_back_button(parent, user_info, root):
    back_button = tk.Button(parent, text="Back", font=('Arial', 12), command=lambda: go_back(user_info, root))
    # Layout: Bottom-right corner with padding
    back_button.pack(anchor="se", side="bottom", padx=10, pady=10)

def get_doctor_info(user_id):
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()

    # Get the doctor's ID
    cursor.execute("SELECT Doctor_id FROM Doctors WHERE User_id = ?", (user_id,))
    doctor_id = cursor.fetchone()[0]

    # Get the doctor's personal information
    cursor.execute("SELECT First_name, Last_name, User_name, Password, Date_of_birth, Phone_number, Address FROM Users WHERE User_id = ?",
                   (user_id,))
    doctor_data = cursor.fetchone()
    if doctor_data:
        first_name, last_name, user_name, password, date_of_birth, phone_number, address = doctor_data
    else:
        raise ValueError("User ID not found in database")

    # Find all upcoming appointments for the doctor, including patient information
    cursor.execute(""" 
        SELECT a.Date_of_meeting, u.First_name AS Patient_first_name, u.Last_name AS Patient_last_name
        FROM Meets m
        JOIN Appointment_details a ON m.Examination_id = a.Examination_id
        JOIN Patients p ON m.Patient_id = p.Patient_id
        JOIN Users u ON p.User_id = u.User_id
        WHERE m.Doctor_id = ?
        ORDER BY a.Date_of_meeting ASC;
    """, (doctor_id,))
    appointments = cursor.fetchall()

    upcoming_meeting = []
    upcoming_meetings = [
        (datetime.strptime(appointment[0], '%Y-%m-%d'), appointment[1], appointment[2])
        for appointment in appointments if appointment[0] >= datetime.now().strftime('%Y-%m-%d')
    ]

    if upcoming_meetings:
        closest_appointment = min(upcoming_meetings, key=lambda x: x[0])
        upcoming_meeting = [
            closest_appointment[0].strftime('%Y-%m-%d'),
            closest_appointment[1],
            closest_appointment[2]
        ]

    cursor.close()
    conn.close()

    # Return user information
    return {
        "user_id": user_id,
        "doctor_id": doctor_id,
        "first_name": first_name,
        "last_name": last_name,
        "user_name": user_name,
        "password": password,
        "date_of_birth": date_of_birth,
        "phone_number": phone_number,
        "address": address,
        "upcoming_meeting": upcoming_meeting
    }

def change_personal_information(user_info, root):
    # Add the current frame to the navigation stack
    navigation_stack.append(create_home_page)
    # Clear all widgets in the root window
    for widget in root.winfo_children():
        widget.destroy()
    # Set window title and geometry
    root.title("Personal Information")
    set_geometry(root, window_height=470)
    # Back button
    create_back_button(root, user_info, root)

    # Title label
    title_label = tk.Label(root, text="Update your information", font=("Arial", 18))
    title_label.pack(pady=10)

    # Create a frame for the personal information
    info_frame = tk.Frame(root)
    info_frame.pack(pady=10, padx=20, fill="both", expand=True)

    # Configure the grid columns
    info_frame.columnconfigure(0, weight=1)  # Column for labels
    info_frame.columnconfigure(1, weight=2)  # Column for entry fields

    # Column 1: Labels
    labels = [
        "Name:", "Username:", "Date of Birth (DD-MM-YYYY):",
        "Phone Number:", "Street Address:", "City:", "Postal Code:", "Country:"
    ]
    for i, label_text in enumerate(labels):
        tk.Label(info_frame, text=label_text, font=("Arial", 12)).grid(row=i, column=0, sticky="w", pady=5, padx=10)

    # Column 2: Entry fields
    name_entry = tk.Entry(info_frame, font=("Arial", 12))
    name_entry.insert(0, f"{user_info['first_name']} {user_info.get('last_name', '')}") # Combine the first and the last name
    name_entry.grid(row=0, column=1, pady=5, sticky='ew')

    username_entry = tk.Entry(info_frame, font=("Arial", 12))
    username_entry.insert(0, user_info['user_name'])
    username_entry.grid(row=1, column=1, pady=5, sticky='ew')

    # Split date of birth into three fields
    dob_frame = tk.Frame(info_frame)
    dob_frame.grid(row=2, column = 1, pady=5, sticky="ew")
    day_entry = tk.Entry(dob_frame, width=3, font=('Arial', 12))
    day_entry.grid(row=0, column=2)
    day_entry.insert(0, user_info['date_of_birth'].split('-')[0])
    month_entry = tk.Entry(dob_frame, width=3, font=('Arial', 12))
    month_entry.grid(row=0, column=3, padx=5)
    month_entry.insert(0, user_info['date_of_birth'].split('-')[1])
    year_entry = tk.Entry(dob_frame, width=5, font=('Arial', 12))
    year_entry.grid(row=0, column=4, padx=5)
    year_entry.insert(0, user_info['date_of_birth'].split('-')[2])

    phone_entry = tk.Entry(info_frame, font=('Arial', 12))
    phone_entry.insert(0, user_info['phone_number'])
    phone_entry.grid(row=3, column=1, pady=5, sticky="ew")

    address_entries = [
        tk.Entry(info_frame, font=("Arial", 12)) for _ in range(4)
    ]
    address_parts = user_info['address'].split(", ")
    for i, entry in enumerate(address_entries):
        entry.insert(0, address_parts[i] if i < len(address_parts) else "")
        entry.grid(row=4+i, column=1, pady=5, sticky="ew")


    # Save button
    save_button = tk.Button(root, text="Save Changes", font=('Arial', 12),
                            command=lambda: save_changes(
                                name_entry.get(),
                                username_entry.get(),
                                f"{day_entry.get()}-{month_entry.get()}-{year_entry.get()}",
                                phone_entry.get(),
                                ", ".join([entry.get() for entry in address_entries]), # Join the address entries into a single string
                                user_info,
                                confirmation_label
                            ))
    save_button.pack(pady=5)

    # Confirmation label, initially empty
    confirmation_label = tk.Label(root, text="", font=("Arial", 12), fg="red")
    confirmation_label.pack(pady=5)

def save_changes(name, username, dob, phone, address, user_info, confirmation_label):
    # Split the name into the first and last name
    names = name.split(maxsplit=1)
    first_name = names[0]
    last_name = names[1] if len(names) > 1 else ""

    # Validate date of birth Format
    try:
        day, month, year = map(int, dob.split('-'))

        # Check if day, month, and year are in a valid range
        if not (1 <= day <= 31 and 1 <= month <= 12 and len(str(year)) == 4):
            raise ValueError("invalid date values")

        # Check if the date is valid (e.g., Feb 30 is invalid)
        try:
            datetime(year, month, day)
        except ValueError:
            raise ValueError("invalid date")

        # Check if the birth year is not in the future
        current_year = datetime.now().year
        if year > current_year:
            raise ValueError("birth year cannot be in the future.")

    except ValueError as e:
        confirmation_label.config(text=f"Invalid date of birth: {str(e)}", fg="red")
        return

    # Validate phone number (simple numeric check)
    if not phone.isdigit() or len(phone) != 11:
        confirmation_label.config(text="Invalid phone number: ensure it contains 11 digits.", fg="red")
        return

    # Check if any value changed
    if (
        first_name == user_info['first_name'] and
        last_name == user_info['last_name'] and
        username == user_info['user_name'] and
        dob == user_info['date_of_birth'] and
        phone == user_info['phone_number'] and
        address == user_info['address']
    ):
        confirmation_label.config(text="You haven't updated any information yet!")
        return

    # Update user_info with new values
    user_info['first_name'] = first_name
    user_info['last_name'] = last_name
    user_info['user_name'] = username
    user_info['date_of_birth'] = dob
    user_info['phone_number'] = phone
    user_info['address'] = address

    # Update the database
    user_id = user_info['user_id']
    try:
        conn = sqlite3.connect('Database.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Users 
            SET 
                First_name = ?,
                Last_name = ?,
                User_name = ?, 
                Date_of_birth = ?, 
                Phone_number = ?, 
                Address = ? 
            WHERE 
                User_id = ?;
        """, (first_name, last_name, username, dob, phone, address, user_id))
        conn.commit()
        confirmation_label.config(text="Information updated successfully!", fg="green")
    except sqlite3.Error as e:
        confirmation_label.config(text=f"Database error: {e}", fg="red")
    finally:
        cursor.close()
        conn.close()

    # Update the confirmation label with a success message
    confirmation_label.config(text="Information updated successfully!", fg="green")

def questionnaire_list(user_info, root):
    # Add the current frame to the navigation stack
    navigation_stack.append(create_home_page)
    # Clear all widgets in the root window
    for widget in root.winfo_children():
        widget.destroy()
    # Set window title and geometry
    root.title("Questionnaires")
    set_geometry(root)
    # Back button
    create_back_button(root, user_info, root)

    """Function to display a list of questionnaires and the patients who have access to each one."""
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()

    # Get a list of all questionnaires
    cursor.execute("SELECT Questionaire_id, Questionaire_name FROM Questionaire")
    questionnaires = cursor.fetchall()

    label = tk.Label(root, text="List of Questionnaires", font=("Arial", 14))
    label.pack(pady=20)

    # Create a frame to display the list of questionnaires
    list_frame = tk.Frame(root)
    list_frame.pack(pady=10, fill="both", expand=True)

    # Display each questionnaire in the list
    for questionnaire in questionnaires:
        q_id, q_name = questionnaire
        questionnaire_button = tk.Button(list_frame, text=q_name, font=("Arial", 12), width=40,
                                         command=lambda: show_patients_for_questionnaire(q_id, user_info, root))
        questionnaire_button.pack(pady=5)

    cursor.close()
    conn.close()

def show_patients_for_questionnaire(questionnaire_id, user_info, root):
    # Add the current frame to the navigation stack
    navigation_stack.append(questionnaire_list)
    # Clear all widgets in the root window
    for widget in root.winfo_children():
        widget.destroy()
    # Set window title and geometry
    root.title(f"Access to questionnaire {questionnaire_id}")
    set_geometry(root)
    # Back button
    create_back_button(root, user_info, root)

    # Search bar
    search_frame = tk.Frame(root)
    search_frame.pack(pady=10)

    search_label = tk.Label(search_frame, text="Search:", font=("Arial", 12))
    search_label.pack(side=tk.LEFT, padx=5)

    search_entry = tk.Entry(search_frame, font=("Arial", 12), width=30)
    search_entry.pack(side=tk.LEFT, padx=5)

    search_button = tk.Button(search_frame, text="Search", font=("Arial", 12),
                              command=lambda: display_patients(list_frame, search_entry.get(), questionnaire_id))
    search_button.pack(side=tk.LEFT, padx=5)

    # Create a scrolling canvas
    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Frame inside the canvas for content
    list_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=list_frame, anchor="nw")

    # Display initial list of patients
    display_patients(list_frame, '', questionnaire_id)


def display_patients(list_frame, search_query, questionnaire_id):
    """Displays the list of patients with access status and filters by search query."""
    # Clear previous list
    for widget in list_frame.winfo_children():
        widget.destroy()

    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()

    # Fetch patients based on search query
    cursor.execute("""
            SELECT u.First_name, u.Last_name, p.Patient_id, 
                   CASE WHEN h.Questionaire_id IS NOT NULL THEN 1 ELSE 0 END AS has_access
            FROM Patients p
            JOIN Users u ON p.User_id = u.User_id
            LEFT JOIN has_access_to h ON p.Patient_id = h.Patient_id AND h.Questionaire_id = ?
            WHERE u.First_name LIKE ? OR u.Last_name LIKE ?
        """, (questionnaire_id, f"%{search_query}%", f"%{search_query}%"))
    patients = cursor.fetchall()

    # Add each patient to the list with toggle buttons
    for first_name, last_name, patient_id, has_access in patients:
        status_color = "green" if has_access else "red"
        button_text = f"{first_name} {last_name} - {'Available' if has_access else 'Unavailable'}"

        toggle_button = tk.Button(
            list_frame,
            text=button_text,
            bg=status_color,
            fg="white",
            width=40,
            command=lambda pid=patient_id, access=has_access: toggle_access(pid, questionnaire_id, access, list_frame,
                                                                            search_query)
        )
        toggle_button.pack(pady=5)

    cursor.close()
    conn.close()

def toggle_access(patient_id, questionnaire_id, has_access, list_frame, search_query):
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()

    if has_access:
        # Remove access
        cursor.execute("""
                DELETE FROM has_access_to 
                WHERE Patient_id = ? AND Questionaire_id = ?
            """, (patient_id, questionnaire_id))
    else:
        # Grant access
        cursor.execute("""
                INSERT INTO has_access_to (Patient_id, Questionaire_id)
                VALUES (?, ?)
            """, (patient_id, questionnaire_id))

    conn.commit()
    cursor.close()
    conn.close()

    # Refresh patient list with current search query
    display_patients(list_frame, search_query, questionnaire_id)

def patient_list(user_info, root):
    # Add the current frame to the navigation stack
    navigation_stack.append(create_home_page)
    # Clear all widgets in the root window
    for widget in root.winfo_children():
        widget.destroy()
    # Set window title and geometry
    root.title("Patients")
    set_geometry(root)
    # Back button
    create_back_button(root, user_info, root)

    # Top frame with "Patient list" title and search bar
    frame_top = tk.Frame(root)
    frame_top.pack(fill=tk.X, pady=10)
    # Red bar with "Patient list" label
    title_bar = tk.Label(frame_top, text="Patient list", fg="white", bg="red", font=("Arial", 14), width=20)
    title_bar.pack(side=tk.LEFT, padx=10)
    # Search bar
    search_entry = tk.Entry(frame_top, font=("Arial", 12))
    search_entry.insert(0, "Search patient...")
    search_entry.bind("<FocusIn>", lambda e: clear_placeholder())
    search_entry.bind("<FocusOut>", lambda e: restore_placeholder())
    search_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    # Bind the root window to defocus the search bar on click elsewhere
    def defocus(event):
        # Ensure only clicks outside the search_entry and other Entry widgets defocus
        if event.widget != search_entry and not isinstance(event.widget, tk.Entry):
            root.focus()
    root.bind("<Button-1>", defocus)
    # Function to defocus when pressing Enter
    def defocus_on_enter(event):
        search_entry.master.focus_set()  # Focus the parent of the search_entry
    search_entry.bind("<Return>", defocus_on_enter)
    # Placeholder handling
    def clear_placeholder():
        if search_entry.get() == "Search patient...":
            search_entry.delete(0, tk.END)
    def restore_placeholder():
        if search_entry.get() == "":
            search_entry.insert(0, "Search patient...")
    # Function to filter patient list based on the search text
    def search_patient():
        search_term = search_entry.get().lower()
        for patient_button in patient_buttons:
            label_patient_name = patient_button.winfo_children()[0]
            patient_name = label_patient_name.cget('text').lower()
            if search_term in patient_name:
                patient_button.grid() # Make the button visible
            else:
                patient_button.grid_remove() # Temporarily hide button without disrupting the grid layout
        update_scroll_region()  # Update scroll region after filtering
    search_entry.bind("<KeyRelease>", lambda e: search_patient())

    # Fetch patients assigned to the doctor
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.Patient_id, u.First_name, u.Last_name, 
               GROUP_CONCAT(d.Diagnose, ', ') AS Diagnoses
        FROM Treats t
        JOIN Patients p ON t.Patient_id = p.Patient_id
        JOIN Users u ON p.User_id = u.User_id
        LEFT JOIN Diagnoses ds ON p.Patient_id = ds.Patient_id
        LEFT JOIN Diagnosis d ON ds.Diagnose_id = d.Diagnose_id
        WHERE t.Doctor_id = ?
        GROUP BY p.Patient_id
        ORDER BY u.First_name, u.Last_name;
    """, (user_info['doctor_id'],))
    patients = cursor.fetchall()

    # Fetch the next appointment for each patient and include it in the data
    patient_data_list = []
    for patient in patients:
        patient_id, first_name, last_name, diagnosis = patient
        diagnoses_list = diagnosis.split(", ")
        unique_diagnoses = ",\n".join(sorted(set(diagnoses_list)))

        cursor.execute("""
            SELECT Date_of_meeting 
            FROM Appointment_details a
            JOIN Meets m ON a.Examination_id = m.Examination_id
            WHERE m.Patient_id = ?
            ORDER BY Date_of_meeting LIMIT 1
        """, (patient_id,))
        next_appointment_result = cursor.fetchone()

        if next_appointment_result:
            next_appointment = next_appointment_result[0]
        else:
            next_appointment = None
        patient_data_list.append((patient_id, first_name, last_name, unique_diagnoses, next_appointment))

    # Sort the patient data:
    # 1. Patients with appointments first, by date
    # 2. Patients without appointments alphabetically by first name
    patient_data_list.sort(key=lambda x: (
        x[4] is None, # Sort patients without appointments last
        datetime.strptime(x[4], '%Y-%m-%d') if x[4] else None, # Sort by appointment date
        x[1], # Sort by first name
        x[2] # Sort by last name when first names are equal
    ))

    # Frame for the list of patients (with scrollable canvas)
    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    frame_patients = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame_patients, anchor="nw")
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Update scroll region and toggle scrollbar visibility
    def update_scroll_region():
        frame_patients.update_idletasks() # Update inner frame dimensions
        canvas.config(scrollregion=canvas.bbox("all"))
        toggle_scrollbar()

    # Dynamic scrollbar visibility and behavior
    def toggle_scrollbar():
        canvas.update_idletasks() # Update canvas dimensions
        bbox = canvas.bbox("all")  # Get the bounding box of all content in the canvas

        if bbox:
            canvas_height = canvas.winfo_height()
            content_height = bbox[3] - bbox[1]

            if content_height > canvas_height:
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Show scrollbar
                canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
            else:
                scrollbar.pack_forget()  # Hide scrollbar
                canvas.unbind_all("<MouseWheel>")

    def _on_mouse_wheel(event):
        if canvas.winfo_exists():  # Ensure the canvas is still present
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

    # List to store patient buttons for searching
    patient_buttons = []
    # Display sorted patients
    for i, patient_data in enumerate(patient_data_list):
        patient_id, first_name, last_name, diagnosis, next_appointment = patient_data

        # Create patient button frame
        patient_button_frame = tk.Frame(frame_patients, relief="solid", bd=2)
        patient_button_frame.grid(row=i, column=0, pady=5, padx=20, sticky="ew")

        # Configure the grid for the patient button frame
        patient_button_frame.grid_columnconfigure(0, weight=1)  # Left column
        patient_button_frame.grid_columnconfigure(1, weight=1)  # Right column

        # Create a list of labels to pack in the frame
        labels = [
            (f"{first_name} {last_name}", 12, 0, "w"),  # Patient name
            (f"Diagnoses: {diagnosis}", 10, 0, "w"),  # Diagnosis
            (f"Next appointment: {'None' if next_appointment is None else next_appointment}", 12, 1, "e") # Next appointment
        ]

        # Create and pack each label
        for text, font_size, col, anchor in labels:
            label = tk.Label(patient_button_frame, text=text, font=("Arial", font_size), anchor=anchor, wraplength=350)
            label.grid(row=labels.index((text, font_size, col, anchor)), column=col, sticky=anchor, padx=10, pady=2)

        # Store patient button frame (for the search function)
        patient_buttons.append(patient_button_frame)
        # Bind click event
        patient_button_frame.bind("<Button-1>", lambda event, p=patient_data: open_patient_profile(p, user_info, root))

    # Update scroll region after widgets are added
    update_scroll_region()

    cursor.close()
    conn.close()

def open_patient_profile(patient, user_info, root):
    patient_id, first_name, last_name, diagnosis, next_appointment = patient
    # Add the current frame to the navigation stack
    navigation_stack.append(patient_list)
    # Clear all widgets in the root window
    for widget in root.winfo_children():
        widget.destroy()
    # Set window title and geometry
    root.title(f"{first_name} {last_name}'s profile")
    set_geometry(root, window_width=1350, window_height=900)
    # Back button
    create_back_button(root, user_info, root)

    # Main frame to split into left and right halves
    frame_main = tk.Frame(root)
    frame_main.pack(fill=tk.BOTH, expand=True)

    # Top frame with patient name
    frame_top = tk.Frame(frame_main)
    frame_top.pack(fill=tk.X, pady=10)
    title_bar = tk.Label(frame_top, text=f"{first_name} {last_name}", fg="white", bg="red", font=("Arial", 14), width=20)
    title_bar.pack(side=tk.LEFT, padx=10)

    # Left frame for treatment notes
    frame_left = tk.Frame(frame_main)
    frame_left.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.BOTH, expand=True)

    # Right frame for next appointment and questionnaires
    frame_right = tk.Frame(frame_main)
    frame_right.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.BOTH, expand=True)

    # Frame to hold treatment notes content, with grey background
    frame_treatment_notes = tk.Frame(frame_left, bg="lightgrey")
    frame_treatment_notes.pack(fill=tk.BOTH, expand=True)

    # Title of page
    label_treatment_notes = tk.Label(frame_treatment_notes, text="Treatment notes", font=("Arial", 18), bg="lightgrey")
    label_treatment_notes.pack(padx=20, pady=10, anchor="n")

    # Setup Treeview for dynamic table display
    columns = ("Diagnosis", "Date", "Treatment Plan")
    tree = ttk.Treeview(frame_treatment_notes, columns=columns, show="headings")

    # Sort States for sorting columns
    sort_states = {col: False for col in columns}  # False = Ascending, True = Descending

    # Function to sort Treeview columns
    def sort_tree(col):
        reverse = sort_states[col]
        data = [(tree.set(child, col), child) for child in tree.get_children("")]
        try:
            if col == "Date":
                data.sort(key=lambda item: datetime.strptime(item[0], '%Y-%m-%d'), reverse=reverse)
            else:
                data.sort(key=lambda item: float(item[0]) if item[0].isdigit() else item[0].lower(), reverse=reverse)
        except ValueError:
            data.sort(reverse=reverse)
        for index, (_, item) in enumerate(data):
            tree.move(item, "", index)
        sort_states[col] = not reverse
        update_heading(col)

    def update_heading(sorted_column):
        for column in columns:
            if column == sorted_column:
                arrow = "▲" if sort_states[column] else "▼"
                tree.heading(column, text=f"{column} {arrow}")
            else:
                tree.heading(column, text=column)

    # Configuring column headers and adding sorting function
    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_tree(c))
        tree.column(col, anchor="w", width=150 if col != "Date" else 100)

    def get_treatment_notes(patient_id):
        conn = sqlite3.connect('Database.db')
        cursor = conn.cursor()

        # Fetch treatment notes for the given patient, sorted by newest date first
        cursor.execute("""
            SELECT d.Diagnose, ad.Date_of_meeting, ad.Treatment_notes, d.Diagnose_id
            FROM Meets m
            LEFT JOIN Appointment_details ad ON m.Examination_id = ad.Examination_id
            LEFT JOIN Diagnoses ds ON ds.Patient_id = m.Patient_id AND ds.Doctor_id = m.Doctor_id AND ds.Diagnose_id = ad.Examination_id
            LEFT JOIN Diagnosis d ON d.Diagnose_id = ds.Diagnose_id
            WHERE m.Patient_id = ?
            ORDER BY ad.Date_of_meeting DESC;
        """, (patient_id,))
        treatment_notes = cursor.fetchall()

        conn.close()
        return treatment_notes

    # Refresh the Treeview
    def refresh_treeview(tree, patient_id):
        for item in tree.get_children():
            tree.delete(item)
        treatment_notes = get_treatment_notes(patient_id)
        for note in treatment_notes:
            date_of_meeting = note[1] or ''
            treatment_plan = note[2] or 'N/A'  # Default to "N/A" if missing
            diagnosis = note[0] or 'N/A'  # Default to "N/A" if missing
            if date_of_meeting and treatment_plan != 'N/A':  # Only show valid entries
                tree.insert("", "end", values=(diagnosis, date_of_meeting, treatment_plan))

    refresh_treeview(tree, patient_id)

    # Pack the Treeview to expand dynamically
    tree.pack(fill=tk.BOTH, expand=True)
    update_heading("Date")  # Initially sort by Date

    def edit_notes(patient, user_info, root, tree):
        # Extract patient details
        patient_id, first_name, last_name, diagnosis, next_appointment = patient

        # Add the current frame to the navigation stack
        navigation_stack.append(lambda user_info, root: open_patient_profile(patient, user_info, root))

        # Clear all widgets in the root window
        for widget in root.winfo_children():
            widget.pack_forget()

        # Set window title and geometry
        root.title("Edit Notes")
        set_geometry(root)

        # Main frame to split into left and right halves
        frame_main = tk.Frame(root)
        frame_main.pack(fill=tk.BOTH, expand=True)

        # Top frame with patient name
        frame_top = tk.Frame(frame_main)
        frame_top.pack(fill=tk.X, pady=10)

        # Top red title bar with patient's name
        title_bar = tk.Label(frame_top, text=f"{first_name} {last_name}", fg="white", bg="red", font=("Arial", 14),
                             width=20)
        title_bar.pack(side=tk.LEFT, padx=10)

        # Main frame for content with light-grey background
        frame_content = tk.Frame(frame_main, bg="lightgrey")
        frame_content.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Title of page
        label_treatment_notes = tk.Label(frame_content, text="Treatment notes", font=("Arial", 18), bg="lightgrey")
        label_treatment_notes.grid(row=0, column=0, columnspan=2, padx=20, pady=10)

        # Frame configuration for grid layout
        frame_content.columnconfigure(0, weight=1)
        frame_content.columnconfigure(1, weight=3)

        # "Diagnosis" label and input
        tk.Label(frame_content, text="Diagnosis:", bg="lightgrey", font=("Arial", 12)).grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        entry_diagnosis = tk.Entry(frame_content, font=("Arial", 12), width=50)
        entry_diagnosis.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        entry_diagnosis.focus_set()

        # "Treatment Plan" label and input
        tk.Label(frame_content, text="Treatment Plan:", bg="lightgrey", font=("Arial", 12)).grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )
        entry_treatment_plan = tk.Entry(frame_content, font=("Arial", 12), width=50)
        entry_treatment_plan.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Add spacer frame to push buttons to the bottom
        spacer = tk.Frame(frame_content, bg="lightgrey")
        spacer.grid(row=3, column=0, columnspan=2, sticky="nsew")
        frame_content.rowconfigure(3, weight=1)  # Ensures spacer expands

        # Confirm and Cancel buttons
        frame_buttons = tk.Frame(frame_content, bg="lightgrey")
        frame_buttons.grid(row=4, column=0, columnspan=2, pady=20, sticky="ew")

        # Configure column weights for equal spacing
        frame_buttons.columnconfigure(0, weight=1)
        frame_buttons.columnconfigure(1, weight=1)

        # Add buttons with red background
        btn_confirm = tk.Button(frame_buttons, text="Confirm", font=("Arial", 12), bg="red", fg="white",
                                command=lambda: on_confirm(tree))
        btn_confirm.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

        btn_cancel = tk.Button(frame_buttons, text="Cancel", font=("Arial", 12), bg="red", fg="white",
                               command=lambda: on_cancel())
        btn_cancel.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        def on_confirm(tree):
            diagnosis = entry_diagnosis.get().strip()
            treatment_plan = entry_treatment_plan.get().strip()

            if not diagnosis or not treatment_plan:
                tk.messagebox.showerror("Error", "Both Diagnosis and Treatment Plan are required.")
                return

            try:
                # Use current date for consistency
                diagnose_date = datetime.now().strftime('%Y-%m-%d')

                conn = sqlite3.connect('Database.db')
                cursor = conn.cursor()

                # Insert a new diagnosis
                cursor.execute(
                    "INSERT INTO Diagnosis (Diagnose_date, Diagnose) VALUES (?, ?)",
                    (diagnose_date, diagnosis)
                )
                diagnose_id = cursor.lastrowid

                # Insert a new appointment detail
                cursor.execute(
                    "INSERT INTO Appointment_details (Date_last_modified, Date_of_meeting, Treatment_notes) VALUES (?, ?, ?)",
                    (diagnose_date, diagnose_date, treatment_plan)
                )
                examination_id = cursor.lastrowid

                # Link Diagnosis and Patient/Doctor in Diagnoses table
                cursor.execute(
                    "INSERT INTO Diagnoses (Patient_id, Doctor_id, Diagnose_id) VALUES (?, ?, ?)",
                    (patient_id, user_info["doctor_id"], diagnose_id)
                )

                # Link Appointment_detail in Meets table
                cursor.execute(
                    "INSERT INTO Meets (Patient_id, Doctor_id, Examination_id) VALUES (?, ?, ?)",
                    (patient_id, user_info["doctor_id"], examination_id)
                )

                conn.commit()
                tk.messagebox.showinfo("Success", "New diagnosis added successfully.")

                # Refresh Treeview
                refresh_treeview(tree, patient_id)
                conn.close()

            except sqlite3.Error as e:
                tk.messagebox.showerror("Database Error", f"An error occurred: {e}")
                conn.rollback()
                conn.close()

        def on_cancel():
            go_back(user_info, root)

    # Edit Treatment Notes button
    edit_notes_button = tk.Button(frame_left, text="Add notes", font=("Arial", 12), fg="white", bg="red", command=lambda: edit_notes(patient, user_info, root, tree))
    edit_notes_button.pack(side=tk.BOTTOM, pady=10)

    # ---------------- RIGHT HALF ----------------
    # Top section of the right frame (for Next Appointment)
    frame_right_top = tk.Frame(frame_right, bg="lightgrey")
    frame_right_top.pack(fill=tk.X, padx=10)

    # Next Appointment section
    next_appointment_label = tk.Label(frame_right_top, text="Next appointment", font=("Arial", 18), bg="lightgrey")
    next_appointment_label.pack(side=tk.TOP, anchor='w', padx=10, pady=5)
    next_appointment_value = tk.Label(frame_right_top, text="", font=("Arial", 12), bg="lightgrey")
    next_appointment_value.pack(anchor='w', padx=10, pady=5)

    # Bottom section of the right frame (for Questionnaires)
    frame_right_bottom = tk.Frame(frame_right, bg="lightgrey")
    frame_right_bottom.pack(fill=tk.BOTH, expand=True, padx=10, pady=20)

    # Questionnaires section
    questionnaires_label = tk.Label(frame_right_bottom, text="Questionnaires", font=("Arial", 18), bg="lightgrey")
    questionnaires_label.pack(side=tk.TOP, pady=10, padx=10, anchor='w')

    # Display the appointment date and time
    def load_appointment():
        conn = sqlite3.connect('Database.db')
        cursor = conn.cursor()
        cursor.execute("""
           SELECT Date_of_meeting FROM Appointment_details
           JOIN Meets ON Appointment_details.Examination_id = Meets.Examination_id
           WHERE Meets.Patient_id = ?
           ORDER BY Date_of_meeting LIMIT 1
        """, (patient_id,))
        next_appointment_result = cursor.fetchone()
        conn.close()

        if next_appointment_result:
            next_appointment_value.config(text=next_appointment_result[0])
        else:
            next_appointment_value.config(text="No upcoming appointment")

    load_appointment()

    # Function to load available questionnaires for the patient
    def load_questionnaires():
        conn = sqlite3.connect('Database.db')
        cursor = conn.cursor()
        cursor.execute("""
           SELECT q.Questionaire_name
           FROM has_access_to h
           JOIN Questionaire q ON h.Questionaire_id = q.Questionaire_id
           WHERE h.Patient_id = ?
        """, (patient_id,))
        questionnaires_result = cursor.fetchall()
        conn.close()

        if questionnaires_result:
            for idx, (questionnaire_name,) in enumerate(questionnaires_result):
                button = tk.Button(frame_right_bottom, text=questionnaire_name, font=("Arial", 12),
                                  command=lambda name=questionnaire_name: open_questionnaire(name))
                button.pack(pady=5, anchor='w', padx=10)
        else:
            no_questionnaire_label = tk.Label(frame_right_bottom, text="No questionnaires assigned to this patient.",
                                             font=("Arial", 12), bg="lightgray")
            no_questionnaire_label.pack(pady=10)

    # Call to load questionnaires at the start
    load_questionnaires()

    # Function to open a selected questionnaire
    def open_questionnaire(questionnaire_name):
        conn = sqlite3.connect('Database.db')
        cursor = conn.cursor()

        # Get the questionnaire ID based on its name
        cursor.execute("""
           SELECT Questionaire_id FROM Questionaire
           WHERE Questionaire_name = ?
        """, (questionnaire_name,))
        questionnaire_data = cursor.fetchone()

        if questionnaire_data:
            questionnaire_id = questionnaire_data[0]

            # Fetch patients who have filled out this questionnaire and their answers
            cursor.execute("""
               SELECT f.Patient_id, q.Questionaire_date, qa.Answer, qs.Question_number
               FROM Fills_in f
               JOIN Questionaire_responses q ON f.Attempt_id = q.Attempt_id
               JOIN Question_answers qa ON qa.Attempt_id = f.Attempt_id
               JOIN Questions qs ON qa.Question_id = qs.Question_number
               WHERE f.Questionaire_id = ?
            """, (questionnaire_id,))
            responses = cursor.fetchall()

            # Clear any previous answers or messages from the GUI
            for widget in frame_right_bottom.winfo_children():  # Clear the frame to reset the view
                widget.destroy()

            if responses:
                # Display the patient's answers in the GUI
                for response in responses:
                    patient_id, date, answer, question_number = response
                    answer_label = tk.Label(frame_right_bottom,
                                           text=f"Patient {patient_id} answered Question {question_number} on {date}: {answer}",
                                           font=("Arial", 12))
                    answer_label.pack(pady=5, anchor='w', padx=10)
            else:
                # Show a popup messagebox with the same message
                messagebox.showinfo("No Answers", "No answers yet for this questionnaire.")
                # After showing the messagebox, reload the list of questionnaires
                load_questionnaires()

        else:
            # Clear the frame and show the error message if the questionnaire is not found
            for widget in frame_right_bottom.winfo_children():
                widget.destroy()

            # Show an error popup and clear the screen
            messagebox.showerror("Error", "Questionnaire not found.")
            # After showing the error, reload the list of questionnaires
            load_questionnaires()

        conn.close()

def change_password(user_info, root):
    """
    Changes the window to display three field to allow the patient to change their password.

    parameters:
        user_info (dict):  A dictionary with all the information about the user, created by the function get_user_info
        root (tkinter.Tk): Contains the information about the window as it is currently displayed, this variable is used to change the current window to display something new.
    """
    # Clear all widgets in the root window

    # Add the current frame to the navigation stack
    navigation_stack.append(create_home_page)
    # Clear all widgets in the root window
    for widget in root.winfo_children():
        widget.destroy()
    # Set window title and geometry
    root.title("Change password")
    set_geometry(root)
    # Back button
    create_back_button(root, user_info, root)

    # Title label
    title_label = tk.Label(root, text="Change password", font=("Arial", 18))
    title_label.pack(pady=10)

    # Labels and entries for password fields
    fields = [
        {"label": "Current password", "entry_var": "current_password"},
        {"label": "New password", "entry_var": "new_password"},
        {"label": "Repeat new password", "entry_var": "repeat_new_password"}
    ]

    entries = {}
    for field in fields:
        label = tk.Label(root, text=field["label"], font=("Arial", 12))
        label.pack(pady=5)

        entry = tk.Entry(root, font=("Arial", 12), show="*")
        entry.pack(pady=5)

        entries[field["entry_var"]] = entry

    def password_visibility():
        if show_password_var.get():
            for entry in entries.values():
                entry.config(show="")
        else:
            for entry in entries.values():
                entry.config(show="*")

    # Checkbox for showing password
    show_password_var = tk.BooleanVar()
    show_password_checkbox = tk.Checkbutton(root, text="Show passwords", variable=show_password_var, font=("Arial", 12))
    show_password_checkbox.pack(pady=5)
    show_password_checkbox.config(command=password_visibility)

    error_or_success_label = tk.Label(root, text="", font=("Arial", 12), fg="red")
    error_or_success_label.pack(pady=5)
    root.error_or_success_label = error_or_success_label

    # Submit button
    submit_button = tk.Button(root, text="Confirm change", font=('Arial', 12),
                              command=lambda: confirm_password_change(hashlib.md5(entries["current_password"].get().encode()).hexdigest(),
                                                                      hashlib.md5(entries["new_password"].get().encode()).hexdigest(),
                                                                      hashlib.md5(entries["repeat_new_password"].get().encode()).hexdigest(),
                                                                      user_info,
                                                                      root))
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

    # Check if all fields are filled
    if not current_password or not new_password or not repeat_new_password:
        root.error_or_success_label.config(text="All fields must be filled!", fg="red")
        return

    # Check if the current password is correct
    if current_password != user_info['password']:  # This assumes user_info contains the current password
        root.error_or_success_label.config(text="Incorrect current password!", fg="red")
        return

    # Check if the passwords match
    if new_password != repeat_new_password:
        root.error_or_success_label.config(text="New passwords do not match!", fg="red")
        return

    # Check if the new password is not the same as the old password
    if new_password == current_password:
        root.error_or_success_label.config(text="New password cannot be the same as the old password!", fg="red")
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

# Main function to run the application
def create_home_page(doctor_info, root=None):
    if root is None:
        root = tk.Tk()

    # Clear the root window for reloading the home page
    for widget in root.winfo_children():
        widget.destroy()

    # Set window title and geometry
    root.title("Home")
    set_geometry(root)

    # Welcome text for the doctor
    last_name = doctor_info.get('last_name', '').strip()
    if last_name:
        welcome_text = f"Hello Dr. {last_name},\n welcome to your personal Psybridge page."
    else:
        welcome_text = "Hello doctor,\n welcome to your personal Psybridge page."

    if doctor_info.get('upcoming_meeting'):
        # Get the appointment date
        upcoming_date = datetime.strptime(doctor_info['upcoming_meeting'][0], '%Y-%m-%d')
        formatted_date = upcoming_date.strftime('%d %B %Y')
        patient_name = f"{doctor_info['upcoming_meeting'][1]} {doctor_info['upcoming_meeting'][2]}"
        # Update welcome text with appointment details
        welcome_text += (f"\n \n Your next appointment is on {formatted_date},\n"
                         f"with patient {patient_name}.")

    # Display welcome message, centered
    label_welcome = tk.Label(
        root,
        text=welcome_text,
        font=("Arial", 12),
        wraplength=600,
        justify="center"
    )
    label_welcome.pack(pady=20)

    # Left frame for buttons
    frame_left = tk.Frame(root)
    frame_left.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.BOTH, expand=True)

    # Buttons for patient list, questionnaires and schedule
    buttons_left = [
        ("Patients", lambda: patient_list(doctor_info, root)),
        ("Questionnaires", lambda: questionnaire_list(doctor_info, root)),
        ("Schedule appointment", lambda: ss.main(doctor_info, root, "doctor")),  # Proper tuple with command
    ]
    for text, command in buttons_left:
        tk.Button(frame_left, text=text, bg="red", fg="white", width=20, height=2, command=command).pack(pady=10, fill=tk.X)

    # Right frame for doctor's personal information
    frame_right = tk.Frame(root, bg="lightgrey")
    frame_right.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.BOTH, expand=True)

    label_personal_info = tk.Label(frame_right, text="Personal information:", font=("Arial", 12), bg="lightgrey")
    label_personal_info.pack(anchor="nw", padx=10, pady=5)

    # Define labels and corresponding doctor info keys
    personal_info = [
        ("Name:", f"{doctor_info.get('first_name', '')} {doctor_info.get('last_name', '')}"),
        ("Username:", doctor_info.get('user_name', '')),
        ("Date of birth:", doctor_info.get('date_of_birth', '')),
        ("Phone number:", doctor_info.get('phone_number', '')),
        ("Address:", doctor_info.get('address', '')),
    ]

    # Create labels dynamically
    for text, value in personal_info:
        tk.Label(frame_right, text=f"{text} {value}", font=("Arial", 10), bg="lightgrey", wraplength=450).pack(
            anchor="nw", padx=10, pady=5
        )

    # Buttons for change info and change password
    buttons_right = [
        ("Change personal information", lambda: change_personal_information(doctor_info, root)),
        ("Change password", lambda: change_password(doctor_info, root))
    ]
    for text, command in buttons_right:
        tk.Button(frame_right, text=text, bg="red", fg="white", width=25, height=1, command=command).pack(anchor = "s", pady=5, padx=10)

    root.mainloop()

def main(user_id):
    create_home_page(get_doctor_info(user_id))

if __name__ == "__main__":
    user_id = 51 # Example doctor user ID
    create_home_page(get_doctor_info(user_id))
