#Basic unittest:
import tkinter
#Check if back_button is frozen
#Check if a booked appointment is removed from available appointments and added to the booked appointments
#check if patient interface is hidden after launching scheduling system and vice versa
#check if an appointment window appears after double clicking with details
#check with nothing happens after clicking table headings and "nothing" area
#check if (initially) every quarter of time between 9-17 exists
#check if "book an appointment" button loads the available appointments page
#check if "your appointments" button loads the booked appointments page

import unittest
import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock, patch

import patient_interface as pi
import scheduling_system as ss
from scheduling_system_old import main
info_dict = {"doctor_name":("Jack","Strong"), "first_name":"John", "last_name":"Smith"}
info_dict2 = {"doctor_name":("Jack","Strong"), "first_name":"John", "last_name":"Smith"}


class TestStringMethods(unittest.TestCase):
    #root = tk.Tk()
    #x = main(info_dict, root, 1)
    '''
    (available_appointments, booked_appointments, back_button, back_button2,
 empty_message1, empty_message2, old_root, inter_root, is_doctor,
 full_name, user_dictionary) = None, None, None, None, None, None, None, None, 0, "", {"doctor_name": ("Test", "Doctor")}
    '''
    def test_global_initialization(self):
        self.assertIsNone(ss.available_appointments)

    def test_startpage_existence(self):
        self.assertIsNotNone(ss.StartPage(None, None))
    def test_ondoubleclick_window(self): #fails
        #root = tk.Tk()
        obj = ss.AppointmentList(None, None) #container - tk.frame, controller -
        print(obj.double_click)


    def test_mainclass_existence(self):
        self.assertIsNotNone(ss.Mainclass())

    def test_appointmentlist_existence(self):
        self.assertIsNotNone(ss.AppointmentList(None, None))

    def test_appointmentbook_exists(self):#fails
        # Create an instance of MyClass
        obj = ss.AppointmentList(None, None)

        # Check if the 'my_function' exists in the object
        self.assertTrue(hasattr(obj, 'AppointmentBook'), "Function 'my_function' does not exist")
    def test_confirmation_exists(self):
        # Create an instance of MyClass
        obj = ss.Schedule(None, None)
        # Check if the 'my_function' exists in the object
        self.assertTrue(hasattr(obj, 'Confirmation'), "Function 'my_function' does not exist")
    def test_backbutton_exists(self):
        # Create an instance of MyClass
        obj = ss.Schedule(None, None)
        # Check if the 'my_function' exists in the object
        self.assertIsNotNone(obj.go_back_button)
    def test_schedule_widgets_patient(self):
        # Create an instance of MyClass
        ss.is_doctor=0
        obj = ss.Schedule(None, None)
        # Check if the 'my_function' exists in the object
        widgets=obj.children
        self.assertIsNotNone(widgets)
        for w in widgets:
            self.assertIsNotNone(w)
        self.assertEqual(len(widgets),4)
        self.assertEqual(len(widgets), 4)
        self.assertIsInstance(widgets['!label'], tk.Label)
        self.assertIsInstance(widgets['!treeview'], ttk.Treeview)
        self.assertIsInstance(widgets['!scrollbar'], ttk.Scrollbar)
        self.assertIsInstance(widgets['!button'], tk.Button)
    def test_schedule_widgets_doctor(self):
        # Create an instance of MyClass
        ss.is_doctor=1
        obj2 = ss.Schedule(None, None)
        # Check if the 'my_function' exists in the object
        widgets2=obj2.children
        self.assertIsNotNone(widgets2)

        for i in widgets2:
            self.assertIsNotNone(i)
        self.assertEqual(len(widgets2),4)
        self.assertIsInstance(widgets2['!label'], tk.Label)
        self.assertIsInstance(widgets2['!treeview'], ttk.Treeview)
        self.assertIsInstance(widgets2['!scrollbar'], ttk.Scrollbar)
        self.assertIsInstance(widgets2['!button'], tk.Button)

    def test_startpage_widgets_doctor(self):
        # Create an instance of MyClass
        ss.is_doctor=1
        obj = ss.StartPage(None, None)
        # Check if the 'my_function' exists in the object
        widgets=obj.children
        self.assertIsNotNone(widgets)
        for i in widgets:
            self.assertIsNotNone(i)
        self.assertEqual(len(widgets),3)
        self.assertIsInstance(widgets['!label'], tk.Label)
        self.assertIsInstance(widgets['!button'], tk.Button)
        self.assertIsInstance(widgets['!button2'], tk.Button)


    def test_startpage_widgets_patient(self):
        # Create an instance of MyClass
        ss.is_doctor=0
        obj = ss.StartPage(None, None)
        # Check if the 'my_function' exists in the object
        widgets=obj.children
        self.assertIsNotNone(widgets)
        for i in widgets:
            self.assertIsNotNone(i)
        self.assertEqual(len(widgets),4)
        self.assertIsInstance(widgets['!label'], tk.Label)
        self.assertIsInstance(widgets['!button'], tk.Button)
        self.assertIsInstance(widgets['!button2'], tk.Button)
        self.assertIsInstance(widgets['!button3'], tk.Button)
    def test_appointmentlist_widgets_patient(self):
        # Create an instance of MyClass
        ss.is_doctor=0
        obj = ss.AppointmentList(None, None)
        # Check if the 'my_function' exists in the object
        widgets=obj.children
        self.assertIsNotNone(widgets)
        for i in widgets:
            self.assertIsNotNone(i)
        print(widgets)
        self.assertEqual(len(widgets),4)
        self.assertIsInstance(widgets['!label'], tk.Label)
        self.assertIsInstance(widgets['!treeview'], ttk.Treeview)
        self.assertIsInstance(widgets['!scrollbar'], ttk.Scrollbar)
        self.assertIsInstance(widgets['!button'], tk.Button)


    def test_deletion_exists(self):
        # Create an instance of MyClass
        obj = ss.Schedule(None, None)
        # Check if the 'my_function' exists in the object
        self.assertTrue(hasattr(obj, 'Deletion'), "Function 'my_function' does not exist")
    '''
    def test_deletion_exists(self):
        # Create an instance of MyClass
        obj = ss.Schedule(None, None)
    '''

    def test_showframe_exists(self):
        # Create an instance of MyClass
        obj = ss.Mainclass()
        # Check if the 'my_function' exists in the object
        self.assertTrue(hasattr(obj, 'show_frame'), "Function 'my_function' does not exist")
    def test_recover_root_exists(self):
        # Create an instance of MyClass
        # Check if the 'my_function' exists in the object
        self.assertTrue(hasattr(ss, 'recover_root'), "Function 'my_function' does not exist")
    def test_onclose_exists(self):
        # Create an instance of MyClass
        # Check if the 'my_function' exists in the object
        self.assertTrue(hasattr(ss, 'on_close'), "Function 'my_function' does not exist")

    def test_mainclass_frames(self):#fails
        app = ss.Mainclass()

        ss.is_doctor=0
        self.assertEqual(len(ss.StartPage.children), 4)
    def test_schedule_label(self):
        ss.is_doctor = 1
        old_root = ss.Schedule(None, None)
        # Check that the frames dictionary is initialized
        self.assertIsNotNone(old_root.main_label)
        # Ensure the expected frames exist in the dictionary
        self.assertEqual(old_root.main_label.cget("text"), "List of appointments to confirm or modify")
        ss.is_doctor = 0
        old_root = ss.Schedule(None, None)
        # Check that the frames dictionary is initialized
        self.assertIsNotNone(old_root.main_label)
        # Ensure the expected frames exist in the dictionary
        self.assertEqual(old_root.main_label.cget("text"), "List of appointments booked by you")

    def test_doubleclick_exists(self):
        # Create an instance of MyClass
        # Check if the 'my_function' exists in the object
        self.assertTrue(hasattr(ss, 'OnDoubleClick'), "Function 'my_function' does not exist")
    def test_main_exists(self):
        # Create an instance of MyClass
        # Check if the 'my_function' exists in the object
        self.assertTrue(hasattr(ss, 'main'), "Function 'my_function' does not exist")
    def test_book_process(self):#fails
        #Mainclass() -> StartPage() -> AppointmentList() -> AppointmentBook
        root = tk.Tk()
        ss.available_appointments = ttk.Treeview(root)
        ss.available_appointments.pack()
        ss.booked_appointments = ttk.Treeview(root)
        ss.booked_appointments.pack()
        ss.booked_appointments.insert('', 'end', text="4", values=(
        '0000', 'Piotr Lichota', "01-01-2025", '14:30', 'Einsteinweg 55 - Leiden', 'No'))
        x = ss.AppointmentList(None, None)
        item = ss.available_appointments.selection_set(ss.available_appointments.get_children()[0])
        self.assertIsNotNone(x.AppointmentBook(item,root))
    def test_ondoubleclick_existence(self):#fails
        root = tk.Tk()
        ss.back_button = tk.Button(root, text="Yes")
        ss.available_appointments = ttk.Treeview(root)
        self.assertIsNotNone(ss.OnDoubleClick(None, None, 1))
    def test_patient_existence(self):
        self.assertTrue(hasattr(ss, 'Patient'), "Function 'my_function' does not exist")
        self.assertIsNotNone(ss.Patient("Piotr", "Lichota"))
    def test_doctor_existence(self):
        self.assertTrue(hasattr(ss, 'Doctor'), "Function 'my_function' does not exist")
        self.assertIsNotNone(ss.Doctor("Piotr", "Lichota"))
    def test_recover_root_existence(self):#fails
        root = tk.Tk()
        self.assertIsNotNone(ss.recover_root(root, root))

    def test_recover_root(self):#fails
        #win1, win2=tk.Tk(), tk.Tk()
        #win2.withdraw()
        root = tk.Tk()

        ss.recover_root(ss.old_root,pi.root)


    def test_mainclass_initialization(self):#fails
        app = ss.Mainclass()
        assert app is not None
        assert ss.StartPage in app.frames.keys()
        assert ss.AppointmentList in app.frames.keys()
        assert ss.Schedule in app.keys()

    def test_button_applist(self):
        app = ss.AppointmentList(None, None)  # filling available appointments
        self.assertIsNotNone(app.go_back_button)
    def test_values(self):
        app = ss.AppointmentList(None, None)

        self.assertEqual(app.label.cget("text"), "List of appointments available for booking")

    def test_initialize_patient(self):
        patient = ss.Patient("Piotr", "Lichota")
        self.assertEqual(patient.name, "Piotr")
        self.assertEqual(patient.surname, "Lichota")
        self.assertEqual(repr(patient), "Piotr Lichota")
    def test_schedule_existence(self):
        self.assertIsNotNone(ss.Schedule(None,None))
    def test_initialize_doctor(self):
        doctor = ss.Doctor("Piotr", "Lichota")
        self.assertEqual(doctor.name, "Piotr")
        self.assertEqual(doctor.surname, "Lichota")
        self.assertEqual(repr(doctor), "Piotr Lichota")


    def test_on_close(self):#fails
        win1, win2 = tk.Tk(), tk.Tk()
        ss.on_close(win1, win2, 0)
        self.assertFalse(win1.winfo_viewable())
    def test_destroy_label(self):
        win1 = tk.Tk()
        label = tk.Label(win1)
        label.pack()

        # Ensure label exists before destruction
        self.assertIn(label, win1.children.values())

        # Destroy the label
        ss.destroy_label(label)

        # Ensure label does not exist after destruction
        self.assertNotIn(label, win1.children.values())

    def test_stop_program(self):
        root2=tk.Tk()
        ss.stop_program(root2)

    def test_of_confirmation(self):
        #Schedule() -> Confirmation
        #def Confirmation(self, item, number, window)
        #number - boolean
        applist = ss.AppointmentList(None, None)
        children = ss.available_appointments.get_children()
        for child in children[1:]:
            ss.available_appointments.delete(child)
        booked = ss.Schedule(None, None)
        ss.empty_message2 = tk.Tk()
        print("Appointments: ", ss.available_appointments.get_children()[0])
        item = ss.available_appointments.get_children()[0]
        root, root2, root3 = tk.Tk(), tk.Tk(), tk.Tk()
        ss.user_dictionary = {"doctor_name": ("Jack", "Strong"), "first_name": "John", "last_name": "Smith"}
        applist.AppointmentBook(item, root) #an appointment is booked
        booked.Confirmation(item, 1, root2)
        self.assertEqual(ss.back_button2.cget('state'), tk.NORMAL)
        item_values = ss.booked_appointments.item(item, "values")
        temp_list = list(item_values)
        self.assertEqual(temp_list[-1], 'Yes')
        try:
            exists = root2.winfo_exists()
        except tk.TclError:
            exists = False

        self.assertFalse(exists)
        self.assertEqual(temp_list[-1], 'Yes')

        booked.Confirmation(item, 0, root3)
        item_values = ss.booked_appointments.item(item, "values")
        temp_list = list(item_values)
        self.assertEqual(temp_list[-1], 'No')

    def test_of_deletion(self):
        applist = ss.AppointmentList(None, None)
        children = ss.available_appointments.get_children()
        for child in children[1:]:
            ss.available_appointments.delete(child)
        booked = ss.Schedule(None, None)
        ss.empty_message2 = tk.Tk()
        print("Appointments: ", ss.available_appointments.get_children()[0])
        item = ss.available_appointments.get_children()[0]
        root, root2 = tk.Tk(), tk.Tk()
        ss.user_dictionary = {"doctor_name": ("Jack", "Strong"), "first_name": "John", "last_name": "Smith"}
        applist.AppointmentBook(item, root)
        self.assertEqual(len(ss.available_appointments.get_children()), 0)
        new_values = ss.booked_appointments.item(item, "values")
        modified_tuple = new_values[:-1]
        booked.Deletion(item, root2)
        self.assertEqual(len(ss.booked_appointments.get_children()), 0)

        self.assertIsNotNone(ss.empty_message2)
        ss.empty_message1=tk.Tk()
        try:
            exists = root2.winfo_exists()
        except tk.TclError:
            exists = False
        self.assertFalse(exists)
        self.assertEqual(ss.back_button2.cget('state'), tk.NORMAL)
        self.assertEqual(len(ss.available_appointments.get_children()), 1)

    def test_main_function(self):
        root_mock = MagicMock(spec=tk.Tk)
        root_mock2 = MagicMock(spec=tk.Tk)
        none_dict = {"doctor_name": (None, None), "first_name": None, "last_name": None}
        #old_root_mock = MagicMock(spec=tk.Tk)
        #classic_root=tk.Tk()
        # Mock global variables
        ss.start=0
        # Call the main function
        ss.main(info_dict, root_mock, 1)


        self.assertIsInstance(root_mock, MagicMock)  # Mock `Mainclass`
        self.assertEqual(ss.full_name, "John Smith")
        ss.main(info_dict, root_mock, 0)
        #self.assertEqual(ss.full_name, "John Smith")
        self.assertTrue(root_mock.winfo_ismapped())

        ss.main(none_dict, root_mock2, 0)

        #self.assertTrue(root_mock.mainloop.assert_called_once())
        with patch("scheduling_system.sys.exit", MagicMock()):

            ss.start = 1
            ss.old_root = None

            # Test when start is 1 and old_root is None
            ss.main(info_dict, root_mock, 0)




    def test_for_doubleclick(self):
        ss.is_doctor = 1
        applist = ss.AppointmentList(None, None)
        booked = ss.Schedule(None, None)
        window, window2=tk.Tk(), tk.Tk()
        ss.available_appointments.bind("<Double-1>", lambda event: ss.OnDoubleClick(event, window, 0))
        self.assertIsNotNone(ss.booked_appointments.bind("<Double-1>"))
        class FakeEvent():
            def __init__(self,x,y):
                self.x=x
                self.y=y
        region = FakeEvent(0,0)
        ss.OnDoubleClick(None, window, 0)
        self.assertNotEqual(region, "heading")
        self.assertIsNotNone(ss.OnDoubleClick(region, window, 0))
        self.assertIsNotNone(ss.double_window)

        ss.is_doctor = 0
        ss.double_window=None

        ss.OnDoubleClick(None, window, 0)







    def test_booking(self):#fails
        #Mainclass() -> StartPage() -> AppointmentList() -> AppointmentBook
        #AppointmentBook(self, item, window)
        #item - add an entry and select it, main app window
        #global back_button, available_appointments initialized with appointmentlist
        #global empty_message1, empty_message2, user_dictionary

        applist = ss.AppointmentList(None,None)
        children = ss.available_appointments.get_children()
        for child in children[1:]:
            ss.available_appointments.delete(child)
        booked = ss.Schedule(None,None)
        ss.empty_message2 = tk.Tk()




        #print("Dzieci: ", children)
        #applist.AppointmentBook(None,None)
        #applist.AppointmentBook()
        self.assertIsNotNone(ss.available_appointments)
        print("Appointments: ", ss.available_appointments.get_children()[0])
        item = ss.available_appointments.get_children()[0]
        self.assertIsNotNone(item)
        root = tk.Tk()
        self.assertIsNotNone(root)
        ss.user_dictionary = {"doctor_name":("Jack","Strong"), "first_name":"John", "last_name":"Smith"}
        applist.AppointmentBook(item, root)
        self.assertEqual(len(ss.available_appointments.get_children()), 0)
        self.assertIsNotNone(root)
        self.assertEqual(item, ss.booked_appointments.get_children()[-1])
        last_element_id = ss.booked_appointments.get_children()[-1]

        last_element_values = ss.booked_appointments.item(last_element_id, "values")[-1]
        self.assertEqual("No", last_element_values)
        self.assertEqual(ss.back_button.cget('state'), tk.NORMAL)
        #self.assertFalse(root.winfo_exists())
        try:
            exists = root.winfo_exists()
        except tk.TclError:
            exists = False

        self.assertFalse(exists)
        self.assertEqual(applist.go_back_button, ss.back_button)
        found_label = None
        new_values = ss.booked_appointments.item(last_element_id, "values")
        label_text = f"Appointment {new_values} booked succesfully. Now, wait upon a doctor confirmation."
        for widget in applist.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("text") == label_text:
                found_label = widget
                break

        self.assertIsNotNone(found_label, f"Label with text '{label_text}' was not found.")
        #print(found_label)
        print(found_label.pack_info())
        self.assertEqual(found_label.pack_info()['padx'], 20, "padx is not set correctly")
        self.assertEqual(found_label.pack_info()['pady'], 20, "pady is not set correctly")

        try:
            exists2 = ss.empty_message2.winfo_exists()
        except tk.TclError:
            exists2 = False

        self.assertFalse(exists2)

        self.assertIsNotNone(ss.empty_message1)
        #print("Empty msg2: ", ss.empty_message2.cget("text"))

        self.assertEqual(ss.empty_message1.pack_info()['padx'], 20, "padx is not set correctly")
        self.assertEqual(ss.empty_message1.pack_info()['pady'], 20, "pady is not set correctly")




if __name__=="__main__":  
    unittest.main()
