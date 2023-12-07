import sqlite3
connection = sqlite3.connect("users_database.db")

cursor = connection.cursor()
#cursor.execute("""DROP TABLE schedule""")

cursor.execute("CREATE TABLE IF NOT EXISTS schedule (schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,day TEXT, start_time TEXT, end_time TEXT,student_id INTEGER,job_id INTEGER, FOREIGN KEY (student_id) REFERENCES users(id),FOREIGN KEY (job_id) REFERENCES job_posts(job_id))")
'''
create_table_query = 
CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT,
    student_name TEXT,
    job_start TEXT,
    job_end TEXT,
    student_start TEXT,
    student_end TEXT
);

cursor.execute(create_table_query)

'''


'''
cursor.execute("""
CREATE TABLE notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    id_job INTEGER,
    title_job TEXT,
    message TEXT,
    duration_of_job TEXT,
    work_location TEXT,
    confirm INTEGER,
    current_date DATE,
    end_date DATE,         
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (id_job) REFERENCES job_posts(job_id),
    FOREIGN KEY (title_job) REFERENCES job_posts(job_title),
    FOREIGN KEY (duration_of_job) REFERENCES job_posts(job_duration),
    FOREIGN KEY (work_location) REFERENCES job_posts(work_location)
)
""")
'''


#cursor.execute("""
#CREATE TABLE notifications (
#    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
#    user_id INTEGER,
#    job_id INTEGER,
#    job_title TEXT,
#    message TEXT,
#    job_duration TEXT,
#    confirm INTEGER,
#    FOREIGN KEY (user_id) REFERENCES users(id),
#    FOREIGN KEY (job_id) REFERENCES job_posts(job_id),
#    FOREIGN KEY (job_title) REFERENCES job_posts(job_title),
#    FOREIGN KEY (job_duration) REFERENCES job_posts(job_duration)
#)
#""")

#cursor.execute("INSERT INTO users VALUES ('2005892', 'Aa@12345', 'Ranya Alghamdi', '2005892@uj.edu.sa', 'student')")
#cursor.execute("INSERT INTO users VALUES ('1905480', 'Aa@12346', 'Manar Eyad', '1905480@uj.edu.sa', 'student')")
#cursor.execute("INSERT INTO users VALUES ('1905453', 'Aa@12347', 'Sumaia Ahmed', '1905453@uj.edu.sa', 'student')")
#cursor.execute("INSERT INTO users VALUES ('2006786', 'Aa@12348', 'Raneem Aljadani', '2006786@uj.edu.sa', 'student')")
#cursor.execute("INSERT INTO users VALUES ('4514542', 'Aa@12349', 'ELHAM ALGAMDI', '4514542@uj.edu.sa', 'employee')")
#cursor.execute("INSERT INTO users VALUES ('4514534', 'Aa@12340', 'AHHLAM MOHAMMED', '4514534@uj.edu.sa', 'employee')")


#cursor.execute("""
#CREATE TABLE job_posts (
 #   job_id INTEGER PRIMARY KEY AUTOINCREMENT,
  #  user_id INTEGER,
   # job_title TEXT,
   # required_major TEXT,
    #min_gpa REAL,
#    skills TEXT,
 #   working_hours INTEGER,
  #  job_duration TEXT,
  #  positions_available INTEGER,
   # FOREIGN KEY (user_id) REFERENCES users(id)
#)
#""")

'''
cursor.execute("""
CREATE TABLE job_times (
    job_time_id INTEGER PRIMARY KEY AUTOINCREMENT,
    time_id INTEGER,
    fixed_flexible TEXT,
    flexible_hours INTEGER
    sunday_job_periods INTEGER,
    sunday_start TEXT,
    sunday_end TEXT,
    monday_job_periods INTEGER,
    monday_start TEXT,
    monday_end TEXT,
    tuesdayـjob_periods INTEGER,
    tuesday_start TEXT,
    tuesday_end TEXT,
    wednesday_job_periods INTEGER,
    wednesday_start TEXT,
    wednesday_end TEXT,
    thursday_job_periods INTEGER,
    thursday_start TEXT,
    thursday_end TEXT,
    FOREIGN KEY (time_id) REFERENCES job_posts(job_id)
)""")
'''

#cursor.execute("""
#CREATE TABLE files (
 #   id INTEGER PRIMARY KEY AUTOINCREMENT,
 #   user_id INTEGER,
 #   data BLOB,
 #   FOREIGN KEY (user_id) REFERENCES users(id)
#)
#""")

''' 
import random

# List of Arabic female first names in English
arabic_first_names = [
    "Sara", "Layla", "Fatima", "Aisha", "Zahra",
    "Noura", "Maha", "Samar", "Rana", "Salma",
    "Mariam", "Hala", "Yara", "Lina", "Rania",
    "Amira", "Dina", "Maya", "Hadeel", "Jana",
    "Farah", "Nadia", "Reem", "Joud", "Dalal",
    "Leila", "Noor", "Huda", "Safia", "Amina",
    "Riham", "Dalia", "Rima", "Mona", "Sawsan",
    "Wafa", "Najla", "Ghada", "Maha", "Laila",
    "Hayat", "Zainab", "Asma", "Hanan", "Amani",
    "Nada", "Saida", "Jawaher", "Rawan", "Maram",
    "Abeer", "Samira", "Rasha", "Razan", "Sahar",
    "Fatima", "Warda", "Shaima", "Hind", "Maha",
    "Raneem", "Manar"
    # Add more first names here
]

# List of Arabic female last names in English
arabic_last_names = [
    "Khaled", "Ahmed", "Hassan", "Mohammed", "Ali",
    "Abdullah", "Khalid", "Hassan", "Ahmed", "Mohammed",
    "Ibrahim", "Saleh", "Omar", "Mahmoud", "Hamza",
    "Saad", "Kamal", "Mahmoud", "Ali", "Hassan",
    "Abbas", "Jaber", "Rashid", "Saeed", "Tarabulsi",
    "Salem", "Rahman", "Nasser", "Sharif", "Farouk",
    "Hamid", "Hussein", "Saeed", "Hadi", "Khalifa",
    "Qasim", "Mansour", "Mahdi", "Karim", "Sultan"
    # Add more last names here
]

# Generate 200 records
for i in range(196):
    id = '2040' + str(i + 1).zfill(3)  # Generate unique ID with length 7
    password = ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(8))  # Generate a random password
    first_name = random.choice(arabic_first_names)  # Select a random Arabic female first name
    last_name = random.choice(arabic_last_names)  # Select a random Arabic female last name
    name = first_name + " " + last_name  # Combine the first name and last name
    email = id + "@uj.edu.sa"  # Generate email based on the ID
    user_type = "student"  # Set the type of user
    
    query = "INSERT INTO users VALUES ('{}', '{}', '{}', '{}', '{}')".format(id, password, name, email, user_type)
    cursor.execute(query)
'''

connection.commit()
