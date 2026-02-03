"""
Authors:
- Jixuan Yao: Initialize database, login, sending verification email, verify email, limit the type and size of uploaded files.
- Marit Paul: Signup, select registration role, reset password.
- David Xu: Upload file for doctor registration, store files in the database.

About this Python file:
This file contains the login interface for the project. It starts by connecting to the project database.
The login interface includes features such as 'login', 'register', and 'reset password'.
All related functionalities are implemented in this file.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import os
import requests
import random as rd
import patient_interface as pi
import admin_system as ad
import doctor_interface as do
import shutil
import hashlib

# the following codes have error on jixuan's computer:
# try:
#     if home:
#         pass
# except:
#     home = tk.Tk() # home page(first window)
# for widget in home.winfo_children():
#     widget.destroy()

home = tk.Tk()
home.title("Welcome to Psybridge")
window_width = 450  # size of window
window_height = 300
screen_width = home.winfo_screenwidth()  # get the width of screen
screen_height = home.winfo_screenheight()  # get the height of screen
x = (screen_width // 2) - (window_width // 2)  # Calculate x-coordinate to center the window
y = (screen_height // 2) - (window_height // 2)  # Calculate y-coordinate to center the window

# centering the window on the screen
home.geometry(f'{window_width}x{window_height}+{x}+{y}')

tk.Label(home, text="Username").place(x=97, y=150)
tk.Label(home, text="Password").place(x=99, y=190)

# entry field of username
# instantiate a string variable. username's type including string, int, combiation of string and int
var_name = tk.StringVar()

# entry is text input rectangular, here also connect it with home window
entry_name = tk.Entry(home, textvariable=var_name)
entry_name.place(x=160, y=150)

# entry field of password
# a variable for password
var_pwd = tk.StringVar()

# a input entry area for password
entry_pwd = tk.Entry(home, textvariable=var_pwd)
entry_pwd.place(x=160, y=190)


def init_db(database = 'Database.db', unverified_data= 'register_doctor.db' ):
    """
    Connect to two specified SQLite databases.

    If either database file does not exist, a `FileNotFoundError` is raised.
    This function does not create new database files but ensures the `doctors` table
    exists in the `unverified_data` database.

    Parameters:
    database(db): The database of the project containing all the user information. The default value is 'Database.db',
    the database we have created.
    unverified_data(db) :Contains a table named `doctors` for storing doctor registration application. The default
    value is 'register_doctor.db', the database we have created.

    """
    if not os.path.exists(database):
        raise FileNotFoundError(f"Database file '{database}' does not exist")
    if not os.path.exists(unverified_data):
        raise FileNotFoundError(f"Unverified data file '{unverified_data}' does not exist")

    conn1 = sqlite3.connect(unverified_data)
    cursor1 = conn1.cursor()

    # cursor1.execute('''DROP TABLE IF EXISTS doctors''') # this command is only for first run

    # Create register application table for doctor if not exists
    cursor1.execute('''CREATE TABLE IF NOT EXISTS doctors (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        email TEXT NOT NULL,
        filename TEXT,
        certificate_file BLOB
    )''')

    conn1.commit()
    conn1.close()

    conn2 = sqlite3.connect(database)
    conn2.commit()
    conn2.close()

def user_login(username=None, password=None):
    """
    Open the login window and handle user login data by comparing the input data with the database.

    This function retrieves the username and password entered by the user, connects to a SQLite database to check
    if the username exists, and compares the entered password with the stored password. If the password matches,
    a welcome message is displayed.And the Interface of different user role will shows up by calling the function
    open_interface. If the password is incorrect, an error window is opened with options to re-enter the password
    or quit. If the username or password fields are empty, an error message is displayed. If the username is not
    in the database, a prompt is shown offering the option to register.
    """
    user_name = username if username is not None else var_name.get()
    # user_pwd = password if password is not None else var_pwd.get()

    #The password entered by the user. An integer type of variable is also allowed, which will be automatically
    # converted to a string.
    user_pwd = hashlib.md5(var_pwd.get().encode()).hexdigest()


    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT password,User_id FROM users WHERE User_name = ?', (user_name,))
    result = cursor.fetchone()

    if result:
        stored_password, user_id = result
        if user_pwd == stored_password:
            tk.messagebox.showinfo(title='Welcome', message='Welcome, ' + user_name + "\U0001F603")
            open_interface(user_id)
            return "success"
        else:
            tk.messagebox.showerror(message='Incorrect Password ☹')
            return "error"
    elif user_name == "" or user_pwd == "":
        tk.messagebox.showerror(message='empty username or password ☹')
        return "error"
    else:
        go_signup = tk.messagebox.askyesno('Welcome', 'You have not registered yet. Would you like to register now?😊')
        if go_signup:
            open_role_selection()
        else:
            return

def open_interface(user_id):
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM Patients WHERE User_id = ?', (user_id,))
    is_patient = cursor.fetchone()

    cursor.execute('SELECT 1 FROM Admins WHERE User_id = ?', (user_id,))
    is_admin = cursor.fetchone()

    cursor.execute('SELECT 1 FROM Doctors WHERE User_id = ?', (user_id,))
    is_doctor = cursor.fetchone()

    if is_patient:
     # the user who log in is patient
        pi.main(user_id, home)

    elif is_admin:
        ad.main(home)
        home.destroy()

    elif is_doctor:
        do.main(user_id)
        home.destroy()

# The hided codes below is login function with frequent iteraction with the GUI
# def user_login():
#     """
#     Open the login window and handle user login data by comparing the input data with the database.
#
#     This function retrieves the username and password entered by the user, connects to a SQLite database to check
#     if the username exists, and compares the entered password with the stored password. If the password matches,
#     a welcome message is displayed.And the Interface of different user type(patient , doctor or admin) will shows up.
#      If the password is incorrect, an error window is opened with options to
#     re-enter the password or quit (close all windows). If the username or password fields are empty, an error
#     message is displayed. If the username is not in the database, a prompt is shown offering the option to register.
#     """
#
#     # get user name and password from the input area:
#     # The username entered by the user. An integer type of variable is also allowed, which will be automatically
#     # converted to a string.
#     user_name = var_name.get()
#     user_pwd = var_pwd.get()
#
#     conn = sqlite3.connect('Database.db')
#     cursor = conn.cursor()
#
#     cursor.execute('SELECT password,User_id FROM users WHERE User_name = ?', (user_name,))
#     result = cursor.fetchone()
#
#     # check if we have this username on database
#     if result:
#         print("result",result)
#         stored_password, user_id = result
#         if user_pwd == stored_password:
#             tk.messagebox.showinfo(title='Welcome', message='Welcome, ' + user_name + "\U0001F603")
#             cursor.execute('SELECT 1 FROM Patients WHERE User_id = ?', (user_id,))
#             is_patient = cursor.fetchone()
#
#             cursor.execute('SELECT 1 FROM Admins WHERE User_id = ?', (user_id,))
#             is_admin = cursor.fetchone()
#
#             cursor.execute('SELECT 1 FROM Doctors WHERE User_id = ?', (user_id,))
#             is_doctor = cursor.fetchone()
#
#             if is_patient:
#                 # the user who log in is patient
#                 pi.main(user_id, home)
#
#             elif is_admin:
#                 ad.main()
#                 home.destroy()
#
#             elif is_doctor:
#                 do.main(user_id)
#                 home.destroy()
#
#         else:
#             # tk.messagebox.showerror(message = 'Incorrect Password :(')
#             incorrect_psw = tk.Toplevel()
#             incorrect_psw.title("Welcome to Psybridge")
#             incorrect_psw.geometry(f'{window_width}x{window_height}+{x}+{y}')
#             temporary = tk.Label(incorrect_psw, text="Incorrect Password \u2639", font=("Helvetica", 12))
#             temporary.pack(expand=True)
#             bt_reenter = tk.Button(incorrect_psw, text='Re-enter Password', command=lambda: re_enter(incorrect_psw))
#             bt_reenter.place(x=125, y=200)
#             bt_tem_back = tk.Button(incorrect_psw, text="Quit", command=home.quit)
#             bt_tem_back.place(x=275, y=200)
#
#     elif user_name == "" or user_pwd == "":
#         tk.messagebox.showerror(message='empty username or password \u2639')
#
#     # if the user not in database, prompt to register
#     else:
#         # select yes or no
#         go_signup = tk.messagebox.askyesno('Welcome',
#                                            'You have not registered yet. Would you like to register now?\U0001F603')  # Welcome is title
#         if go_signup:
#             open_role_selection()
#
#     def re_enter(incorrect_psw):
#         incorrect_psw.destroy()  # Close the incorrect password window
#         var_pwd.set('')  # Clear the password entry field
#         entry_pwd.focus()  # Set focus to the password entry field


def usr_sign_up():
    '''
    Open an registeration window and store the input data of user

    This function allow user to register by choosing their role (Patient or Doctor), and input information includes
     username,password and email. Password will be input twice to match and email need verification by sending them
     a verification code.If all  things are correctly entered, then the register information will stored into the
     database. For the registeration of patient, we store it to the Database.db which is the official
     databse of our program. And for registeration of doctor, we need the user to upload the certificate of the doctor
     and then store the information on registeration_application.db, which will be reviewd by the admin of our program
     later. As long as the doctor registeration approved by the admin, we store the doctor data into the Datase.db

    '''

    # Function for confirming registration
    def handle_signup():
        # Get the content from the input fields

        # np = hashlib.md5(new_pwd.get().encode()).hexdigest()
        # npf = hashlib.md5(new_pwd_confirm.get().encode()).hexdigest()

        nn = new_name.get()
        # np = new_pwd.get()

        np = hashlib.md5(new_pwd.get().encode()).hexdigest()
        npf = hashlib.md5(new_pwd_confirm.get().encode()).hexdigest()


        # npf = new_pwd_confirm.get()
        email = new_email.get()

        conn = sqlite3.connect('Database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE User_name = ?', (nn,))
        if cursor.fetchone():
            tk.messagebox.showerror('Error', 'Username already exists')
            window_sign_up.lift()

        elif np == '' or nn == '' or email == '':
            tk.messagebox.showerror('Error', 'Username, password or email is empty')
            window_sign_up.lift()

        elif np != npf:
            tk.messagebox.showerror('Error', 'Passwords do not match')
            window_sign_up.lift()
        else:
            # new
            # Different actions based on the role
            if chosen_role == 'Patient':
                if verify_email(email):
                    messagebox.showinfo('Welcome', 'Registration successful')
                    # Add new user data to database with role
                    cursor.execute('INSERT INTO users (User_name, Password, Email) VALUES (?, ?, ?)', (nn, np, email))
                    user_id = cursor.lastrowid  # get the user_id

                    cursor.execute('INSERT INTO patients (User_id) VALUES (?)', (user_id,))
                    conn.commit()
                    window_sign_up.destroy()
                # else: tk.messagebox.showerror('Error', 'Please go back and retry')
            else:
                # Frame 9 for doctor/admin (not implemented)
                if verify_email(email):
                    messagebox.showinfo('Welcome', 'Email is verified successfully')
                    # Add new user data to database with role
                    conn.commit()
                    window_sign_up.destroy()
                    upload_file_window(nn, np, email)

            window_sign_up.destroy()

        conn.close()

    # Create a new registration window
    window_sign_up = tk.Toplevel()
    window_sign_up.geometry(f'{window_width}x{window_height}+{x}+{y}')
    window_sign_up.title('Register')

    # Username label and entry field
    new_name = tk.StringVar()
    tk.Label(window_sign_up, text='Username:').place(x=10, y=10)
    tk.Entry(window_sign_up, textvariable=new_name).place(x=150, y=10)

    # Email label and entry field
    new_email = tk.StringVar()
    tk.Label(window_sign_up, text='Email:').place(x=10, y=40)
    tk.Entry(window_sign_up, textvariable=new_email).place(x=150, y=40)

    # Password label and entry field
    new_pwd = tk.StringVar()
    tk.Label(window_sign_up, text='Enter password:').place(x=10, y=70)
    tk.Entry(window_sign_up, textvariable=new_pwd, show='*').place(x=150, y=70)

    # Confirm password label and entry field
    new_pwd_confirm = tk.StringVar()
    tk.Label(window_sign_up, text='Re-enter password:').place(x=10, y=100)
    tk.Entry(window_sign_up, textvariable=new_pwd_confirm, show='*').place(x=150, y=100)

    # Confirm registration button
    bt_confirm_sign_up = tk.Button(window_sign_up, text='Confirm registration', command=handle_signup)
    bt_confirm_sign_up.place(x=150, y=150)


# new
def open_role_selection():
    """
    Open a window for user to select the role they want to register.

    User can choose the role as "patient" or "doctor". And user can also cancel the selection. After user choosing role,
    sign_up function will be called.
    """
    role_window = tk.Toplevel()
    role_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
    role_window.title('Choose Role')

    tk.Label(role_window, text='Choose Role:').place(x=20, y=20)

    def select_role(role):
        global chosen_role
        chosen_role = role
        role_window.destroy()  # Close the role selection window
        usr_sign_up()  # Go to sign up for all roles

    tk.Button(role_window, text='Patient Version', command=lambda: select_role('Patient')).place(x=200, y=20)
    tk.Button(role_window, text='Doctor Version', command=lambda: select_role('Doctor')).place(x=200, y=70)
    tk.Button(role_window, text='Cancel', command=role_window.destroy).place(x=220, y=170)


# new
def open_blank_page(role):
    """
    This function opens a blank window for the role user chose to register and set the window title accordingly.

    Parameters:
    role (str): The user role for which the dashboard is being opened ("Patient" or "Doctor").
    """
    # Create a blank window for the selected role (Doctor/Admin)
    blank_window = tk.Toplevel()
    blank_window.title(f"{role} Dashboard")
    blank_window.geometry(f'{window_width}x{window_height}+{x}+{y}')


def open_forgot_password_window():
    """
    This function opens a window to reset the user's password.

    This function opens a window to reset the user's password. To reset the password the user need to input their
    username, new password, and email to verify. If the username exists in the database, the email is verified,
    and the new password is different from the previous one, the new password is updated.
    If the user does not exist, an option to register is provided.
    """
    re_set = tk.Toplevel(home)
    re_set.title("Reset Password")
    re_set.geometry(f'{window_width}x{window_height}+{x}+{y}')

    tk.Label(re_set, text="Username").place(x=97, y=100)
    tk.Label(re_set, text="New Password").place(x=50, y=150)
    tk.Label(re_set, text="Email").place(x=97, y=190)

    # entry field of username
    re_set_name_var = tk.StringVar()
    re_set_name_entry = tk.Entry(re_set, textvariable=re_set_name_var)
    re_set_name_entry.place(x=160, y=100)


    # entry field for password
    re_set_pwd_var = tk.StringVar()  # StringVar for password
    re_set_pwd_entry = tk.Entry(re_set, textvariable=re_set_pwd_var, show='*')  # show='*' hides password input
    re_set_pwd_entry.place(x=160, y=150)

    # entry field for email
    re_email_var = tk.StringVar()
    re_email_entry = tk.Entry(re_set, textvariable=re_email_var)
    re_email_entry.place(x=160, y=190)

    # Function to handle password reset
    def reset_password():
        re_name = re_set_name_var.get()
        re_pwd = hashlib.md5(re_set_pwd_var.get().encode()).hexdigest()
        email = re_email_var.get()

        # Retrieve user data from local file, if file not exists create one and write an admin info in it
        conn = sqlite3.connect('Database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE User_name = ?", (re_name,))
        user_info = cursor.fetchone()

        # Check if username exists in users_info
        if user_info:   #if the user name exists in the database
            if verify_email(email):  #if the email is verified successfully
                if re_pwd == user_info[1]:
                    tk.messagebox.showinfo(title='Reset Password',
                                           message='New password cannot be the same as previous one.')

                    # Ensure the reset window is always on top
                    re_set.lift()
                    re_set.focus_force()  # Optional: bring the window to the front and focus
                else:
                    # Update password
                    cursor.execute("UPDATE users SET Password = ? WHERE User_name = ?", (re_pwd, re_name))
                    conn.commit()  # Commit the changes
                    tk.messagebox.showinfo(title='Reset Password',
                                           message="Your new password has been successfully set!")
                    re_set.destroy()

        elif re_name == "" or re_pwd == "": # there is no input values
            tk.messagebox.showerror(title="Error", message='Username or password cannot be empty.')
            # Ensure the reset window is always on top
            re_set.lift()
            re_set.focus_force()  # Optional: bring the window to the front and focus

        else:
            # If the user does not exist, prompt to register
            go_signup = tk.messagebox.askyesno('Register',
                                               'You have not registered yet. Would you like to register now?')
            if go_signup:
                usr_sign_up()  # Call the function to sign up the user
                re_set.destroy()
            # new
            else:
                # Ensure the reset window is always on top
                re_set.lift()
                re_set.focus_force()  # Optional: bring the window to the front and focus

    bt_Confirm = tk.Button(re_set, text='Confirm', command=reset_password)
    bt_Confirm.place(x=40, y=230)

    bt_Cancel = tk.Button(re_set, text='Cancel', command=re_set.destroy)
    bt_Cancel.place(x=120, y=230)

def is_allowed_type(file_path):
    """
    Check if the file uploaded is of the type we allowed

    Parameters:
    file_path (str): The path to the file to check.

    Returns:
    bool: True if the file type is allowed (PDF, PNG, JPG), False otherwise.
    """
    allowed_type = {'.pdf', '.png', '.jpg'}
    return os.path.splitext(file_path)[1].lower() in allowed_type


def is_allowed_size(file_path):
    """
    Check if the file uploaded is of the size we allowed

    Parameters:
    file_path (str): The path to the file to check.

    Returns:
    bool: True if the file size is allowed (less or equal to 6MB), False otherwise.
    """
    size = os.path.getsize(file_path)
    print(size)
    max_size = 6 * 1024 * 1024  # byte of 6MB
    return size <= max_size


def handle_file_upload(file_path, nn, np, email):
    """
    Validates the selected file type and size, then uploads it to the database if valid.

    Checks if a file has been selected, verifies its type and size, and if it meets
    the requirements, calls insert_file to save it in the database. If any validation
    fails, an appropriate error message is displayed.

    Parameters:
    file_path (str): Path of the uploaded file.
    nn (str): Username of the user.
    np (str): Password of the user.
    email (str): Email of the user.

    Returns:
    str: Success or error message.
    """
    try:
        # Step 1: Validate file type
        if not is_allowed_type(file_path):
            return "Invalid file type. Please upload a PDF, PNG, or JPG."

        # Step 2: Validate file size
        if not is_allowed_size(file_path):
            return "File size exceeds 6MB. Please upload a smaller file."

        # Step 3: Prepare to store the file
        folder_path = "certificates"
        os.makedirs(folder_path, exist_ok=True)  # Ensure the folder exists
        destination_path = os.path.join(folder_path, os.path.basename(file_path))

        # Step 4: Check if username already exists
        conn = sqlite3.connect('register_doctor.db')
        c = conn.cursor()
        c.execute("SELECT * FROM doctors WHERE username = ?", (nn,))
        existing_user = c.fetchone()
        if existing_user:
            conn.close()
            return f"Username '{nn}' is already registered. Please choose a different username."

        # Step 5: Copy the file to the destination folder
        shutil.copyfile(file_path, destination_path)

        # Step 6: Insert user information into the database
        c.execute(
            "INSERT INTO doctors (username, password, email, filename, certificate_file) VALUES (?, ?, ?, ?, ?)",
            (nn, np, email, os.path.basename(file_path), destination_path),
        )
        conn.commit()
        conn.close()

        # Return success message
        return "File uploaded successfully. We'll review it and contact you shortly!"
    except Exception as e:
        # Log the error and return a user-friendly error message
        return f"Error uploading file: {str(e)}"


# front-end of upload file window
def upload_file_window(nn, np, email):
    """
    Opens a window to upload a professional certificate file for doctor registeration.

    This function opens a window interface for users to upload a file (limited to PDF, PNG, and JPG formats with
    a maximum size of 6MB) of  professional certificate as a doctor. The file user uploaded will be stored in
    doctor_registeration database. And will be viewd by admin of our program. There are several inner functions
    to realize the function of uploading and saving file.

    Parameters:
    nn (str): Username of the registeration
    np (str): Password of the registeration
    email (str): Email of the registeration
    """
    def upload_file():
        """
        Handle the upload action .
        """
        if not file_path:
            messagebox.showwarning("Error", "No file selected. Please select a file first.")
            return
        result_message = handle_file_upload(file_path, nn, np, email)
        if result_message.startswith("Error"):
            messagebox.showerror("Error", result_message)
        else:
            messagebox.showinfo("Success", result_message)
            upload_window.destroy()

    def select_file():
        """
        Open a file dialog for the user to select a file.

        Sets the nonglobal variable 'file_path' to the selected file's path.
        """
        nonlocal file_path
        file_path = filedialog.askopenfilename()
        file_label.config(text=f"Selected: {file_path}" if file_path else "No file selected")

    file_path = None
    upload_window = tk.Toplevel()
    upload_window.geometry("400x300")

    tk.Label(upload_window, text="Please upload your Professional Qualification Certificate").pack(pady=10)
    file_label = tk.Label(upload_window, text="No file selected")
    file_label.pack(pady=5)

    tk.Button(upload_window, text="Select File", command=select_file).pack(pady=5)
    tk.Button(upload_window, text="Upload File", command=upload_file).pack(pady=5)
    tk.Button(upload_window, text="Cancel", command=upload_window.destroy).pack(pady=5)


# below are old version of function upload_file_widow, which merged front end and back end
#
# def uploadFileWindow(nn, np, email):
#     # Function to insert file into the database
#     """
#         Opens a window to upload a professional certificate file for doctor registeration.
#
#         This function opens a window interface for users to upload a file (limited to PDF, PNG, and JPG formats with
#         a maximum size of 6MB) of  professional certificate as a doctor. The file user uploaded will be stored in
#         doctor_registeration database. And will be viewd by admin of our program. There are several inner functions
#         to realize the function of uploading and saving file.
#
#         Parameters:
#         nn (str): The username of the user.
#         np (str): The password of the user.
#         email (str): The email of the user.
#
#         Returns:
#         None
#         """
#     def insert_file(file_path):
#         """
#         Inserts the selected file into the 'doctors' table in the register_doctor.db.
#
#         Parameters:
#         file_path:The path to the selected file to insert.
#         """
#         try:
#             conn = sqlite3.connect('register_doctor.db')
#             c = conn.cursor()
#             # Read file as binary
#             with open(file_path, 'rb') as f:
#                 file_data = f.read()
#             # Insert file into the database
#             c.execute(
#                 "INSERT INTO doctors (username, password, email, filename, certificate_file) VALUES (?, ?, ?, ?, ?)",
#                 (nn, np, email, os.path.basename(file_path), file_data))
#             conn.commit()
#             conn.close()
#             messagebox.showinfo("Success",
#                                 "File uploaded and saved successfully, we'll review it and contact you shortly!")
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to save the file: {str(e)}")
#
#     # Function to open file dialog and select a file
#     def select_file():
#         """
#         Opens a file dialog for the user to select a file and displays the file path.
#
#         Sets the global variable 'file_path' to the selected file's path.
#         """
#         global file_path
#         file_path = filedialog.askopenfilename()
#         if file_path:
#             file_label.config(text=f"Selected: {file_path}")
#         uploadFile.lift()
#         uploadFile.focus_force()  # Optional: bring the window to the front and focu
#
#     # Function to handle the upload when the accept button is clicked
#     def upload_file():
#         """
#         Validates the selected file type and size, then uploads it to the database if valid.
#
#         Checks if a file has been selected, verifies its type and size, and if it meets
#         the requirements, calls insert_file to save it in the database. If any validation
#         fails, an appropriate error message is displayed.
#         """
#         if file_path:
#             if is_allowed_type(file_path):
#                 if is_allowed_size(file_path):
#                     insert_file(file_path)
#                     uploadFile.destroy()
#                 else:
#                     messagebox.showwarning("Error", "please select file less or equal than 6MB.")
#                     uploadFile.lift()  # keep the page uoloadfile
#             else:
#                 messagebox.showwarning("Error", "please select file of type pdf,png,jpg.")
#                 uploadFile.lift()  # keep the page uoloadfile
#
#         else:
#             messagebox.showwarning("No file", "Please select a file first.")
#             uploadFile.lift()  # keep the page uoloadfile
#
#     uploadFile = tk.Toplevel(home)
#     uploadFile.geometry(f'{window_width}x{window_height}+{x}+{y}')
#
#     guide_label = tk.Label(uploadFile, text="Please upload your Professional "
#                                             "Qualification Certificate. \n Only PDF, JPG,"
#                                             " and PNG files with a maximum size of \n 10MB "
#                                             "are permitted", width=50, anchor="w")
#     guide_label.pack(pady=10)
#
#     # File path label
#     file_label = tk.Label(uploadFile, text="No file selected", width=50, anchor="w")
#     file_label.pack(pady=10)
#
#     # Select file button
#     select_button = tk.Button(uploadFile, text="Select File", command=select_file)
#     select_button.pack(pady=5)
#
#     # Accept button
#     accept_button = tk.Button(uploadFile, text="Upload File", command=upload_file)
#     accept_button.pack(pady=5)
#
#     # Cancel button
#     cancel_button = tk.Button(uploadFile, text="Cancel", command=uploadFile.destroy)
#     cancel_button.pack(pady=5)

# the API response time is nearly 40 seconds
def send_mail(tomail):
    """
    Sends an email to verify if the email user input is valid.

    This function calls an external API to send an email with a random verification code of HTML content. The email is
    sent by a predefined email account with specific SMTP seetings. The function returns the code for further purpose
    in function "verify_email".

    Parameters:
    tomail (str): The recipient's email address.

    Returns:
    int: The verification code sent to the user if the email is sent successfully; otherwise, None.
    """
    url = "https://luckycola.com.cn/tools/customMail"  # API
    code = rd.randint(300, 500)

    content = f"""
    #         <div>
    #             <p>Hi! Your verification code is:</p>
    #             <h2 style='color: blue;'>{code}</h2>
    #             <p>Please enter this code in the entry to verify your email.</p>
    #         </div>
    #         """

    payload = {
        "ColaKey": "YPbPlz5Y6sEaBK17351383491572TLywtbhMx",
        "tomail": tomail,
        "fromTitle": "Email Confirmation",
        "subject": "Your Verification Code",
        "smtpCode": "spfzmtiuplticbbh",
        "smtpEmail": "407555902@qq.com",
        "smtpCodeType": "qq",
        "isTextContent": False,
        "content": content
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print("Email sent successfully!")
        return code
    except requests.exceptions.Timeout:
        print("Request timed out, but the email might still be sent.")
        return code
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


#
def verify_email(email):
    """
    Send the verification code and prompt the user to enter the verification code to verify the email address.

    This function send the verification email by calling the function "send_email" and verifies if the user input
     verification code is same as what we send. Two inner functions are used to check.If the email is sent successfully,
     a window prompts the user to enter the verification code. If the entered code matches the sent code, the email
     is verified successfully, and a confirmation message is shown. The function returns `True` if verification is
     successful; otherwise, it returns `False`.

    Parameters:
    email (str): The email address to which the verification code will be sent.

    Returns:
    bool: True if the email is successfully verified, False otherwise.
    """
    code = send_mail(email)
    temporary = False
    if code:
        tk.messagebox.showinfo('Email Sent', 'A verification code has been sent to your email address.')
        verify_window = tk.Toplevel()
        verify_window.lift()
        print(code)
        verify_window.title("Email Verification")
        verify_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        tk.Label(verify_window, text="Enter Verification Code:").pack(pady=10)
        code_entry = tk.Entry(verify_window)
        code_entry.pack(pady=5)

        # tk.messagebox.showinfo('Email Sent', 'A verification code has been sent to your email address.')

        def check_code():
            nonlocal temporary  # intermiediate value which will be return
            input_code = code_entry.get()
            if input_code == str(code):
                messagebox.showinfo('Success', 'Email verified successfully!')
                verify_window.destroy()
                temporary = True
                return True
            else:
                messagebox.showerror('Error', 'Incorrect verification code or Invalid email address. ')
                verify_window.lift()

        tk.Button(verify_window, text="Verify", command=check_code).pack(pady=10)
        verify_window.wait_window()
    return temporary


bt_register = tk.Button(home, text='Register', command=open_role_selection)
bt_register.place(x=40, y=230)
bt_login = tk.Button(home, text='Login', command=user_login)
bt_login.place(x=110, y=230)
bt_quit = tk.Button(home, text="Quit", command=home.quit)
bt_quit.place(x=170, y=230)

bt_forget_psw = tk.Button(home, text="Forgot Your Password?", command=open_forgot_password_window)
bt_forget_psw.place(x=220, y=230)


def main():
    init_db('Database.db', 'register_doctor.db')


    home.mainloop()


if __name__ == "__main__":
    main()