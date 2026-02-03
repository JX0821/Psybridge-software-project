'''
Author: Jixuan Yao, Marit Paul
This document contain tests for Log_in_System. The statement coverage of tests is 85%. However, the test for
 checking verification code needs UI interaction (counts 3% coverage). If you run it and input value 1234
 then the test will pass.
'''

import unittest
import os
import sqlite3
import Log_in_System as login
from Log_in_System import home, var_name, var_pwd, bt_register, bt_login, bt_quit, bt_forget_psw,user_login,open_interface
# from unittest.mock import patch
from unittest.mock import patch, MagicMock, mock_open, ANY,call
import tkinter as tk

# import requests
# import random as rd


class TestInitDb(unittest.TestCase):
    """
    Tests for the init_db function.
    This class verifies: 1. Proper exception raising for missing databases. 2. Correctly connect the database
    when they exist.

    We applied gray-box tests here, combining partitioning test and coverage based test
    where the statement coverage is 100% (coverage of the function that is tested)
    and each branch is excuted at least once. Four test cases are designed for four
    equivalence partitions of the input:
    {database1 exists & database2 not exist, database1 not exist & database2 exist,
    both databases exist, neither database exists}.Every conditions are evaluated, and
    every decisions are evaluated.
    """

    def test_both_files_exist(self):
        """
        Case 1: Both files exist.
        Test if the function passes without raising an exception when both files exist.
        """
        # create dummy temporary files for testing
        with open("TestDatabase1.db", "w") as db:
            db.write("")
        with open("TestRegisterDoctor1.db", "w") as reg:
            reg.write("")

        # no exception should be raised
        try:
            login.init_db("TestDatabase1.db", "TestRegisterDoctor1.db")
        except Exception as e:
            self.fail(f"Unexpected exception raised when both files exist: {e}")
        finally:
            # remove the temporary test database
            os.remove("TestDatabase1.db")
            os.remove("TestRegisterDoctor1.db")

    def test_first_file_missing(self):
        """
        Case 2: The first file is missing.
        Test if the function raises FileNotFoundError with the correct message.
        """
        with open("TestRegisterDoctor2.db", "w") as reg:
            reg.write("")

        with self.assertRaises(FileNotFoundError) as context:
            login.init_db("NonExistentDatabase1.db", "TestRegisterDoctor2.db")

        self.assertIn("Database file 'NonExistentDatabase1.db' does not exist", str(context.exception))

        # Clean up
        os.remove("TestRegisterDoctor2.db")

    def test_second_file_missing(self):
        """
        Case 3: The second file is missing.
        Test if the function raises FileNotFoundError with the correct message.
        """
        with open("TestDatabase2.db", "w") as db:
            db.write("")

        with self.assertRaises(FileNotFoundError) as context:
            login.init_db("TestDatabase2.db", "NonExistentRegisterDoctor1.db")

        self.assertIn("Unverified data file 'NonExistentRegisterDoctor1.db' does not exist", str(context.exception))

        # Clean up
        os.remove("TestDatabase2.db")

    def test_both_files_missing(self):
        """
        Case 4: Both files are missing.
        Test if the function raises FileNotFoundError for the first missing file.
        """
        with self.assertRaises(FileNotFoundError) as context:
            login.init_db("NonExistentDatabase2.db", "NonExistentRegisterDoctor2.db")

        self.assertIn("Database file 'NonExistentDatabase2.db' does not exist", str(context.exception))

# Because the original login function is interacted frequently with GUI, which is very difficult to design the test,
# so we design a stub function for it which contains its main functionality without interaction with GUI

# def stub_user_login(username, password):
#     """
#     Simulates user login logic without interacting with Tkinter.
#
#     The main functionalities and logic of this stub function are the same with the user_login function, but we removed
#     the parts which need to interact with Tkinter,  instead, we use the tuple to contain the information of status and
#     message which should be shown by Tkinter.
#
#     Parameters:
#         username (str): The entered username.
#         password (str): The entered password.
#
#     Returns:
#         tuple: A tuple (status, message) of the result of the login attempts.
#                - status: "success", "error", or "prompt".
#                - message: Additional information, such as a welcome message or error details.
#     """
#     if not username or not password:
#         return "error", "Empty username or password"
#
#     # Connect to the database
#     conn = sqlite3.connect('Database.db')
#     cursor = conn.cursor()
#
#     # Query the database for the user
#     cursor.execute("SELECT password, User_id FROM users WHERE User_name = ?", (username,))
#     result = cursor.fetchone()
#
#     if result:
#         stored_password, user_id = result
#         if password == stored_password:  # Compare plain text password
#             # Check the role by querying the respective tables
#             roles_tables = {
#                 "Patients": "patient",
#                 "Admins": "admin",
#                 "Doctors": "doctor",
#             }
#
#             for table, role in roles_tables.items():
#                 cursor.execute(f"SELECT 1 FROM {table} WHERE User_id = ?", (user_id,))
#                 if cursor.fetchone():  # If a match is found in the table
#                     conn.close()
#                     return "success", f"Welcome, {username}! You are logged in as a {role}."
#
#             conn.close()
#             return "error", "Role not found for this user."
#         else:
#             conn.close()
#             return "error", "Incorrect password"
#     else:
#         conn.close()
#         return "prompt", "User not found. Would you like to register?"
#
# class TestStubUserLogin(unittest.TestCase):
#     '''
#     class of tests for the stub login function
#
#     The tests included in this class is a grey-box test, including partitioning test and coverage based unittest, where
#      the statement coverage is 100% (coverage of the function that is tested) and each branch is excuted at least once.
#      Six test cases are designed for six equivalence partitions of the input:{empty username and/or password, username
#      not exists, username exists and password incorrect, username exists and password correct and role is doctor,
#      username exists and password correct and role is patient, username exists and password correct and role is admin}.
#      We use the exsistent data:
#      admin : user name:  "HarperZ" ,password: "4a7d1ed414474e4033ac29ccb8653d9b";
#     doctor: user name: "WatsonB", password: "4a7d1ed414474e4033ac29ccb8653d9b";
#     patient: user name: “SmithJ”,  password: “4a7d1ed414474e4033ac29ccb8653d9b";
#     every conditions are evaluated, and every decisions are evaluated.
#
#     '''
#
#     # Case 1: Empty username and/or password
#     def test_empty_username_or_password(self):
#         '''
#         Tests the case where the username and/or password fields are empty.
#         '''
#         status, message = stub_user_login("", "")
#         self.assertEqual(status, "error")
#         self.assertEqual(message, "Empty username or password")
#
#     # Case 2: Username does not exist
#     def test_username_not_exists(self):
#         '''
#         Tests the case where the provided username does not exist in the database.
#         '''
#         status, message = stub_user_login("nonexistent_user", "password123")
#         self.assertEqual(status, "prompt")
#         self.assertEqual(message, "User not found. Would you like to register?")
#
#     # Case 3: Username exists but password is incorrect
#     def test_username_exists_password_incorrect(self):
#         '''
#         Tests the case where the username exists but the password is incorrect.
#         '''
#         status, message = stub_user_login("HarperZ", "wrong_password")
#         self.assertEqual(status, "error")
#         self.assertEqual(message, "Incorrect password")
#
#     # Case 4: Username and password are correct and the role is admin
#     def test_username_exists_password_correct_admin(self):
#         '''
#         Tests the case where the username and password are correct and the role is admin.
#         '''
#         status, message = stub_user_login("HarperZ", "4a7d1ed414474e4033ac29ccb8653d9b")
#         self.assertEqual(status, "success")
#         self.assertIn("Welcome, HarperZ", message)
#         self.assertIn("admin", message)
#
#     # Case 5: Username and password are correct and the role is doctor
#     def test_username_exists_password_correct_doctor(self):
#         '''
#         Tests the case where the username and password are correct and the role is doctor.
#         '''
#         status, message = stub_user_login("WatsonB", "4a7d1ed414474e4033ac29ccb8653d9b")
#         self.assertEqual(status, "success")
#         self.assertIn("Welcome, WatsonB", message)
#         self.assertIn("doctor", message)
#
#     def test_username_exists_password_correct_patient(self):
#         '''
#         Tests the case where the username and password are correct and the role is patient.
#         '''
#         status, message = stub_user_login("SmithJ", "4a7d1ed414474e4033ac29ccb8653d9b")
#         self.assertEqual(status, "success")
#         self.assertIn("Welcome, SmithJ", message)
#         self.assertIn("patient", message)


class TestOpenBlankPage(unittest.TestCase):
    @patch("tkinter.Toplevel")  # Mock the Toplevel class to avoid GUI creation
    def test_open_blank_page_runs(self, mock_toplevel):
        """
        Test that open_blank_page runs without errors for different roles.

        This test applies Black-Box Testing to verify that the function runs successfully for valid inputs
        without focusing on the internal implementation or GUI interactions.
        """
        try:
            login.open_blank_page("Patient")
            login.open_blank_page("Doctor")
        except Exception as e:
            self.fail(f"open_blank_page raised an exception: {e}")

        # Ensure Toplevel is called for each role
        self.assertEqual(mock_toplevel.call_count, 2, "Toplevel should be called twice.")

class TestLoginHomeWindow(unittest.TestCase):
    '''
    This class includes several white-box tests for the setting of the home windows and its components
    '''
    @classmethod
    def setUpClass(cls):
        """
        Initialize the home window for test
        """
        cls.home = home

    def test_window_title(self):
        """
        Test if the home window title is correctly set.
        """
        self.assertEqual(self.home.title(), "Welcome to Psybridge")

    def test_window_size_and_position(self):
        """
        Test if the window size and position are correct
        """
        # Tkinter layout information is only fully updated after the event loop runs
        # or update_idletasks() is called. Call the update_idletasks() make sure
        # winfo_x() and winfo_y() return the correct positions.
        self.home.update_idletasks()

        geometry = self.home.geometry()
        self.assertTrue(geometry.startswith("450x300"), f"Unexpected geometry: {geometry}")

    def test_labels_exist(self):
        """
        Test if the 'Username' and 'Password' labels exist.
        """
        labels = [widget for widget in self.home.winfo_children() if widget.winfo_class() == 'Label']
        label_texts = [label.cget("text") for label in labels]
        self.assertIn("Username", label_texts, "'Username' label is missing.")
        self.assertIn("Password", label_texts, "'Password' label is missing.")

    def test_entry_fields_exist(self):
        """
        Test if two entry fields for 'Username' and 'Password' exist.
        """
        entries = [widget for widget in self.home.winfo_children() if widget.winfo_class() == 'Entry']
        self.assertEqual(len(entries), 2, "Entry fields are not correctly set up.")
        self.assertTrue(any(entry["textvariable"] == str(var_name) for entry in entries),
                        "Entry field for 'Username' is missing.")
        self.assertTrue(any(entry["textvariable"] == str(var_pwd) for entry in entries),
                        "Entry field for 'Password' is missing.")

    def test_entry_fields_position(self):
        """
        Test if the entry fields are positioned correctly.
        """
        # Tkinter layout information is only fully updated after the event loop runs
        # or update_idletasks() is called. Call the update_idletasks() make sure
        # winfo_x() and winfo_y() return the correct positions.
        self.home.update_idletasks()

        for widget in self.home.winfo_children():
            if widget.winfo_class() == 'Entry' and widget["textvariable"] == str(var_name):
                self.assertEqual(widget.winfo_x(), 160, "Username entry field x position is incorrect.")
                self.assertEqual(widget.winfo_y(), 150, "Username entry field y position is incorrect.")
            if widget.winfo_class() == 'Entry' and widget["textvariable"] == str(var_pwd):
                self.assertEqual(widget.winfo_x(), 160, "Password entry field x position is incorrect.")
                self.assertEqual(widget.winfo_y(), 190, "Password entry field y position is incorrect.")

    def test_buttons_creation_and_layout(self):
        """
        Test if buttons in homw are created and positioned correctly.
        """

        self.home.update_idletasks()
        # Register button
        self.assertEqual(bt_register.cget("text"), "Register")
        self.assertEqual(bt_register.winfo_x(), 40)
        self.assertEqual(bt_register.winfo_y(), 230)

        # Login button
        self.assertEqual(bt_login.cget("text"), "Login")
        self.assertEqual(bt_login.winfo_x(), 110)
        self.assertEqual(bt_login.winfo_y(), 230)

        # Quit button
        self.assertEqual(bt_quit.cget("text"), "Quit")
        self.assertEqual(bt_quit.winfo_x(), 170)
        self.assertEqual(bt_quit.winfo_y(), 230)

        # Password button
        self.assertEqual(bt_forget_psw.cget("text"), "Forgot Your Password?")
        self.assertEqual(bt_forget_psw.winfo_x(), 220)
        self.assertEqual(bt_forget_psw.winfo_y(), 230)

    # use patch object t replace the mainloop method of 'home'
    @patch.object(home, 'mainloop')
    def test_mainloop(self, mock_mainloop):
        """
        Test if mainloop runs.
        """
        home.mainloop()

        #make sure 'mainloop' is called once
        mock_mainloop.assert_called_once()

# mutated login function for mutation test( change the condition 'password == stored_password'
# to 'password != stored_password'):
# def user_login():
#     """
#     Open the login window and handle user login data by comparing the input data with the database.
#     This function has been mutated for testing purposes.
#     """
#     # get user name and password from the input area:
#     user_name = var_name.get()
#     user_pwd = var_pwd.get()
#
#     conn = sqlite3.connect('Database.db')
#     cursor = conn.cursor()
#
#     cursor.execute('SELECT password, User_id FROM users WHERE User_name = ?', (user_name,))
#     result = cursor.fetchone()
#
#     # check if we have this username in the database
#     if result:
#         stored_password, user_id = result
#
#         # Mutation 1: Incorrect password comparison
#         if user_pwd != stored_password:  # Changed == to !=
#             tk.messagebox.showinfo(title='Welcome', message='Welcome, ' + user_name + "\U0001F603")
#
#             # Mutation 2: Return incorrect role data
#             cursor.execute('SELECT 1 FROM Patients WHERE User_id = ?', (user_id,))
#             is_patient = None  # Incorrectly fixed to None
#
#             cursor.execute('SELECT 1 FROM Admins WHERE User_id = ?', (user_id,))
#             is_admin = True  # Incorrectly fixed to True
#
#             cursor.execute('SELECT 1 FROM Doctors WHERE User_id = ?', (user_id,))
#             is_doctor = None  # Incorrectly fixed to None
#
#             if is_patient:
#                 open_interface('patient', user_id)
#             elif is_admin:
#                 open_interface('admin', user_id)
#             elif is_doctor:
#                 open_interface('doctor', user_id)
#
#         else:
#             tk.messagebox.showerror(message='Incorrect Password ☹')
#
#     elif user_name == "" or user_pwd == "":
#         tk.messagebox.showerror(message='empty username or password ☹')
#
#     # if the user not in the database, prompt to register
#     else:
#         go_signup = tk.messagebox.askyesno('Welcome', 'You have not registered yet. Would you like to register now?😊')
#         return "prompt" if go_signup else "error"
class TestUserLogin(unittest.TestCase):
    '''
    class of tests for the login function

    The tests included in this class is a grey-box test, including partitioning test and coverage based unittest, where
    the statement coverage is 100% (coverage of the function that is tested) and each branch is excuted at least once.
    Four test cases are designed for four equivalence partitions of the input:{empty username and/or password, username
    not exists, username exists and password incorrect, username exists and password correct}.
    We use the exsistent data:
    admin : user name:  "HarperZ" ,password: "4a7d1ed414474e4033ac29ccb8653d9b";
    every conditions are evaluated, and every decisions are evaluated.

    '''
    def setUp(self):
        """
        Set mock tkinter variables and functions for testing.
        """

        # mock messagebox
        self.messagebox_mock = MagicMock()
        self.original_messagebox = tk.messagebox
        tk.messagebox = self.messagebox_mock

        # mock tkinter logic
        self.original_toplevel = tk.Toplevel
        tk.Toplevel = MagicMock()

    def tearDown(self):
        """
        drawback to original tkinter functions after test.
        """
        tk.messagebox = self.original_messagebox
        tk.Toplevel = self.original_toplevel

    @patch("Log_in_System.open_interface")
    def test_empty_username_and_password(self, mock_open_interface):
        """
        login with empty username and password fields.
        """
        # Mock open_interface to avoid triggering actual interface
        mock_open_interface.return_value = None


        var_name.set("")
        var_pwd.set("")

        result = user_login()

        self.messagebox_mock.showerror.assert_called_once_with(
            message='empty username or password ☹'
        )

        # verify open_interface was not called
        mock_open_interface.assert_not_called()

        # return value
        self.assertEqual(result, "error")

    @patch("Log_in_System.open_role_selection")
    def test_user_chooses_register(self, mock_open_role_selection):
        """
        Test case for non-existent username.
        """
        var_name.set("NonExistentUser")
        var_pwd.set("any_password")

        # Simulate user selecting "Yes" in the messagebox prompt
        self.messagebox_mock.askyesno.return_value = True

        # Call the function
        result = user_login()

        # Check that the prompt was displayed
        self.messagebox_mock.askyesno.assert_called_once_with(
            'Welcome', 'You have not registered yet. Would you like to register now?😊'
        )

        # Ensure that open_role_selection was called
        mock_open_role_selection.assert_called_once()

        # Check the return value
        self.assertEqual(result, None)

    @patch("Log_in_System.open_interface")
    def test_admin_login_success(self, mock_open_interface):
        """
        Test case for correct username and password.
        """
        # mock for return value of function open_interface()
        mock_open_interface.return_value = None

        # mockfor username and password
        var_name.set("HarperZ")
        var_pwd.set("0000")

        result = user_login()

        # verify welcome message was displayed
        self.messagebox_mock.showinfo.assert_called_once_with(
            title='Welcome', message='Welcome, HarperZ\U0001F603'
        )

        # verift that open_interface_window was called with admin role
        mock_open_interface.assert_called_once_with(51)
        self.assertEqual(result, "success")

    @patch("Log_in_System.open_interface")
    def test_admin_login_wrong_password(self, mock_open_interface):
        """
        Test case for incorrect password.
        """
        # mock for return value of function open_interface()
        mock_open_interface.return_value = None

        var_name.set("HarperZ")
        var_pwd.set("wrong_password")

        result = user_login()

        self.messagebox_mock.showerror.assert_called_once_with(
            message='Incorrect Password ☹'
        )

        mock_open_interface.assert_not_called()

        # verify the return value
        self.assertEqual(result, "error")

class TestOpenInterfaceSimple(unittest.TestCase):
    '''
    This class includes three tests for function open_interface(user_id). Gray-box tesing is applied, integrating both
    partitioning test and coverage based unittest, where the statement coverage is 100% (coverage of the function that
    is tested) and each branch is excuted at least once.
    Three test cases are designed for three equivalence partitions of the input:{user role is patient, user role is
    doctor, user role is admin}. Every condition and decision is considered.
    '''
    @patch("Log_in_System.pi.main")
    @patch("Log_in_System.ad.main")
    @patch("Log_in_System.do.main")
    @patch("Log_in_System.home", create=True)
    @patch("sqlite3.connect")
    def test_open_interface_patient(self, mock_connect, mock_home, mock_doctor_main, mock_admin_main, mock_patient_main):
        """
        Test if patient interface is opened when user role is patient
        """

        # mock database cursor
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchone.side_effect = [
            True,  # user in Patients table
            None,  # user in Admin table
            None   # user in Doctor table
        ]

        open_interface(1)

        # verify pi.main was called
        mock_patient_main.assert_called_once()  # Ensure pi.main was called exactly once

        # verify no other interfaces were called
        mock_admin_main.assert_not_called()
        mock_doctor_main.assert_not_called()

    @patch("Log_in_System.pi.main")
    @patch("Log_in_System.ad.main")
    @patch("Log_in_System.do.main")
    @patch("Log_in_System.home", create=True)
    @patch("sqlite3.connect")
    def test_open_interface_doctor(self, mock_connect, mock_home, mock_doctor_main, mock_admin_main, mock_patient_main):
        """
        Test if doctor interface is opened when user role is doctor
        """

        # mock database cursor
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchone.side_effect = [
            None,  # user in Patients table
            None,  # user in Admin table
            True  # user in Doctor table
        ]

        open_interface(3)

        # verify do.main was called
        mock_doctor_main.assert_called_once()  # Ensure do.main was called exactly once

        # verify no other interfaces were called
        mock_patient_main.assert_not_called()
        mock_admin_main.assert_not_called()

    @patch("Log_in_System.pi.main")
    @patch("Log_in_System.ad.main")
    @patch("Log_in_System.do.main")
    @patch("Log_in_System.home", create=True)
    @patch("sqlite3.connect")
    def test_open_interface_admin(self, mock_connect, mock_home, mock_doctor_main, mock_admin_main, mock_patient_main):
        """
        Test if admin interface is opened when user role is admin
        """

        # mock database cursor
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchone.side_effect = [
            None,  # first call, user in Patients table
            True,  # second call, user in Admins table
            None  # third call, user in Doctors table
        ]

        open_interface(2)

        # verify ad.main was called
        mock_admin_main.assert_called_once()  # Ensure ad.main was called exactly once

        # verify no other interfaces were called
        mock_patient_main.assert_not_called()
        mock_doctor_main.assert_not_called()

class TestIsAllowedType(unittest.TestCase):
    """
    This class includes gray box test cases for is_allowed_type function.

    The test cases are designed to cover all conditions and decisions in the function.
    Statement coverage of the function is 100%, and all logical branches are executed at least once.
    """

    def test_allowed_file_types(self):
        """
        Test files with allowed and disallowed extensions.
        """
        self.assertTrue(login.is_allowed_type("test_document.pdf"))
        self.assertTrue(login.is_allowed_type("image.png"))
        self.assertTrue(login.is_allowed_type("photo.jpg"))
        self.assertFalse(login.is_allowed_type("test_document.txt"))

class TestIsAllowedSize(unittest.TestCase):
    """
    This class includes boundary value test cases for the is_allowed_size function.

    The test cases cover the edge cases of file size limits, ensuring correctness at and around
    the boundary of 6MB. The statement coverage of the function is 100%, and the boundary conditions
    are evaluated.
    """
    @patch("os.path.getsize")
    def test_different_size(self,mock_getsize):
        # size at the edge under boundry
        mock_getsize.return_value = 6 * 1024 * 1024 - 1
        self.assertTrue(login.is_allowed_size("dummy_path"))

        # exactly 6MB
        mock_getsize.return_value = 6 * 1024 * 1024
        self.assertTrue(login.is_allowed_size("dummy_path"))

        # size at the edge beyound boundry
        mock_getsize.return_value = 6 * 1024 * 1024 + 1
        self.assertFalse(login.is_allowed_size("dummy_path"))


class TestUploadFileWindow(unittest.TestCase):
    """
    Test class for upload_file_window function.
    """

    @patch("Log_in_System.handle_file_upload")
    @patch("tkinter.Toplevel")
    @patch("tkinter.Label")
    @patch("tkinter.Button")
    @patch("tkinter.messagebox.showinfo")
    @patch("tkinter.filedialog.askopenfilename")
    def test_upload_file_window(
        self,
        mock_file_upload,
        mock_showinfo,
        mock_button,
        mock_label,
        mock_toplevel,
        mock_handle_file_upload,
    ):
        """
        Test the behavior of the uploaading file and the components of the window
        """
        mock_window = MagicMock()
        mock_toplevel.return_value = mock_window
        mock_file_upload.return_value = "dummy_file.pdf"
        mock_handle_file_upload.return_value = "File uploaded successfully."

        login.upload_file_window("user123", "pass123", "user@example.com")

        # check the window and the labels are created
        mock_toplevel.assert_called_once()
        mock_label.assert_any_call(mock_window, text="Please upload your Professional Qualification Certificate")
        mock_label.assert_any_call(mock_window, text="No file selected")

        # mock selection
        select_file_button = mock_button.call_args_list[0][1]["command"] # call the command parameter of the first defined mock button
        # the first button is select
        select_file_button() # the button's command is called, which is mock_file_upload
        mock_file_upload.assert_called_once()

        # simulate upload
        upload_button = mock_button.call_args_list[1][1]["command"] # call the command parameter of the second defined mock button
        # the second button is upload
        upload_button() # the button's command is called, which is mock_handle_file_upload,
        mock_handle_file_upload.assert_called_once_with("dummy_file.pdf", "user123", "pass123", "user@example.com")
        mock_showinfo.assert_called_once_with("Success", "File uploaded successfully.")

class TestHandleFileUpload(unittest.TestCase):
    """
    This class includes test cases for the 'handle_file_upload' function. This class applies grey box test including
    partitioning test and coverage based test. Four eqvailence classes are evaluated{ corect file with valid username,
     file of invalid type, file of invalid size, invalid(exsistent) username}. All the branches are excuted at least once.
    """

    @patch("shutil.copyfile")
    @patch("os.makedirs")
    @patch("os.path.join")
    @patch("sqlite3.connect")
    @patch("Log_in_System.is_allowed_size")
    @patch("Log_in_System.is_allowed_type")
    def test_successful_upload(self, mock_is_allowed_type, mock_is_allowed_size, mock_sqlite_connect, mock_path_join, mock_makedirs, mock_copyfile):
        """
        Test for successful file upload--corect file with valid username.
        """

        mock_is_allowed_type.return_value = True
        mock_is_allowed_size.return_value = True
        mock_path_join.return_value = "certificates/dummy_file.pdf"
        mock_conn = mock_sqlite_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = None  # Simulate no existing user

        result = login.handle_file_upload("dummy_file.pdf", "test_user", "test_pass", "dummy@com")

        self.assertEqual(result, "File uploaded successfully. We'll review it and contact you shortly!")
        mock_is_allowed_type.assert_called_once_with("dummy_file.pdf")
        mock_is_allowed_size.assert_called_once_with("dummy_file.pdf")
        mock_makedirs.assert_called_once_with("certificates", exist_ok=True)
        mock_copyfile.assert_called_once_with("dummy_file.pdf", "certificates/dummy_file.pdf")
        mock_cursor.execute.assert_any_call(
            "INSERT INTO doctors (username, password, email, filename, certificate_file) VALUES (?, ?, ?, ?, ?)",
            ("test_user", "test_pass", "dummy@com", "dummy_file.pdf", "certificates/dummy_file.pdf")
        )

    @patch("Log_in_System.is_allowed_type")
    def test_invalid_file_type(self, mock_is_allowed_type):
        """
        Test invalid file type.
        """
        mock_is_allowed_type.return_value = False


        result = login.handle_file_upload("invalid_file.txt", "test_user", "test_pass", "dummy@com")


        self.assertEqual(result, "Invalid file type. Please upload a PDF, PNG, or JPG.")
        mock_is_allowed_type.assert_called_once_with("invalid_file.txt")

    @patch("Log_in_System.is_allowed_size")
    @patch("Log_in_System.is_allowed_type")
    def test_file_size_exceeds_limit(self, mock_is_allowed_type, mock_is_allowed_size):
        """
        Test invalid file size.
        """
        mock_is_allowed_type.return_value = True
        mock_is_allowed_size.return_value = False


        result = login.handle_file_upload("large_file.pdf", "test_user", "test_pass", "dummy@com")


        self.assertEqual(result, "File size exceeds 6MB. Please upload a smaller file.")
        mock_is_allowed_type.assert_called_once_with("large_file.pdf")
        mock_is_allowed_size.assert_called_once_with("large_file.pdf")

    @patch("sqlite3.connect")
    @patch("Log_in_System.is_allowed_size")
    @patch("Log_in_System.is_allowed_type")
    def test_username_already_registered(self, mock_is_allowed_type, mock_is_allowed_size, mock_sqlite_connect):
        """
        Test invalid username whic is already registered.
        """
        mock_is_allowed_type.return_value = True
        mock_is_allowed_size.return_value = True

        mock_conn = mock_sqlite_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = ("test_user",)  # Simulate existing user

        result = login.handle_file_upload("dummy_file.pdf", "test_user", "test_pass", "dummy@com")

        self.assertEqual(result, "Username 'test_user' is already registered. Please choose a different username.")
        mock_is_allowed_type.assert_called_once_with("dummy_file.pdf")
        mock_is_allowed_size.assert_called_once_with("dummy_file.pdf")
        mock_cursor.execute.assert_any_call("SELECT * FROM doctors WHERE username = ?", ("test_user",))


class TestSendMailFunction(unittest.TestCase):
    '''
    Class of unittest case for function of sending the verification email

    There is only one test case in this test class.
    '''

    @patch("Log_in_System.requests.post") # Mock replace the post request in Log_in_System
    def test_send_mail_success(self, mock_post):
        '''
        Test case for function of sending the verification email

         This test ensures the functionality of the `send_mail` function by using a mock post request
        to replace the actual API request. This approach avoids dependencies on external services, ensuring
        the test is isolated and reliable. This function test if a verification code is generated, and confirm
        the generated code falls within the range of [300, 500].
        '''
        # mock_post.return_value.status_code = 200 # this code is redundant for current function.
        # Previously the sending email function check the status_code of request == 200 and now it only check the
        # return value of method raise_for_status
        mock_post.return_value.raise_for_status = lambda: None
        # lambda: None represents a simple function that does nothing and simply exists.
        # It is used to replace the real raise_for_status() method.

        tomail = "fake@email.com"
        code = login.send_mail(tomail)
        print(code)

        self.assertIsNotNone(code, "Verification code should not be None")
        # we defined the range of verification code is (300,500)
        self.assertGreaterEqual(code, 300, "Verification code should be >= 300")
        self.assertLessEqual(code, 500, "Verification code should be <= 500")


class TestVerifyEmail(unittest.TestCase):
    '''
    Tests for functionality of verify code and the UI components of verification_code window
    '''
    @patch('Log_in_System.send_mail')  # Correctly mock the send_mail function
    def test_successful_verification(self, mock_send_mail):
        '''
            Half-automated test for the verify_email function, which requires manual interaction to input the verification code.

            This test uses mock to simulate the `send_mail` function's behavior by returning a fixed verification code (1234).
            The `verify_email` function is then called, and we manually input the correct code (1234) during the test execution.
            If the correct code is entered, the test passes. I didn't find a way to mock the click action of the button "verify",
            and the checking code action can only be conducted after click that button.
            '''
        mock_send_mail.return_value = 1234

        result = login.verify_email("test@example.com")
        mock_send_mail.assert_called_once_with("test@example.com")
        self.assertTrue(result, "The function should return True when the correct verification code is sent.")
    @patch("tkinter.Toplevel")
    @patch("tkinter.Label")
    @patch("tkinter.Entry")
    @patch("tkinter.Button")
    @patch("tkinter.messagebox.showinfo")
    @patch("Log_in_System.send_mail")
    def test_verify_email_components(
        self, mock_send_mail, mock_showinfo, mock_button, mock_entry, mock_label, mock_toplevel
    ):
        """
        Test that all the components are created correctly in 'verify_email'.
        """
        # Mock the send_mail function
        mock_send_mail.return_value = "12345"  # Mock the verification code
        mock_window = MagicMock()
        mock_toplevel.return_value = mock_window

        # Call the function
        login.verify_email("dummy@com")


        mock_toplevel.assert_called_once_with()
        self.assertTrue(mock_toplevel.called)
        mock_label.assert_any_call(mock_window, text="Enter Verification Code:")
        self.assertTrue(mock_label.called)
        mock_entry.assert_called_once_with(mock_window)
        self.assertTrue(mock_entry.called)
        mock_button.assert_any_call(mock_window, text="Verify", command=ANY)
        self.assertTrue(mock_button.called)
        mock_showinfo.assert_called_once_with(
            'Email Sent', 'A verification code has been sent to your email address.'
        )


# below are the old version tests for login function where stub functions are used
# Because the original functions ( 'is_allowed_type', 'is_allowed_size','upload_file') interact with GUI and is difficult
# to conduct fully automated tests, so I Create helper functions that replicate the core logic of these functions

# below are stub functions
# def is_allowed_type(file_path):
#     """Helper function: Validate file type."""
#     allowed_extensions = (".pdf", ".png", ".jpg")
#     return file_path.endswith(allowed_extensions)
#
# def is_allowed_size(file_path):
#     """Helper function: Validate file size."""
#     max_size = 6 * 1024 * 1024  # 6 MB
#     return os.path.getsize(file_path) <= max_size
#
# def insert_file_into_db_stub(username, password, email, file_path, db_path="test_register_doctor.db"):
#     """Helper function: Simulate database insertion logic."""
#
#     if not is_allowed_type(file_path):
#         print(f"Invalid file type for {file_path}. Allowed types are: .pdf, .png, .jpg.")
#         return False
#
#         # Validate file size
#     if not is_allowed_size(file_path):
#         print(f"File size exceeds 6 MB for {file_path}.")
#         return False
#
#     try:
#         conn = sqlite3.connect(db_path)
#         c = conn.cursor()
#         with open(file_path, "rb") as f:
#             file_data = f.read()
#         c.execute(
#             "INSERT INTO doctors (username, password, email, filename, certificate_file) VALUES (?, ?, ?, ?, ?)",
#             (username, password, email, os.path.basename(file_path), file_data)
#         )
#         conn.commit()
#         conn.close()
#         return True
#     except Exception as e:
#         print(f"Error inserting file into database: {e}")
#         return False
#
# class TestFileUploadLogic(unittest.TestCase):
#     '''
#     This class contains tests for three helper functions: is_allowed_type, is_allowed_size, insert_file_into_db_stub.
#     '''
#     def setUp(self):
#         """Create a test database and test files for test use."""
#         # Create a test database
#         self.db_path = "test_register_doctor.db"
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS doctors (
#                 username TEXT,
#                 password TEXT,
#                 email TEXT,
#                 filename TEXT,
#                 certificate_file BLOB
#             )
#         """)
#         conn.commit()
#         conn.close()
#
#         # Create test files
#         self.valid_file = "test_file.pdf"
#         with open(self.valid_file, "wb") as f:
#             f.write(b"test data")
#
#         self.invalid_file = "test_file.txt"
#         with open(self.invalid_file, "wb") as f:
#             f.write(b"test data")
#
#     def tearDown(self):
#         """Revome test database and test files after testing."""
#         if os.path.exists(self.db_path):
#             os.remove(self.db_path)
#         if os.path.exists(self.valid_file):
#             os.remove(self.valid_file)
#         if os.path.exists(self.invalid_file):
#             os.remove(self.invalid_file)
#
#     def test_is_allowed_type(self):
#         """
#         Test valid and invalid file types, and mutation detection.
#
#         This test applies black-box test, Negative Test, Mutation Testing
#         and Partition Testing.
#         - The txt files as negative case.
#         - The mutated implementation of is_allowed_type (allowing .txt as valid) is detected by the test
#         because it expects .txt files to be invalid.
#         - The partitioning file extensions are valid (.pdf, .png, .jpg) and invalid (.txt, no extensions, etc.) groups.
#         """
#         # Valid file types
#         self.assertTrue(is_allowed_type(self.valid_file), "Valid file type should return True")
#
#         # Invalid file types
#         self.assertFalse(is_allowed_type(self.invalid_file), "Invalid file type should return False")
#
#         # Mutation detection: `.txt` should fail
#         txt_file = "example.txt"
#         self.assertFalse(is_allowed_type(txt_file), "Files with '.txt' extension should return False")
#
#     def test_is_allowed_size_boundaries(self):
#         """
#         Test valid and invalid file sizes, including boundary cases.
#
#         This test applies black-box testing, Boundary Value Analysis, and Negative Testing.
#         - Boundary Value Analysis: Tests the exact size limit (6 MB) and slightly over the limit (6 MB + 1 byte).
#         - Negative Testing: The size out of limit are treated as invalid.
#         - Black-Box Testing: It focuses on inputs and outputs without concern for the internal implementations.
#
#         Validates:
#         - A file exactly 6 MB is allowed.
#         - A file slightly over 6 MB is rejected.
#         """
#         # Create boundary files
#         exactly_6mb = "test_file_6mb.bin"
#         slightly_over_6mb = "test_file_6mb_plus.bin"
#         with open(exactly_6mb, "wb") as f:
#             f.write(b"a" * (6 * 1024 * 1024))  # Exactly 6 MB
#         with open(slightly_over_6mb, "wb") as f:
#             f.write(b"a" * (6 * 1024 * 1024 + 1))  # Slightly over 6 MB
#
#         try:
#             self.assertTrue(is_allowed_size(exactly_6mb))
#             self.assertFalse(is_allowed_size(slightly_over_6mb))
#         finally:
#             os.remove(exactly_6mb)
#             os.remove(slightly_over_6mb)
#
#     # the following two tests can be seen as Partitioning test strategy when put them together
#     # Two partitions: valid file, invalid file
#     def test_insert_file_into_db(self):
#         """
#         Test inserting a valid file into the database.
#
#         This test applies black-box testing and Positive Testing.
#         - Black-Box Testing: It focuses on inputs and expected outputs (database insertion successful).
#         - Positive Testing: It ensures valid inputs result in correct database behavior.
#         """
#         result = insert_file_into_db_stub(
#             "test_user", "test_pass", "test_email@example.com", self.valid_file, self.db_path
#         )
#         self.assertTrue(result)
#
#         # velidate database entries
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM doctors WHERE username = ?", ("test_user",))
#         row = cursor.fetchone()
#         conn.close()
#
#         self.assertIsNotNone(row)
#         self.assertEqual(row[0], "test_user")
#         self.assertEqual(row[1], "test_pass")
#         self.assertEqual(row[2], "test_email@example.com")
#         self.assertEqual(row[3], "test_file.pdf")
#
#     def test_insert_invalid_file(self):
#         """
#         Test inserting an invalid file.
#
#         This test applies black-box testing and Negative Testing.
#         - Black-Box Testing: It verifies the database's ability to handle input without considering internal implementation.
#         - Negative Testing: It Checks that an invalid file can not be inserted.
#         """
#         result = insert_file_into_db_stub(
#             "test_user", "test_pass", "test_email@example.com", self.invalid_file, self.db_path
#         )
#         self.assertFalse(result)
#
#
#     # Minimal Testing for GUI: Since GUI elements are harder to test, I perform a very basic
#     # test to ensure the function doesn’t raise unexpected exceptions when run:
#     def test_uploadFileWindow_does_not_crash(self):
#         """Test that the uploadFileWindow function initializes without errors."""
#         username, password, email = "test_user", "test_pass", "test_email@example.com"
#         try:
#             login.uploadFileWindow(username, password, email)
#         except Exception as e:
#             self.fail(f"uploadFileWindow raised an exception: {e}")

class TestUsrSignUp(unittest.TestCase):
    """
    This class tests the `usr_sign_up` function using white-box and black-box testing approaches.
    """

    @patch("tkinter.Toplevel")  # Mock the Toplevel class to avoid GUI creation
    def test_usr_sign_up_window_creation(self, mock_toplevel):
        """
        Test that the sign-up window is created without errors and includes expected components.
        """
        try:
            login.usr_sign_up()
        except Exception as e:
            self.fail(f"usr_sign_up raised an exception: {e}")

        # Ensure Toplevel is called once
        self.assertEqual(mock_toplevel.call_count, 1, "Toplevel should be called once for sign-up.")

    @patch("Log_in_System.tk.messagebox.showerror")
    @patch("Log_in_System.tk.StringVar")
    @patch("Log_in_System.tk.Button")
    @patch("Log_in_System.tk.Toplevel")
    @patch("Log_in_System.sqlite3.connect")
    def test_username_already_exists(self, mock_connect, mock_toplevel, mock_button, mock_stringvar, mock_showerror):
        """
        Test sign-up when the username already exists in the database.
        """
        # Mock tk.StringVar to simulate user inputs
        mock_name = MagicMock()
        mock_name.get.return_value = "existing_user"
        mock_email = MagicMock()
        mock_email.get.return_value = "test@example.com"
        mock_pwd = MagicMock()
        mock_pwd.get.return_value = "password123"
        mock_pwd_confirm = MagicMock()
        mock_pwd_confirm.get.return_value = "password123"

        # Side effects for each StringVar instance
        mock_stringvar.side_effect = [mock_name, mock_email, mock_pwd, mock_pwd_confirm]

        # Mock the Toplevel window
        mock_window = MagicMock()
        mock_toplevel.return_value = mock_window

        # Mock the Button creation
        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        # Mock the database cursor to simulate the username existing
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("existing_user",)

        # Call the usr_sign_up function
        login.usr_sign_up()

        # Extract the `command` attribute from the Button instance
        command = mock_button.call_args[1]["command"]

        # Execute the command to simulate the button click
        command()

        # Validate that the error message is displayed
        mock_showerror.assert_called_once_with("Error", "Username already exists")

    @patch("Log_in_System.tk.messagebox.showerror")
    @patch("Log_in_System.tk.StringVar")
    @patch("Log_in_System.tk.Button")
    @patch("Log_in_System.tk.Toplevel")
    @patch("Log_in_System.sqlite3.connect")
    def test_empty_username_password_email(self, mock_connect, mock_toplevel, mock_button, mock_stringvar, mock_showerror):
        """
        Test sign-up with empty username, password, or email fields.
        """
        # Mock tk.StringVar to simulate empty input fields
        mock_name = MagicMock()
        mock_name.get.return_value = ""
        mock_email = MagicMock()
        mock_email.get.return_value = ""
        mock_pwd = MagicMock()
        mock_pwd.get.return_value = ""
        mock_pwd_confirm = MagicMock()
        mock_pwd_confirm.get.return_value = ""

        # Side effects for each StringVar instance in the function
        mock_stringvar.side_effect = [mock_name, mock_email, mock_pwd, mock_pwd_confirm]

        # Mock the Toplevel window
        mock_window = MagicMock()
        mock_toplevel.return_value = mock_window

        # Mock the Button creation and track the `command` function
        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        # Mock the database cursor and its behavior
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Simulate no username exists in the database

        # Call the usr_sign_up function
        login.usr_sign_up()

        # Extract the `command` attribute from the Button instance
        command = mock_button.call_args[1]["command"]

        # Execute the command to simulate the button click
        command()

        # Validate that the error message is displayed
        mock_showerror.assert_called_once_with("Error", "Username, password or email is empty")

    @patch("Log_in_System.tk.messagebox.showerror")
    @patch("Log_in_System.tk.StringVar")
    @patch("Log_in_System.tk.Button")
    @patch("Log_in_System.tk.Toplevel")
    @patch("Log_in_System.sqlite3.connect")
    def test_passwords_do_not_match(self, mock_connect, mock_toplevel, mock_button, mock_stringvar, mock_showerror):
        """
        Test sign-up when the passwords do not match.
        """
        # Mock tk.StringVar to simulate user inputs
        mock_name = MagicMock()
        mock_name.get.return_value = "new_user"
        mock_email = MagicMock()
        mock_email.get.return_value = "test@example.com"
        mock_pwd = MagicMock()
        mock_pwd.get.return_value = "password123"
        mock_pwd_confirm = MagicMock()
        mock_pwd_confirm.get.return_value = "different_password"

        # Side effects for each StringVar instance
        mock_stringvar.side_effect = [mock_name, mock_email, mock_pwd, mock_pwd_confirm]

        # Mock the Toplevel window
        mock_window = MagicMock()
        mock_toplevel.return_value = mock_window

        # Mock the Button creation
        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        # Mock the database cursor to simulate no username conflict
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        # Call the usr_sign_up function
        login.usr_sign_up()

        # Extract the `command` attribute from the Button instance
        command = mock_button.call_args[1]["command"]

        # Execute the command to simulate the button click
        command()

        # Validate that the error message is displayed
        mock_showerror.assert_called_once_with("Error", "Passwords do not match")

class TestOpenRoleSelection(unittest.TestCase):
    @patch("tkinter.Toplevel")
    @patch("Log_in_System.usr_sign_up")
    def test_open_role_selection_runs(self, mock_usr_sign_up, mock_toplevel):
        """
        Test that open_role_selection runs without errors and opens a new window.
        """
        try:
            login.open_role_selection()
        except Exception as e:
            self.fail(f"open_role_selection raised an exception: {e}")

        # Verify Toplevel is called once
        self.assertEqual(mock_toplevel.call_count, 1, "Toplevel should be called once.")

    @patch("tkinter.Toplevel")
    def test_open_role_selection_buttons(self, mock_toplevel):
        """
        Test that the role selection window includes buttons for 'Patient', 'Doctor', and 'Cancel'.
        """
        # Simulate widgets in the Toplevel
        mock_patient_button = MagicMock()
        mock_patient_button.cget.side_effect = lambda attr: {"text": "Patient Version"}.get(attr)
        mock_doctor_button = MagicMock()
        mock_doctor_button.cget.side_effect = lambda attr: {"text": "Doctor Version"}.get(attr)
        mock_cancel_button = MagicMock()
        mock_cancel_button.cget.side_effect = lambda attr: {"text": "Cancel"}.get(attr)

        mock_window = MagicMock()
        mock_window.winfo_children.return_value = [mock_patient_button, mock_doctor_button, mock_cancel_button]
        mock_toplevel.return_value = mock_window

        # Run the function
        login.open_role_selection()

        # Check button text
        buttons = mock_window.winfo_children()
        button_texts = [btn.cget("text") for btn in buttons]

        self.assertIn("Patient Version", button_texts, "'Patient Version' button is missing.")
        self.assertIn("Doctor Version", button_texts, "'Doctor Version' button is missing.")
        self.assertIn("Cancel", button_texts, "'Cancel' button is missing.")

    @patch("tkinter.Toplevel")
    def test_open_role_selection_cancel(self, mock_toplevel):
        # Simulate canceling role selection
        with patch.dict('Log_in_System.__dict__', {'chosen_role': None}):
            login.open_role_selection()
            # Ensure no role was chosen after canceling
            self.assertEqual(login.chosen_role, None)

class TestOpenForgotPasswordWindow(unittest.TestCase):
    @patch("tkinter.Toplevel")
    def test_open_forgot_password_window_runs(self, mock_toplevel):
        """
        Test that open_forgot_password_window runs without errors.
        """
        try:
            login.open_forgot_password_window()
        except Exception as e:
            self.fail(f"open_forgot_password_window raised an exception: {e}")

        self.assertEqual(mock_toplevel.call_count, 1, "Toplevel should be called once.")

    @patch("Log_in_System.tk.messagebox.showinfo")
    @patch("Log_in_System.tk.StringVar")
    @patch("Log_in_System.tk.Button")
    @patch("Log_in_System.tk.Toplevel")
    @patch("Log_in_System.sqlite3.connect")
    def test_successful_password_reset(self, mock_connect, mock_toplevel, mock_button, mock_stringvar, mock_showinfo):
        """
        Test that resetting password with correct information succeeds.
        """
        # Mock tk.StringVar to simulate user inputs
        mock_username = MagicMock()
        mock_username.get.return_value = "existing_user"
        mock_password = MagicMock()
        mock_password.get.return_value = "new_password"
        mock_email = MagicMock()
        mock_email.get.return_value = "test@example.com"

        # Mock the side effects for StringVar
        mock_stringvar.side_effect = [mock_username, mock_password, mock_email]

        # Mock the database connection and cursor
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("existing_user", "old_password", "test@example.com")

        # Mock the Toplevel window
        mock_window = MagicMock()
        mock_toplevel.return_value = mock_window

        # Mock the Confirm button and attach `reset_password` function
        def mock_button_init(*args, **kwargs):
            if 'command' in kwargs:
                kwargs['command']()
            return MagicMock()

        mock_button.side_effect = mock_button_init

        # Call the forgot password function
        login.open_forgot_password_window()

        # Validate that the SELECT and UPDATE queries were executed
        expected_calls = [
            call("SELECT * FROM users WHERE User_name = ?", ("existing_user",)),
            call("UPDATE users SET Password = ? WHERE User_name = ?", ("new_password", "existing_user")),
        ]
        mock_cursor.execute.assert_has_calls(expected_calls)

        # Validate that feedback is provided to the user
        mock_showinfo.assert_called_once_with(
            title='Reset Password',
            message="Your new password has been successfully set!"
        )



if __name__ == "__main__":
    # test_init_db()
    unittest.main()

