import sys
import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime, timedelta
import copy
import patient_interface as pi

"""
Scheduling system interface

This interface provides operations for patients and doctors to schedule appointments. 
Patients can view available appointments, book appointments and delete appointments. Doctors can view appointment requests, confirm requests and unconfirm/cancel requests.

User roles: 
-Patient:
    - Book new appointments from a list of available time slots.
    - View booked appointments.
    - Delete existing appointments.

-Doctor:
    -View pending appointment requests from patients.
    - Confirm or unconfirm appointments, updating their status.

Global varibles:
    -available_appointments: Tracks available appointment slots in a TreeView widget.
    -booked_appointments: Tracks booked appointment slots in a TreeView widget.
    -back_button, back_button2: Navigation buttons to return to previous windows.
    -empty_message1, empty_message2: Labels displayed when there are no appointments available or booked.
    -old_root: Stores the root window of the scheduling system.

Dependencies:
    - tkinter: Provides GUI components.
    - datetime: Used for handling appointment dates and times.
    - patient_interface: The interface for handling patient-specific operations.

Core Components:
- Classes:
    - Patient: Represents a patient user when the current role is set to patient.
    - Doctor: Represents a doctor user when the current role is set to doctor.
    - Mainclass: Main window and controller for the scheduling system interface.

- Functions:
    - main(user_info, root, role): Entry point for the scheduling system. Initializes the GUI for the given user role.

Key Data Structure:
`user_info (dict)`: A dictionary containing user-specific information.
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

(available_appointments, booked_appointments, back_button, back_button2,
 empty_message1, empty_message2, old_root, inter_root, is_doctor,
 full_name, user_dictionary) = None, None, None, None, None, None, None, None, 0, "", {
    "doctor_name": ("Test", "Doctor")}
double_window = None
start = 1
start_label = None


class StartPage(tk.Frame):
    """
    The Start page of the scheduling system interface.
    This class represents the starting interface for the scheduling system, where patients and doctors can navigate to their respective functionalities.

    Attributes:
        parent (tk.Frame): The parent frame of this interface.
        controller (Mainclass): The main controller managing frame transitions.
    """


    def __init__(self, parent, controller):
        """
        Initializes the StartPage interface.

        Args:
            parent (tk.Frame): The parent frame for this page.
            controller (Mainclass): The controller that manages navigation between pages.

        This method creates navigation buttons:
            - "Book an appointment" and "Go to your appointment list" for patients.
            - "Go to appointment requests" for doctors.
            - "Go back" to return to the previous interface for patients and doctors.
        """


        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=f"Hello, {full_name}!", font=("Arial", 18))
        label.pack(padx=20, pady=20)

        if not is_doctor:
            # Patient-specific options
            # Button to the appointment booking page

            book_button = tk.Button(self, text="Book an appointment", font=('Arial', 18),
                                    command=lambda: controller.show_frame(AppointmentList))
            book_button.pack(expand=True)

            app_list = tk.Button(self, text="Go to your appointment list", font=('Arial', 18),
                                 command=lambda: controller.show_frame(Schedule))
            app_list.pack(expand=True)
        elif is_doctor:
            # Doctor-specific option
            # Button to the list of appointment requests

            app_list = tk.Button(self, text="Go to appointment requests", font=('Arial', 18),
                                 command=lambda: controller.show_frame(Schedule))
            app_list.pack(expand=True)
            
        # Button to navigate back to the previous root interface
        back_button = tk.Button(self, text="Go back", font=('Arial', 18),
                                command=lambda: recover_root(old_root, inter_root))
        back_button.pack(expand=True)


class AppointmentList(tk.Frame):
    """
    This class provides a graphical interface for patients to view and book available appointments in the scheduling system. It displays the list 
    of available time slots and allows users to select and book an appointment.

    Attributes:
        parent (tk.Frame): The parent frame of this interface.
        controller (Mainclass): The main controller managing frame transitions.
    """

    def __init__(self, parent, controller):
        """
        Initializes the Appointment list interface.

        Args:
            parent (tk.Frame): The parent frame for this page.
            controller (Mainclass): The controller that manages navigation between pages.

        This method sets up:
            - A TreeView widget (`available_appointments`) to display the list of available appointments.
            - A scrollbar for checking through the appointment list.
            - Buttons for navigating back to the StartPage.
            - Binds double-click events to handle booking an appointment.

        The list of available appointments is dynamically generated with time slots at 15-minute intervals between 09:00 and 17:00.
        """

        tk.Frame.__init__(self, parent)

        self.label = tk.Label(self, text="List of appointments available for booking", font=("Arial", 18))
        self.label.pack(padx=20, pady=20)
        s = ttk.Style()
        s.theme_use('clam')
        global available_appointments, back_button, user_dictionary
        # if available_appointments is None:
        # Setting up columns and headers for the available appointments TreeView


        available_appointments = ttk.Treeview(self, column=("c1", "c2", "c3", "c4", "c5"), show='headings',
                                              height=5)

        available_appointments.place(x=30, y=95)
        available_appointments["columns"] = ("1", "2", "3", "4", "5")
        available_appointments['show'] = 'headings'
        available_appointments.column("1", width=100, anchor='c')
        available_appointments.column("2", width=100, anchor='c')
        available_appointments.heading("1", text="Account")
        available_appointments.heading("2", text="Type")
        available_appointments.column("# 1", anchor=tk.CENTER)
        available_appointments.heading("# 1", text="Appointment ID")
        available_appointments.column("# 2", anchor=tk.CENTER)
        available_appointments.heading("# 2", text="Doctor")
        available_appointments.column("# 3", anchor=tk.CENTER)
        available_appointments.heading("# 3", text="Date")
        available_appointments.column("# 4", anchor=tk.CENTER)
        available_appointments.heading("# 4", text="Time")
        available_appointments.column("# 5", anchor=tk.CENTER)
        available_appointments.heading("# 5", text="Location")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=available_appointments.yview)
        available_appointments.configure(yscrollcommand=scrollbar.set)
        available_appointments.pack()
        scrollbar.place(x=910, y=75, height=125)
        
        # Generate available time slots at 15-minute intervals between 09:00 and 17:00
        # if counter==1:
        start_time = datetime.strptime("09:00", "%H:%M")
        # End time (5:00 PM)
        end_time = datetime.strptime("17:00", "%H:%M")

        # Interval of 15 minutes
        time_interval = timedelta(minutes=15)

        # Generate all quarter times
        current_time = start_time
        appointment_id = 0
        while current_time <= end_time:
            # print(current_time.strftime("%H:%M"))
            print(user_dictionary)
            available_appointments.insert('', 'end', text="1", values=(
                '0' * (4 - len(str(appointment_id))) + str(appointment_id),
                user_dictionary["doctor_name"][0] + " " + user_dictionary["doctor_name"][1],
                datetime.now().strftime("%d-%m-%Y"),
                current_time.strftime("%H:%M"), 'Einsteinweg 55 - Leiden'))
            current_time += time_interval
            appointment_id += 1

        back_button = tk.Button(self, text="Go back", font=('Arial', 18),
                                command=lambda: controller.show_frame(StartPage))
        back_button.pack(expand=True)
        self.go_back_button = back_button
        available_appointments.bind("<Double-1>", lambda event: OnDoubleClick(event, self, True))
        # fake_event = FakeEvent(0,0)
        # self.double_click = OnDoubleClick(fake_event, self, True)
        # print(self.double_click)

    def AppointmentBook(self, item, window):
        """
        Handles the booking of an appointment.

        Args:
            item (str): The identifier of the selected appointment in the TreeView.
            window (tk.Toplevel): The window displaying the booking confirmation.

        This method:
            - Removes the selected appointment from the available appointments list.
            - Then adds the appointment to the booked appointments list with a "No" confirmation status.
            - Updates the interface to reflect the booking.
            - Displays a success message and closes the confirmation window.
        """

        global empty_message1, empty_message2, back_button
        if (len(available_appointments.get_children())) == 1:
            empty_message1 = tk.Label(self, text="There are currently no appointments available for booking.",
                                      font=("Arial", 18))
            empty_message1.pack(padx=20, pady=20)
        if empty_message2 is not None:
            empty_message2.destroy()

        # Add the selected appointment to the booked appointments list
        new_values = available_appointments.item(item, "values") + ("No",)
        available_appointments.delete(item)
        booked_appointments.insert('', 'end', text="4", values=new_values)
        available_appointments.bind("<Double-1>", lambda event: OnDoubleClick(event, self, True))
        back_button['state'] = tk.NORMAL
        info = tk.Label(self,
                        text=f"Appointment {new_values} booked succesfully. Now, wait upon a doctor confirmation.",
                        font=("Arial", 10))
        # Display success message
        info.pack(padx=20, pady=20)
        self.after(10000, lambda: destroy_label(info))
        self.go_back_button = back_button
        window.destroy()  #


class Schedule(tk.Frame):
    """
    This class provides a graphical interface for both patients and doctors to manage their appointments:
        - Patients can view and delete their appointments.
        - Doctors can view appointment requests and confirm/unconfirm them.

    Attributes:
        parent (tk.Frame): The parent frame of this interface.
        controller (Mainclass): The main controller managing frame transitions.
    """

    def __init__(self, parent, controller):
        """
        Initializes the Schedule interface.

        Args:
            parent (tk.Frame): The parent frame for this page.
            controller (Mainclass): The controller that manages navigation between pages.

        This method sets up:
            - A TreeView widget (`booked_appointments`) to display booked appointments.
            - A scrollbar for chencking through the list of booked appointments.
            - Buttons for going back to the StartPage.
            - Binds double-click events to handle appointment modifications.

        Role-specific functionality:
            - Patients: View and delete their booked appointments.
            - Doctors: View, confirm, or unconfirm appointment requests.
        """

        global is_doctor
        tk.Frame.__init__(self, parent)
        if not is_doctor:
            label = tk.Label(self, text="List of appointments booked by you", font=("Arial", 18))
        elif is_doctor:
            label = tk.Label(self, text="List of appointments to confirm or modify", font=("Arial", 18))
        label.pack(padx=20, pady=20)
        self.main_label = label

        s = ttk.Style()
        s.theme_use('clam')

        global booked_appointments
        global back_button2

        # if booked_appointments is None:
        booked_appointments = ttk.Treeview(self, columns=("1", "2", "3", "4", "5", "6"), show='headings',
                                           height=5)

        booked_appointments.place(x=30, y=95)
        booked_appointments['show'] = 'headings'
        booked_appointments.column("1", width=100, anchor='c')
        booked_appointments.column("2", width=100, anchor='c')

        booked_appointments.heading("1", text="Appointment ID")
        # Change the column name based on the user's role
        if not is_doctor:
            booked_appointments.heading("2", text="Doctor")
        elif is_doctor:
            booked_appointments.heading("2", text="Patient")
        booked_appointments.column("3", anchor=tk.CENTER)
        booked_appointments.heading("3", text="Date")
        booked_appointments.column("4", anchor=tk.CENTER)
        booked_appointments.heading("4", text="Time")
        booked_appointments.column("5", anchor=tk.CENTER)
        booked_appointments.heading("5", text="Location")
        booked_appointments.column("6", anchor=tk.CENTER)
        booked_appointments.heading("6", text="Confirmed")
        scrollbar2 = ttk.Scrollbar(self, orient="vertical", command=booked_appointments.yview)
        booked_appointments.configure(yscrollcommand=scrollbar2.set)
        scrollbar2.place(x=990, y=75, height=125)

        # Bind double-click event only for doctors
        # if isinstance(person, Doctor):
        booked_appointments.bind("<Double-1>", lambda event: OnDoubleClick(event, self, False))
        # booked_appointments.bind("<Double-1>", self.OnDoubleClick)

        booked_appointments.pack()
        # booked_appointments.bind("<Double-1>", self.OnDoubleClick)

        back_button2 = tk.Button(self, text="Go back", font=('Arial', 18),
                                 command=lambda: controller.show_frame(StartPage))
        back_button2.pack(expand=True)
        self.go_back_button = back_button2

    def Confirmation(self, item, number, window):
        """
        Handles the confirmation or unconfirmation of an appointment.
        
        Args:
            item (str): The identifier of the selected appointment in the TreeView.
            number (int): The action to perform:
                - 1: Confirm the appointment.
                - 0: Unconfirm the appointment.
            window (tk.Toplevel): The window displaying the confirmation options.

        This method updates the confirmation status of the selected appointment and reflects the change in the UI.
        """

        global back_button2
        back_button2['state'] = tk.NORMAL
        item_values = booked_appointments.item(item, "values")
        temp_list = list(item_values)
        # Change the last entry to "Yes"
        # Update the confirmation status of the selected appointment
        if number == 1:
            temp_list[-1] = 'Yes'
            message = f"Appointment {item_values} confirmed succesfully."
        else:
            temp_list[-1] = 'No'
            message = f"Appointment {item_values} unconfirmed succesfully."
        info = tk.Label(self,
                        text=message,
                        font=("Arial", 10))
        info.pack(padx=20, pady=20)
        self.after(10000, lambda: destroy_label(info))
        booked_appointments.item(item, values=temp_list)
        # print(temp_list)
        window.destroy()
        booked_appointments.bind("<Double-1>", lambda event: OnDoubleClick(event, self, False))

    def Deletion(self, item, window):
        """
        Handles the deletion of a booked appointment for patients.

        Args:
            item (str): The identifier of the selected appointment in the TreeView.
            window (tk.Toplevel): The window displaying the deletion confirmation.

        This method:
            - Removes the appointment from the `booked_appointments` list.
            - Adds the appointment back to the `available_appointments` list.
            - Updates the interface and displays a success message.
        """

        global empty_message1, empty_message2
        if (len(booked_appointments.get_children())) == 1:
            empty_message2 = tk.Label(self, text="There are currently no appointments booked by you.",
                                      font=("Arial", 18))
            empty_message2.pack(padx=20, pady=20)
        if empty_message1 is not None:
            empty_message1.destroy()
        global back_button2
        back_button2['state'] = tk.NORMAL
        new_values = booked_appointments.item(item, "values")
        modified_tuple = new_values[:-1]
        # print(modified_tuple)
        booked_appointments.delete(item)
        # booked_appointments.insert(item,0)
        available_appointments.insert('', 'end', text="4", values=modified_tuple)
        info = tk.Label(self,
                        text=f"Appointment {new_values} deleted succesfully. Now, it is again available for booking.",
                        font=("Arial", 10))
        info.pack(padx=20, pady=20)
        self.after(10000, lambda: destroy_label(info))
        window.destroy()
        booked_appointments.bind("<Double-1>", lambda event: OnDoubleClick(event, self, False))


class Mainclass(tk.Tk):
    """
    The main class for the scheduling system.

    This class initializes the main application window and manages the navigation 
    between different pages of the scheduling system (StartPage, AppointmentList, Schedule).

    Attributes:
        frames (dict): A dictionary storing the initialized frames (pages) of the application.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the main window and sets up the frame container.

        Args:
            *args: Variable length argument list for the Tkinter application.
            **kwargs: Arbitrary keyword arguments for the Tkinter application.

        This method:
            - Creates a container frame to hold all application pages.
            - Initializes and stores frames for StartPage, AppointmentList, and Schedule.
            - Displays the StartPage as the initial page.
        """

        tk.Tk.__init__(self, *args, **kwargs)
        # Create a container to hold all the application pages
        # Configure the grid to allow flexible resizing

        container = tk.Frame(self)
        container.pack(side="top", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        self.frames = {}
        # Initialize and store instances of all application pages in a dictionary
        # Position each frame in the same grid location to allow seamless switching

        for F in (StartPage, AppointmentList, Schedule):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        print("Frames: ", len(self.frames.keys()))
        self.start_frame = StartPage
        # Display the StartPage as the initial page
        self.show_frame(StartPage)

    def show_frame(self, cont):
        """
        Displays the specified page in the window.

        Args:
            cont (class): The class of the frame to be displayed.

        This method raises the frame associated with the given class (`cont`) to the top
        of the stack, making it visible to the user.
        """

        frame = self.frames[cont]
        frame.tkraise()


def destroy_label(label):
    """
    Destroys a given Tkinter label widget.
    Args:
        label (tk.Label): The label widget to be destroyed.
    """

    label.destroy()


def recover_root(scheduling_root, interface_root):
    """
    Returns to the main interface from the scheduling system.
    Args:
        scheduling_root (tk.Toplevel): The current scheduling window to be withdrawn.
        interface_root(tk.Tk): The root window of the main interface to be restored.
    """

    scheduling_root.withdraw()
    interface_root.deiconify()
    print("Scheduling root: ", scheduling_root.winfo_viewable())
    print("Interface root: ", interface_root.winfo_viewable())

    # print(type(interface_root))
    # pi.main(user_info["user_id"], None)


def on_close(new_window, window, if_appointment_book):
    """
    Handles the closing of a secondary window in the scheduling system.
    Re-enables the appropriate navigation button and rebinds event listeners for the main window's appointment list.

    Args:
        new_window (tk.Toplevel): The window being closed.
        window (tk.Frame): The parent window to rebind the event listeners.
        if_appointment_book (bool): Determines which button and list to update:
            - True: Updates for booking appointments.
            - False: Updates for modifying booked appointments.
    """

    global back_button, back_button2
    back_button = back_button if if_appointment_book else back_button2
    back_button['state'] = tk.NORMAL
    # available_appointments.bind("<Double-1>", window.OnDoubleClick)
    data = available_appointments if if_appointment_book else booked_appointments
    data.bind("<Double-1>", lambda event: OnDoubleClick(event, window, if_appointment_book))
    new_window.destroy()


def OnDoubleClick(event, window, if_appointment_book):
    """
    Handles double-click events when users operator on the appointment lists.

    This function determines whether the patient is interacting with available appointments (for booking) or modify appointments for patients and doctors. 
    It opens a new window to display details of the selected appointment and provides options to book, delete, or modify the appointment based on the user's role (patient or doctor).

    Args:
        event (tk.Event): The double-click event triggered by the user, containing information about the clicked location.
        window (tk.Frame): The parent window in which the event occurred.
        if_appointment_book (bool): A flag indicating the type of appointment list:
            - True: Interacting with available appointments for booking.
            - False: Interacting with booked appointments for modification.

    Returns:
        None
    """

    global back_button, back_button2, available_appointments, booked_appointments, double_window
    if if_appointment_book:
        data, title = available_appointments, "Appointment booking"
        button = back_button

    else:
        data, title = booked_appointments, "Booked appointment modification"
        button = back_button2
    button['state'] = tk.DISABLED
    if event is not None:
        region = data.identify_region(event.x, event.y)
        print(region)
        # Ignore clicks on the heading or empty space
        while region == "heading" or region == "nothing" or region == "separator":
            button['state'] = tk.NORMAL
            return "break"

    data.unbind("<Double-1>")
    item = data.selection()
    item_values = data.item(item, "values")
    print("you clicked on", data.item(item, "values"))
    new_window = tk.Toplevel(window)  # Create a new Toplevel window
    new_window.protocol("WM_DELETE_WINDOW", lambda: on_close(new_window, window, if_appointment_book))
    new_window.title(title)
    new_window.geometry("600x300")
    double_window = new_window
    print("Double window: ", double_window)
    label = ttk.Label(new_window, text=f"Appointment details: {item_values}")
    label.pack(pady=20)
    if if_appointment_book:
        label2 = ttk.Label(new_window, text="Do you want to book this appointment?")
        label2.pack(pady=20)

        # Button to close the new window
        yes_button = ttk.Button(new_window, text="Yes", command=lambda: window.AppointmentBook(item, new_window))
        yes_button.pack(pady=10)
        no_button = ttk.Button(new_window, text="No",
                               command=lambda: on_close(new_window, window, if_appointment_book))
        no_button.pack(pady=10)
    else:
        
        # Doctor-specific options: Confirm or unconfirm appointments
        if is_doctor == 1:
            label2 = ttk.Label(new_window, text="Apply modifications to this appointment:")
            label2.pack(pady=20)
            confirm_button = tk.Button(new_window, text="Confirm", font=('Arial', 18),
                                       command=lambda: window.Confirmation(item, 1, new_window))
            confirm_button.pack(expand=True)
            unconfirm_button = tk.Button(new_window, text="Unconfirm", font=('Arial', 18),
                                         command=lambda: window.Confirmation(item, 0, new_window))
            unconfirm_button.pack(expand=True)
        # Patient-specific option: Delete appointment
        elif is_doctor == 0:
            label2 = ttk.Label(new_window, text="Do you want to delete this appointment?")
            label2.pack(pady=20)
            # Move the Delete button inside the patient block
            delete_button = tk.Button(new_window, text="Delete", font=('Arial', 18),
                                      command=lambda: window.Deletion(item, new_window))
            delete_button.pack(expand=True)
        button2 = tk.Button(new_window, text="Go back", font=('Arial', 18),
                            command=lambda: on_close(new_window, window, if_appointment_book))
        button2.pack(expand=True)


def stop_program(main_root):
    main_root.destroy()
    sys.exit()


class Patient():
    """
    Represents a patient in the scheduling system.

    Attributes:
        name (str): The first name of the patient.
        surname (str): The last name of the patient.
    """

    def __init__(self, name, surname):
        self.name = name
        self.surname = surname

    def __repr__(self):
        return self.name + " " + self.surname


class Doctor():
    """
    Represents a doctor in the scheduling system.

    Attributes:
        name (str): The first name of the doctor.
        surname (str): The last name of the doctor.
    """

    def __init__(self, name, surname):
        self.name = name
        self.surname = surname

    def __repr__(self):
        return self.name + " " + self.surname


def main(user_info, root, role):
    """
    Entry point of the scheduling system.
    This function initializes the scheduling system's Graphical User Interface(GUI) and handles the global variables for appointments. It distinguishes between patient and doctor roles to provide customized functionality.
    Args:
        user_info (dict): A dictionary containing user-specific information.
        root (tk.Tk): The root Tkinter window passed from the previous interface.
        role (int): The user's role, where 1 represents a doctor and 0 represents a patient.

    Returns:
        None

    """

    global old_root, counter, inter_root, is_doctor, inter_root, full_name, user_dictionary, start

    is_doctor, inter_root, user_dictionary = role, root, user_info
    # root_copy = copy.deepcopy(root)
    # inter_root = root
    root.withdraw()

    # Example usage
    iam_doctor = role  # Change this to True if the user is a doctor
    if user_info["first_name"] == None or user_info["last_name"] == None:
        full_name = ""
    else:
        full_name = user_info["first_name"] + " " + user_info["last_name"]
    if "doctor_name" not in user_info.keys() or user_info["doctor_name"] == (None, None):
        user_dictionary["doctor_name"] = ("", "")
    if iam_doctor:
        person = Doctor(user_info["first_name"], user_info["last_name"])
    else:
        person = Patient(user_info["first_name"], user_info["last_name"])

    if old_root is not None:
        old_root.deiconify()

    else:

        old_root = Mainclass()
        old_root.title("Scheduling system")
        if start:
            old_root.protocol("WM_DELETE_WINDOW", lambda: stop_program(old_root))
            old_root.mainloop()


info_dict = {"doctor_name": ("Jack", "Strong"), "first_name": None, "last_name": None}
'''
root=tk.Tk()

main(info_dict, root, 0)
'''






