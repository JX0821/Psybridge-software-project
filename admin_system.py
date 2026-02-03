"""
Authors:
- Jixuan Yao: functions of adding administrator, deleting administrator.
- David Xu Hu: The rest

About this Python file:
This file contains the admin system for the project. The interface is first initialized, and the UI elements are added.
All the functionalities are tied to those UI elements, included in the code below.
"""


import tkinter as tk
import sqlite3
from tkinter import messagebox
from tkPDFViewer2 import tkPDFViewer as pdf

headers = ["", "User ID", "Username", "Password", "Email", "Name", "Surname", "Date of Birth",
                "Phone Number", "Address"]
widths = [5, 5, 15, 15, 10, 10, 10, 10, 10, 40]

unverified_doctors = dict()

def get_window_offset(root, width, height):
    """
    This function calculates the position to center a new window on the screen
    relative to the given root window, with a size of the width and height parameters

    Parameters:
    root (tkinter.Tk): Optional instance of tkinter frame
    width (int): The width of the new window to be centered
    height (int): The height of the new window to be centered

    Returns:
    tuple: A tuple containing the x and y offset to center the window
    """
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    return x, y

def init_main_root(root=None):
    """
    This function optionally takes an instance of a tkinter frame and creates
    the administrator window, overriding the previous window (in case root is passed) or
    creating it inside

    Parameters:
    root (tkinter.Tk): Optional instance of tkinter frame
    """
    if root is None:
        root = tk.Tk()

    # Clear the root window for reloading the main page
    for widget in root.winfo_children():
        widget.destroy()
    root.title("PsyBridge - Administrator Interface")
    root.geometry("600x400")
    # Centers the window
    x, y = get_window_offset(root, 450, 300)
    root.geometry(f'{1220}x{600}+{x - 385}+{y - 150}')
    root.resizable(False, False)

    return root

def create_main_window(root=None, run_loop=True):
    """
    This function optionally takes an instance of a tkinter frame and creates the
    administrator interface, calling all relevant functions to create the window, add all the buttons,
    frames

    Parameters:
    root (tkinter.Tk): Optional instance of tkinter frame
    """
    root = init_main_root(root)

    # Database connection and initial data fetch
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    user_info = cursor.fetchall()

    def init_scrollbar():
        """
        This function adds a vertical and horizontal scrollbar to the canvas containing the data
        """
        # Create the vertical scrollbar
        vsb = tk.Scrollbar(root, orient="vertical", command=c.yview)
        c.configure(yscrollcommand=vsb.set)

        # Create the horizontal scrollbar
        hsb = tk.Scrollbar(root, orient="horizontal", command=c.xview)
        hsb.pack(side="bottom", fill="x")
        c.configure(xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        c.pack(side="top", fill="both", expand=True, pady=20)
        c.create_window((4, 4), window=data_frame, anchor="nw")

        # Bind the configure event for the frame inside the canvas
        data_frame.bind("<Configure>", lambda event, canvas=c: on_frame_configure(canvas))

        def on_frame_configure(canvas):
            # Reset the scroll region to encompass the inner frame
            canvas.configure(scrollregion=canvas.bbox("all"))

    # Canvas that contains the data frame and the scrollbar
    c = tk.Canvas(root, borderwidth=0, background="#f9f9f9")
    # Frame that contains the data
    data_frame = tk.Frame(c, background="#f9f9f9")
    # Second canvas that contains everything else
    c2 = tk.Canvas(root, borderwidth=0, background="white")
    c2.pack(side="bottom", fill="both", expand=True)

    init_scrollbar()
    get_unapproved_doctors(unverified_doctors, cursor)
    insert_data(user_info, data_frame, root, unverified_doctors)

    def init_ui():
        # Frame for the searchbar and filter options
        search_frame = tk.LabelFrame(c2, text="Search Bar and Show Options", bg="#f5dfad")
        search_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        # Frame for the searchbar
        search_bar_frame = tk.Frame(search_frame, bg="#f5dfad")
        search_bar_frame.pack(side="left", fill="both", expand=True)
        search_by_type_frame = tk.Frame(search_frame, relief=tk.SUNKEN, borderwidth=1, bg="#f5dfad")
        search_by_type_frame.pack(side="left", fill="both", expand=True)

        # Frames that contain the filter options
        upper_search_frame = tk.Frame(search_by_type_frame, relief=tk.SUNKEN, borderwidth=1, bg="#f0edd0")
        lower_search_frame = tk.Frame(search_by_type_frame, relief=tk.SUNKEN, borderwidth=1, bg="#edd1ad")
        upper_search_frame.pack(side="top", fill="both", expand=True)
        lower_search_frame.pack(side="top", fill="both", expand=True)

        # Frame for the user management buttons
        management_frame = tk.LabelFrame(c2, text="User Management", bg="#f5dfad")
        management_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        # Management buttons
        add_button = tk.Button(management_frame, text="Add Admin", command=lambda: add_admin(root, conn))
        delete_button = tk.Button(management_frame, text="Delete User",
                                  command=lambda: delete_user(input_entry.get(), root, conn))
        add_button.pack(side="left", expand=True)
        delete_button.pack(side="left", padx=10, pady=5)

        # Search bar
        search_string = tk.StringVar()
        search_bar = tk.Entry(search_bar_frame, textvariable=search_string)
        search_bar.pack(expand=True)  # Expand to fill the space inside the LabelFrame
        search_bar.bind("<KeyRelease>", lambda event: update_table(search_bar.get(), data_frame, root, cursor))

        # Filter buttons
        show_all_button = tk.Button(upper_search_frame, text="Show All Users",
                                    command=lambda: update_table(search_string.get(), data_frame, root, cursor))
        show_all_button.pack(side="left", expand=True)
        show_patients_button = tk.Button(upper_search_frame, text="Show Patients",
                                         command=lambda: update_table(search_string.get(), data_frame, root, cursor,
                                                                      "patients"))
        show_patients_button.pack(side="left", expand=True)
        show_doctors_button = tk.Button(upper_search_frame, text="Show Doctors",
                                        command=lambda: update_table(search_string.get(), data_frame, root, cursor,
                                                                     "doctors"))
        show_doctors_button.pack(side="left", expand=True)
        show_admins_button = tk.Button(upper_search_frame, text="Show Admins",
                                       command=lambda: update_table(search_string.get(), data_frame, root, cursor,
                                                                    "admins"))
        show_admins_button.pack(side="left", expand=True)
        show_unverified_button = tk.Button(lower_search_frame, text="Show Unverified Doctors",
                                           command=lambda: update_table(search_string.get(), data_frame, root, cursor,
                                                                        "unverified"))
        show_unverified_button.pack(side="left", expand=True)

        # Input frame placed below the Delete User button
        input_frame = tk.Frame(management_frame)
        input_frame.pack(side="top", fill="x", pady=10)  # Pack input frame below the button

        # Input label
        input_label = tk.Label(input_frame, text="Input User ID", font=("Arial", 12))
        input_label.pack(side="left", padx=5)  # Label positioned on the left

        input_var = tk.StringVar()
        input_entry = tk.Entry(input_frame, textvariable=input_var, font=("Arial", 12), width=30)
        input_entry.pack(side="left", padx=5)

    init_ui()
    if run_loop:
        root.mainloop()
        conn.close()
    else:
        conn.close()

def update_table(search, data_frame, root, cursor, user_type="users"):
    """
    This function updates the table based on what was written on the search bar, and whether any of the filter buttons
    was pressed.

    Parameters:
    root (tkinter.Tk): The root window to update the data
    data_frame (tkinter.Frame): Tkinter frame that contains all the user data
    search (str): String of whatever was written on the search bar
    user_type (str): Updates the table with the user type defined by this parameter, by default "users" to show all users
    """
    if user_type == "patients":
        query = """SELECT users.* FROM users, patients WHERE (users.User_id = patients.User_id) 
                AND (users.User_id LIKE ? OR User_name LIKE ? OR Address LIKE ?)
                 """
    elif user_type == "doctors":
        query = """SELECT users.* FROM users, doctors WHERE (users.User_id = doctors.User_id) 
                AND (users.User_id LIKE ? OR User_name LIKE ? OR Address LIKE ?)
                 """
    elif user_type == "admins":
        query = """SELECT users.* FROM users, admins WHERE (users.User_id = admins.User_id) 
                AND (users.User_id LIKE ? OR User_name LIKE ? OR Address LIKE ?)
                 """
    elif user_type == "unverified":
        query = """SELECT users.* FROM users, doctors WHERE (users.User_id = doctors.User_id)
                AND (doctors.verify_state = 0) AND (users.User_id LIKE ? OR User_name LIKE ? OR Address LIKE ?)"""
    else:
        query = f"""
                SELECT * FROM users
                WHERE User_id LIKE ? OR User_name LIKE ? OR Address LIKE ?;
                """

    cursor.execute(query, ('%' + search + '%', '%' + search + '%', '%' + search + '%'))
    user_info = cursor.fetchall()
    insert_data(user_info, data_frame, root, unverified_doctors)

def clear_frame(data_frame):
    """
    This function deletes all children off a given frame

    Parameters:
    data_frame (tkinter.Frame): Tkinter frame that contains all user data
    """
    for widget in data_frame.winfo_children():
        widget.destroy()

def insert_data(user_info, data_frame, root, doctors):
    """
    This function inserts the data passed as argument in the frame containing the data

    Parameters:
    root (tkinter.Tk): The root window to update the data
    data_frame (tkinter.Frame): Tkinter frame that contains all the user data
    user_info (list of tuples): A list of tuples where each tuple represents a row of user data
    doctors (dict): dictionary where unverified doctors are stored in
    """
    clear_frame(data_frame)

    if user_info:
        for col, header in enumerate(headers):
            tk.Label(data_frame, text=header, bg="#f0f0f0", font=("Arial", 12)).grid(row=0, column=col, pady=2)
        for col in range(len(headers)):
            data_frame.grid_columnconfigure(col, weight=1)

        total_rows = len(user_info)
        total_columns = len(user_info[0])
        for i in range(total_rows):
            if user_info[i][0] in doctors:
                data = doctors.get(user_info[i][0])
                b = tk.Button(data_frame, text="+", padx=5, command=lambda: certificate_validation(data, root))
                b.grid(row=i+1, column=0, sticky="ew")

            for j in range(total_columns):
                insert_entry(data_frame, user_info, i, j+1)

def get_unapproved_doctors(doctors, cursor):
    """
    This function returns all unapproved doctors and stores them in a dictionary for efficiency of future
    accesses

    Parameters:
    doctors (dict): dictionary where unverified doctors will be stored in
    cursor (sqlite3.Cursor): Database cursor to execute the query
    """
    query = f"""SELECT User_id, Doctor_id, certificate FROM Doctors WHERE verify_state = 0"""
    cursor.execute(query)
    user_info = cursor.fetchall()
    for user in user_info:
        doctors[user[0]] = [user[0], user[1], user[2]]

def insert_entry(data_frame, user_info, i, j):
    """
    This function inserts an entry of data defined by user_info into the
    frame with the user data in position i, j

    Parameters:
    data_frame (tkinter.Frame): Tkinter frame that contains all the user data
    user_info (list of tuples): A list of tuples, where each tuple contains the information of all users
    i (int): Row / X index to access data and place the entry
    j (int): Column / Y index to access data and place the entry
    """
    e = tk.Entry(data_frame, width = widths[j], bg = "#f9f9f9", fg = '#333333', font = ('Arial', 12, 'bold'))
    e.grid(row = i+1, column = j, sticky="ew")
    e.insert(tk.END, str(user_info[i][j-1]))
    e.config(state="readonly")

def check_valid_input(input_id, cursor):
    """
    Check if the input_id(user_id) exists in the Database. The user_id in database would be seen as valid to delete.

    This function queries the database to determine if the provided user_id
    exists. If it does, the function returns True; otherwise, it returns False.
    If a database error occurs, an error message is displayed, and the function
    returns False.

    Parameters:
    input_id (str): The user_id to be checked in the database.
    cursor (sqlite3.Cursor): Database cursor to execute the query

    Returns:
    bool: True if the user_id exists in the database, False otherwise.
    """
    try:
        cursor.execute("SELECT COUNT(*) FROM Users WHERE user_id = ?", (input_id,))
        result = cursor.fetchone()
        return result[0] > 0
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error occurred: {e}")
        return False


def save_admin(window, entries, conn, test = False):
    """
    This function saves an admin into the database, given the information filled in the entries.

    Parameters:
    window (tk.Tk): window with the save admin functionality
    entries (dict): dictionary with the labels and their corresponding entries
    conn (sqlite3.Connection): connection of the database
    test (boolean): value to pass as true if it is being tested, to not commit into the database
    """
    username = entries["Username"].get().strip()
    password = entries["Password"].get().strip()
    email = entries["Email"].get().strip()
    first_name = entries["First Name"].get().strip()
    last_name = entries["Last Name"].get().strip()
    date_of_birth = entries["Date of Birth"].get().strip()
    phone_number = entries["Phone Number"].get().strip()
    address = entries["Address"].get().strip()

    cursor = conn.cursor()

    if not username or not password:
        messagebox.showerror("Error", "Username and password have to be filled.")
        return

    cursor.execute('SELECT * FROM Users WHERE User_name = ?', (username,))
    if cursor.fetchone():
        messagebox.showerror("Error", "Username already exists!")
        return

    # Insert the user into the Users table
    cursor.execute('''
    INSERT INTO Users (User_name, Password, Email, First_name, Last_name, Date_of_birth, Phone_number, Address)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, password, email, first_name, last_name, date_of_birth, phone_number, address))


    # Get the User_id of the newly inserted user
    user_id = cursor.lastrowid
    cursor.execute('''
    INSERT INTO Admins (User_id)
    VALUES (?)
    ''', (user_id,))

    if not test:
        conn.commit()

    messagebox.showinfo("Success", "Admin added successfully!")
    window.destroy()

def add_admin(root, conn, test=False):
    """
    This function add a user of admin role to the database, and opens a window to collect registration
    of admin data and store it in the database. This function uses a helper function to insert user data in the database

    Parameters:
    root (tk.Tk): root window of the system
    cursor (sqlite3.Cursor): Database cursor to execute the query
    test (bool): if true, doesn't commit changes to database, to make it easier to test

    Returns:
    tk.Toplevel: window created with the add admin functionality
    """
    window = tk.Toplevel(root)
    window.title("Add Admin")

    # Define the labels and input fields
    labels = ["Username", "Password", "Email", "First Name", "Last Name", "Date of Birth", "Phone Number", "Address"]
    entries = {}

    # Create input fields for each label
    for idx, label in enumerate(labels):
        tk.Label(window, text=label).grid(row=idx, column=0)
        entry = tk.Entry(window)
        entry.grid(row=idx, column=1)
        entries[label] = entry

    # Define the Save button to trigger the save_admin function
    save_button = tk.Button(window, text="Save", command=lambda: save_admin(window, entries, conn))
    save_button.grid(row=len(labels), column=1)
    return window

def certificate_validation(user_info, root):
    """
    This function creates the window to validate the certificate of an unverified doctor, using the user's information
    to access their specific certificate, and the root window to create the new window

    Parameters:
    root (tkinter.Tk): The root window from which to create the new one
    user_info (list of tuples): A list of tuples, where each tuple contains the information of all users
    """
    certificate_window = tk.Toplevel(root)
    x, y = get_window_offset(root, 450, 300)
    certificate_window.title("Certificate Awaiting Validation")
    certificate_window.geometry(f'{650}x{500}+{x - 100}+{y - 100}')
    buttons_frame = tk.Frame(certificate_window, relief=tk.SUNKEN, borderwidth=1, bg="#D4D4D4")

    conn = sqlite3.connect("Database.db")

    tk.Button(buttons_frame, text="Accept", command=lambda: approve_doctor(user_info[0], certificate_window, unverified_doctors, conn)).pack(pady=10, side="left", expand= True)
    tk.Button(buttons_frame, text="Reject", command=lambda: delete_user(user_info[0], certificate_window, conn, unverified_doctors)).pack(pady=10, side="left", expand= True)
    pdf_frame = tk.Frame(certificate_window)
    buttons_frame.pack(pady=20, fill="both", expand=True)
    pdf_frame.pack()
    show_pdf = pdf.ShowPdf()
    pdf_viewer = show_pdf.pdf_view(pdf_frame, pdf_location=f"{user_info[2]}")
    pdf_viewer.pack()

    return certificate_window

def approve_doctor(doctor_id, window, unverified, conn):
    """
    This function approves an approved doctor of the given id, destroying the current window in the process

    Parameters:
    window (tkinter.Tk): The root window to destroy
    doctor_id (int): ID of the doctor to approve
    conn (sqlite3.Connection): SQLite database connection object
    unverified (dict): dictionary with the unverified doctors
    """
    cursor = conn.cursor()
    query = f"UPDATE Doctors SET verify_state = 1 WHERE User_id = {doctor_id}"
    cursor.execute(query)
    unverified.pop(doctor_id)
    conn.commit()
    window.destroy()

def delete_user(user_id, window, conn, unverified_list = None):
    """
    This function removes a user from the database, and if it is an unverified doctor, it
    also removes it from the unverified doctors list.

    Parameters:
    window (tkinter.Tk): The root window to destroy
    user_id (int): ID of the user to delete
    conn (sqlite3.Connection): SQLite database connection object
    unverified_list (dict): Dictionary with unverified doctors, passed when deleting an unverified doctor
    """
    cursor = conn.cursor()
    valid = True
    if isinstance(user_id, str):
        user_id = user_id.strip()
        if not check_valid_input(user_id, cursor):
            valid = False
        else:
            user_id = int(user_id)

    if not valid:
        messagebox.showinfo("Error", f"User ID {user_id} is invalid.")
    else:
        cursor.execute(f"DELETE FROM Users WHERE User_id = ?", (user_id,))
        messagebox.showinfo("Success", f"Users with ID {user_id} has been successfully deleted.")
        conn.commit()
        if unverified_list:
            unverified_list.pop(user_id)
            window.destroy()

# main
def main(root = None):
    """
    Function that starts the administrator interface, taking the instance of a tkinter frame as parameter

    Parameters:
    root (tkinter.Tk): Contains the information about the window as it is currently displayed, this variable is
    used to change the current window to display something new.
    """
    create_main_window(root)

if __name__ == "__main__":
    main(None)
