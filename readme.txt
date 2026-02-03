Psybridge - Mental Health Resource Management Tool
Course Project | Leiden University | January 2025
This is a group project completed by 6 second-year students at Leiden University for the Software Development course.

Team Members (Group 8)

David Xu Hu
Jixuan Yao
Joris Nouwens
Jingbo Li
Marit Paul
Piotrek Lichota

1.Overview
1.1 This software is designed with the following components:

Login System: The starting point of the application, launched via main.py.
Patient Interface: Provides functionalities for patients to interact with the system.
Doctor Interface: Allows doctors to manage their tasks and interact with the system.
Scheduling System: Handles appointment and schedule management.
Questionnaire Interface: Integrated within both the Patient Interface and Doctor Interface.

1.2 Key Features

Role-based login system (Patient/Doctor/Administrator)
Appointment scheduling system
Psychiatric questionnaire management (HCL-32, SDS scales)
AI chatbot integration (ChatGPT-4.0) for patient support
Secure data storage with SQLite database
Email verification system

1.3 Tech Stack

Language: Python
GUI: Tkinter
Database: SQLite
APIs: OpenAI API, LuckyColaAI (email service)
Development: Git version control

2. Contents
2.1 This folder includes:

Source code for the above-mentioned interfaces.
Two pre-configured databases used by the software.
SQL Script to create and database.
Unittest scripts for testing each interface.
The ER diagram and database structure.
A certificates folder containing images of certificates uploaded by doctors during registration.
Gitlog of all version control activities for tracking development history.


3. To run the software:
3.1 Execute the main.py file. This will initialize the application, starting with the Login System.

3.2 If you want to log in, you can use the following predefined accounts and passwords:

Patient account
Username: EvansJ
Password: 0000

Doctor account
Username: WatsonB
Password: 0000

Admin account
Username: BrooksK
Password: 0000

4. Dependencies
4.1 Ensure the following Python libraries are installed to run the software:

Tkinter
requests
tkPDFViewer2
openai

You can install any missing libraries using pip:
pip install <library-name>


4.2 Libraries Already Included in Python
You do not need to install the following because they are part of Python's standard library:

random
os
datetime
re
hashlib
sqlite3
shutil
webbrowser
