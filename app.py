from flask import Flask, request, redirect , flash, url_for,render_template, session,send_file,jsonify
import sqlite3
from io import BytesIO
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from datetime import date
from collections import namedtuple


#to save pdf file
import os 
if not os.path.exists('/tmp/'):
    os.makedirs('/tmp/')

TEMPLATES_AUTO_RELOAD = True

app = Flask(__name__)
app.secret_key = 'random string'


# Defines the fist route for homepage
@app.route('/')
def index():
   return render_template('index.html')

# Defines the secound route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        connection = sqlite3.connect("users_database.db")
        cursor = connection.cursor()
        
        user_id = request.form['id']
        password = request.form['password']

        cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ? AND password = ?", (user_id, password))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user[0] # Save user_id in session
            if user[2] == 'employee':
                return redirect(url_for("employee"))
            elif user[2] == 'student':
                return redirect(url_for('student'))  # Redirect to the student route
            else:
                flash("Position not recognized. Please try again.", 'error')
        else:
            flash("Sorry, incorrect login. Try again!", 'error')
            return render_template("login.html")
         
        connection.close()

    return render_template("login.html")

@app.route('/find_job',methods=['GET', 'POST'])
def find_job():
    if 'user_id' not in session:
        flash("You are not logged in. Please log in first.", 'error')
        return redirect(url_for("login"))

    user_id = session['user_id']

    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()
    
    if request.method == 'POST':

        name = request.form['name']
        phoneNumber = request.form['phoneNumber']
        languages = request.form.getlist('Languages')
        skills = request.form.getlist('skills')
        gpa = request.form['gpa']
        major = request.form['major']
        experience = request.form['experience']
        work_duration = request.form['work_duration']
        work_preference = request.form['work_preference']
        form_submission = True
        uploaded_file = request.files['pdf_file']    # Get the uploaded file
        print(uploaded_file)

        if  uploaded_file:
            # Save the file to a temporary location
            temp_path = '/tmp/' + uploaded_file.filename
            uploaded_file.save(temp_path)

            # Read the file data as binary
            with open(temp_path, 'rb') as file:
                file_data = file.read()

            # Delete the temporary file
            os.remove(temp_path)

            
        #--------------------------- Start interval data
        
        # Get the sunday interval data from the form
        sundayStarts = []
        sundayEnds = []
        sunday_periods = int(request.form.get('sunday-interval'))
        totalDuration = 0 
        for i in range(sunday_periods):
            #print("i== ",i)
            start_time = request.form.get('sunday-interval-start-time-' + str(i))
            end_time = request.form.get('sunday-interval-end-time-' + str(i))
            duration = calculate_duration(start_time, end_time)
            totalDuration += duration
            print('sunday: ',totalDuration)
            sundayStarts.append(start_time)
            sundayEnds.append(end_time)

        # Get the monday interval data from the form
        mondayStarts = []
        mondayEnds = []
        monday_periods = int(request.form.get('monday-interval'))
        for i in range(monday_periods):
            #print("i== ",i)
            start_time = request.form.get('monday-interval-start-time-' + str(i))
            end_time = request.form.get('monday-interval-end-time-' + str(i))
            duration = calculate_duration(start_time, end_time)
            totalDuration += duration
            print('monday: ',totalDuration)
            mondayStarts.append(start_time)
            mondayEnds.append(end_time)

        # Get the tuesday interval data from the form
        tuesdayStarts = []
        tuesdayEnds = []
        tuesdayـperiods = int(request.form.get('tuesday-interval'))
        for i in range(tuesdayـperiods):
            #print("i== ",i)
            start_time = request.form.get('tuesday-interval-start-time-' + str(i))
            end_time = request.form.get('tuesday-interval-end-time-' + str(i))
            duration = calculate_duration(start_time, end_time)
            totalDuration += duration
            print('tuesday: ',totalDuration)
            tuesdayStarts.append(start_time)
            tuesdayEnds.append(end_time)

        # Get the wednesday interval data from the form
        wednesdayStarts = []
        wednesdayEnds = []
        wednesday_periods = int(request.form.get('wednesday-interval'))
        for i in range(wednesday_periods):
            #print("i== ",i)
            start_time = request.form.get('wednesday-interval-start-time-' + str(i))
            end_time = request.form.get('wednesday-interval-end-time-' + str(i))
            duration = calculate_duration(start_time, end_time)
            totalDuration += duration
            print('wednesday: ',totalDuration)
            wednesdayStarts.append(start_time)
            wednesdayEnds.append(end_time)

        # Get the thursday interval data from the form
        thursdayStarts = []
        thursdayEnds = []
        thursday_periods = int(request.form.get('thursday-interval'))
        for i in range(thursday_periods):
            #print("i== ",i)
            start_time = request.form.get('thursday-interval-start-time-' + str(i))
            end_time = request.form.get('thursday-interval-end-time-' + str(i))
            duration = calculate_duration(start_time, end_time)
            totalDuration += duration
            print('thursday: ',totalDuration)
            thursdayStarts.append(start_time)
            thursdayEnds.append(end_time)
        
        #--------------------------- End interval data
        print(totalDuration)
        totalHoursDuration = convert_minutes_to_hours(totalDuration)
        cursor.execute("INSERT INTO seekers_form (user_id, form_submission, name, phoneNumber, languages, skills, gpa, major, experience, totalHours, sunday_periods,monday_periods,tuesdayـperiods,wednesday_periods,thursday_periods,sunday_start_interval,sunday_end_interval,monday_start_interval,monday_end_interval,tuesday_start_interval,tuesday_end_interval,wednesday_start_interval,wednesday_end_interval,thursday_start_interval,thursday_end_interval,work_duration,work_preference) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (user_id, form_submission, name, phoneNumber, ','.join(languages), ','.join(skills), gpa, major, experience, totalHoursDuration, sunday_periods,monday_periods,tuesdayـperiods,wednesday_periods,thursday_periods,','.join(map(str, sundayStarts)),','.join(map(str, sundayEnds)),','.join(map(str, mondayStarts)),','.join(map(str, mondayEnds)),','.join(map(str, tuesdayStarts)),','.join(map(str, tuesdayEnds)),','.join(map(str, wednesdayStarts)),','.join(map(str, wednesdayEnds)),','.join(map(str, thursdayStarts)),','.join(map(str, thursdayEnds)),work_duration,work_preference ))
        #form_id = cursor.lastrowid

        if  uploaded_file:
            cursor.execute('INSERT INTO files (user_id, filename, data) VALUES (?, ?, ?)',
                    ( user_id,uploaded_file.filename, file_data))

        connection.commit()
        connection.close()

        flash("Request was created successfully!", 'success')
        return redirect(url_for("student"))

    cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if user:
        return render_template('find_job.html', user=user)
    else:
        flash("User not found. Please log in again.", 'error')
        return redirect(url_for("login"))
def calculate_duration(start_time, end_time):
    # Step 1: Convert to 24-hour format
    start_time = convert_to_24_hour(start_time)
    end_time = convert_to_24_hour(end_time)

    # Step 2: Convert to minutes
    start_minutes = convert_to_minutes(start_time)
    end_minutes = convert_to_minutes(end_time)

    # Step 3: Calculate duration
    if end_minutes < start_minutes:
        end_minutes += 24 * 60  # Add 24 hours' worth of minutes

    duration_minutes = end_minutes - start_minutes

    return duration_minutes

def convert_to_24_hour(time_str):
    time_str = time_str.strip()  # Remove leading and trailing spaces
    hour, minute = map(int, time_str[:-3].split(':'))
    am_pm = time_str[-2:].lower()

    if am_pm == 'pm' and hour != 12:
        hour += 12

    return f'{hour:02d}:{minute:02d}'

def convert_to_minutes(time_str):
    hour, minute = map(int, time_str.split(':'))
    return hour * 60 + minute

def convert_minutes_to_hours(duration_minutes):
    hours = duration_minutes // 60
    minutes = duration_minutes % 60
    return hours



# Handle file download
@app.route('/download/<int:file_id>')
def download(file_id):
    # Retrieve the file data from the database based on the form_id
    conn = sqlite3.connect('users_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT filename, data FROM files WHERE file_id = ?', (file_id,))
    file = cursor.fetchone()
    conn.close()

    # Check if the file data exists
    if file is None:
        return 'File not found.'

    filename = file[0]
    file_data = file[1]
    file_obj = BytesIO(file_data)  # Create a file-like object from the file_data
    print(file_obj)

    # Send the file data as a response using send_file
    return send_file(file_obj, download_name=filename, as_attachment=True,mimetype='application/pdf')
    
if __name__ == "__main__":
   app.run(debug = True)

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if 'user_id' not in session:
        flash("You are not logged in. Please log in first.", 'error')
        return redirect(url_for("login"))
    
    user_id = session['user_id']
    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()
    
    if request.method == 'POST':
        job_title = request.form['job_title']
        required_major = request.form['required_major']
        min_gpa = request.form['min_gpa']
        skills = request.form.getlist('skills')
        #working_hours = request.form['working_hours']
        experience = request.form['experience']
        job_duration = request.form['job_duration']
        positions_available = request.form['positions_available']
        required_languages = request.form.getlist('required_languages')
        work_location = request.form['work_location']
        fixed_flexible = request.form['fixed-flexible']

        cursor.execute("INSERT INTO job_posts (user_id, job_title, required_major, min_gpa, skills, experience, job_duration, positions_available, required_languages,work_location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (user_id, job_title, required_major, min_gpa, ','.join(skills), experience, job_duration, positions_available, ','.join(required_languages),work_location))
        # Retrieve the reference key (last inserted row ID)
        reference_key = cursor.lastrowid

        if fixed_flexible == 'Flexible':
            flexible_hours = request.form['flexible_hours']

            cursor.execute("INSERT INTO job_times (time_id,fixed_flexible,flexible_hours) VALUES (?,?,?)",
                       (reference_key,fixed_flexible,flexible_hours))
        
        
        #--------------------------- Start interval data
        if fixed_flexible == 'Fixed':
            # Get the sunday interval data from the form
            sundayStarts = []
            sundayEnds = []
            sunday_periods = int(request.form.get('sunday-interval'))
            #totalDuration = 0 
            for i in range(sunday_periods):
                start_time = request.form.get('sunday-interval-start-time-' + str(i))
                end_time = request.form.get('sunday-interval-end-time-' + str(i))
                #duration = calculate_duration(start_time, end_time)
                #totalDuration += duration
                sundayStarts.append(start_time)
                sundayEnds.append(end_time)

            # Get the monday interval data from the form
            mondayStarts = []
            mondayEnds = []
            monday_periods = int(request.form.get('monday-interval'))
            for i in range(monday_periods):
                start_time = request.form.get('monday-interval-start-time-' + str(i))
                end_time = request.form.get('monday-interval-end-time-' + str(i))
                #duration = calculate_duration(start_time, end_time)
                #totalDuration += duration
                mondayStarts.append(start_time)
                mondayEnds.append(end_time)

            # Get the tuesday interval data from the form
            tuesdayStarts = []
            tuesdayEnds = []
            tuesdayـperiods = int(request.form.get('tuesday-interval'))
            for i in range(tuesdayـperiods):
                start_time = request.form.get('tuesday-interval-start-time-' + str(i))
                end_time = request.form.get('tuesday-interval-end-time-' + str(i))
                #duration = calculate_duration(start_time, end_time)
                #totalDuration += duration
                tuesdayStarts.append(start_time)
                tuesdayEnds.append(end_time)

            # Get the wednesday interval data from the form
            wednesdayStarts = []
            wednesdayEnds = []
            wednesday_periods = int(request.form.get('wednesday-interval'))
            for i in range(wednesday_periods):
                start_time = request.form.get('wednesday-interval-start-time-' + str(i))
                end_time = request.form.get('wednesday-interval-end-time-' + str(i))
                #duration = calculate_duration(start_time, end_time)
                #totalDuration += duration
                wednesdayStarts.append(start_time)
                wednesdayEnds.append(end_time)

            # Get the thursday interval data from the form
            thursdayStarts = []
            thursdayEnds = []
            thursday_periods = int(request.form.get('thursday-interval'))
            for i in range(thursday_periods):
                start_time = request.form.get('thursday-interval-start-time-' + str(i))
                end_time = request.form.get('thursday-interval-end-time-' + str(i))
                #duration = calculate_duration(start_time, end_time)
                #totalDuration += duration
                thursdayStarts.append(start_time)
                thursdayEnds.append(end_time)

            cursor.execute("INSERT INTO job_times (time_id,fixed_flexible,sunday_job_periods,sunday_start,sunday_end,monday_job_periods,monday_start,monday_end,tuesdayـjob_periods,tuesday_start,tuesday_end,wednesday_job_periods,wednesday_start,wednesday_end,thursday_job_periods,thursday_start,thursday_end) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (reference_key,fixed_flexible,sunday_periods,','.join(map(str, sundayStarts)),','.join(map(str, sundayEnds)),monday_periods,','.join(map(str, mondayStarts)),','.join(map(str, mondayEnds)),tuesdayـperiods,','.join(map(str, tuesdayStarts)),','.join(map(str, tuesdayEnds)),wednesday_periods,','.join(map(str, wednesdayStarts)),','.join(map(str, wednesdayEnds)),thursday_periods,','.join(map(str, thursdayStarts)),','.join(map(str, thursdayEnds)) ))
        
            
            #--------------------------- End interval data

        #cursor.execute("INSERT INTO job_times (user_id,fixed_flexible,flexible_hours,sunday_job_periods,sunday_start,sunday_end,monday_job_periods,monday_start,monday_end,tuesdayـjob_periods,tuesday_start,tuesday_end,wednesday_job_periods,wednesday_start,wednesday_end,thursday_job_periods,thursday_start,thursday_end) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        #               (user_id,fixed_flexible,flexible_hours,sunday_periods,','.join(map(str, sundayStarts)),','.join(map(str, sundayEnds)),monday_periods,','.join(map(str, mondayStarts)),','.join(map(str, mondayEnds)),tuesdayـperiods,','.join(map(str, tuesdayStarts)),','.join(map(str, tuesdayEnds)),wednesday_periods,','.join(map(str, wednesdayStarts)),','.join(map(str, wednesdayEnds)),thursday_periods,','.join(map(str, thursdayStarts)),','.join(map(str, thursdayEnds)) ))
        connection.commit()
        connection.close()
        return redirect(url_for("employee"))

    cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if user:
        return render_template('post_job.html', user=user)
    else:
        flash("User not found. Please log in again.", 'error')
        return redirect(url_for("login"))
    
@app.route('/employee')
def employee():
    if 'user_id' in session:
        user_id = session['user_id']
        
        try:
            connection = sqlite3.connect("users_database.db")
            cursor = connection.cursor()

            cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()

            cursor.execute("SELECT * FROM job_posts WHERE user_id = ?", (user_id,))
            jobs = cursor.fetchall()
            
            #session['job_id'] = jobs[0]
            connection.close()

            return render_template('employee.html', jobs=jobs, user=user)
        

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            flash("An error occurred while fetching the job posts. Please try again.", 'error')
            return redirect(url_for('index'))
    else:
        flash("You are not logged in. Please log in first.", 'error')
        return redirect(url_for("login"))


@app.route('/student')
def student():
    if 'user_id' in session:
        user_id = session['user_id']

        try:
            connection = sqlite3.connect("users_database.db")
            cursor = connection.cursor()

            cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()

            cursor.execute("SELECT * FROM seekers_form WHERE user_id = ?", (user_id,))
            seekerForms = cursor.fetchall()


            #check before display
            # Get the current date
            current_date = date.today() 
            confirm = 0
            cursor.execute("SELECT end_date FROM notifications ")
            rows = cursor.fetchall()

            # Iterate through each row
            for row in rows:
                end_date = datetime.strptime(row[0], "%Y-%m-%d").date()
    
                if end_date <= current_date:
                    # Delete the row where end_date has passed
                    cursor.execute("DELETE FROM notifications WHERE end_date = ?", (row[0],))

            cursor.execute("SELECT * FROM notifications WHERE student_id = ? AND confirm = ?", (user_id,confirm))
            notifications = cursor.fetchall()

            

            confirm1 = 1
            print("1")
            cursor.execute("SELECT id_job FROM notifications WHERE student_id = ? AND confirm = ?", (user_id,confirm1))
            #job_id = cursor.fetchone()
            job_id_tuple = cursor.fetchone()
            job_id = job_id_tuple[0] if job_id_tuple else None
            print(job_id)
            print("2")
            #cursor.execute("SELECT * FROM job_times  WHERE time_id = ?", (job_id,))
            #job_times = cursor.fetchall()
            cursor.execute("SELECT * FROM schedule WHERE student_id = ?", (user_id,))
            schedule = cursor.fetchall()
            print("3")
            print("33")
            '''
            select_query = SELECT day, student_name, job_start, job_end, student_start, student_end FROM schedule 
            cursor.execute(select_query)
            rows2 = cursor.fetchall()

            table_data = []
            for row in rows2:
                day, student_name, job_start, job_end, student_start, student_end = row
                table_data.append({
                    'day': day,
                    'student_name': student_name,
                    'job_start': job_start,
                    'job_end': job_end,
                    'student_start': student_start,
                    'student_end': student_end
                    })
            
            '''

            print("44")
            
            connection.commit()
            connection.close()

            return render_template('student.html', seekerForms=seekerForms, user=user, notifications=notifications,schedule=schedule)


        except sqlite3.Error as e:
            print(f"An error occurred1: {e}")
            flash("An error occurred while fetching the form. Please try again.", 'error')
            return redirect(url_for('index'))
    else:
        flash("You are not logged in. Please log in first.", 'error')
        return redirect(url_for("login"))
    
@app.route('/studentCancle')
def studentCancle():
    if 'user_id' not in session:
        flash("You are not logged in. Please log in first.", 'error')
        return redirect(url_for("login"))

    user_id = session['user_id']
    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    return render_template('student.html', user=user)


@app.route('/view_form/<id>')
def view_form(id):
    user_id = session['user_id']

    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM seekers_form WHERE user_id = ? AND id =?", (user_id,id))
    form = cursor.fetchone()
    cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT file_id,filename, data FROM files WHERE user_id = ?", (user_id,))
    file = cursor.fetchone()
   
    return render_template('view_form.html', form=form,user=user,file=file)
 
@app.route('/view_jobs/<id>')
def view_jobs(id):
    user_id = session['user_id']

    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM job_posts WHERE user_id = ? AND job_id =?", (user_id,id))
    jobs = cursor.fetchone()
    cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT * FROM job_times WHERE time_id =?", (id,))
    time = cursor.fetchone()

    return render_template('view_jobs.html', jobs=jobs,user=user,time=time)


@app.route('/update_post_job/<id>' , methods=['GET', 'POST'])
def update_post_job(id):
    if 'user_id' not in session:
        flash("You are not logged in. Please log in first.", 'error')
        return redirect(url_for("login"))

    user_id = session['user_id']
    #jobid = id
    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()

    if request.method == 'POST':
        try:
            new_skill = request.form.getlist('n_skills')
            new_skills = ",".join(map(str, new_skill))
            new_job_title = request.form['n_job_title']

            new_required_languages = request.form.getlist('n_required_languages')
            new_required_languages = ",".join(map(str, new_required_languages))
            new_required_major = request.form['n_required_major']

            new_min_gpa = request.form['n_min_gpa']
            new_skills = new_skills
            #new_working_hours = request.form['n_working_hours']
            new_job_duration = request.form['n_job_duration']
            new_positions_available = request.form['n_positions_available']
            new_experience = request.form['n_experience'] 
            new_work_location = request.form['n_work_location'] 
            new_fixed_flexible = request.form['n_fixed-flexible']

            if new_fixed_flexible == 'Flexible':
                new_flexible_hours = request.form['n_flexible_hours']
                cursor.execute("UPDATE job_times SET fixed_flexible = '{}' , flexible_hours='{}', sunday_job_periods= NULL,sunday_start= NULL,sunday_end= NULL,monday_job_periods= NULL,monday_start= NULL,monday_end= NULL,tuesdayـjob_periods= NULL,tuesday_start= NULL,tuesday_end= NULL,wednesday_job_periods= NULL,wednesday_start= NULL,wednesday_end= NULL,thursday_job_periods= NULL,thursday_start= NULL,thursday_end= NULL WHERE time_id = '{}' ".format(new_fixed_flexible,new_flexible_hours,id))

            if new_fixed_flexible == 'Fixed':
                #--------------------------- Start interval data
                # Get the sunday interval data from the form
                sundayStarts = []
                sundayEnds = []
                sunday_periods = int(request.form.get('sunday-interval2'))
                #totalDuration = 0 
                for i in range(sunday_periods):
                    print("i== ",i)
                    start_time = request.form.get('sunday-interval2-start-time-' + str(i))
                    end_time = request.form.get('sunday-interval2-end-time-' + str(i))
                    #duration = calculate_duration(start_time, end_time)
                    #totalDuration += duration
                    sundayStarts.append(start_time)
                    sundayEnds.append(end_time)

                # Get the monday interval data from the form
                mondayStarts = []
                mondayEnds = []
                monday_periods = int(request.form.get('monday-interval2'))
                for i in range(monday_periods):
                    print("i== ",i)
                    start_time = request.form.get('monday-interval2-start-time-' + str(i))
                    end_time = request.form.get('monday-interval2-end-time-' + str(i))
                    #duration = calculate_duration(start_time, end_time)
                    #totalDuration += duration
                    mondayStarts.append(start_time)
                    mondayEnds.append(end_time)
    
                # Get the tuesday interval data from the form
                tuesdayStarts = []
                tuesdayEnds = []
                tuesdayـperiods = int(request.form.get('tuesday-interval2'))
                for i in range(tuesdayـperiods):
                    print("i== ",i)
                    start_time = request.form.get('tuesday-interval2-start-time-' + str(i))
                    end_time = request.form.get('tuesday-interval2-end-time-' + str(i))
                    #duration = calculate_duration(start_time, end_time)
                    #totalDuration += duration
                    tuesdayStarts.append(start_time)
                    tuesdayEnds.append(end_time)
                
                # Get the wednesday interval data from the form
                wednesdayStarts = []
                wednesdayEnds = []
                wednesday_periods = int(request.form.get('wednesday-interval2'))
                for i in range(wednesday_periods):
                    print("i== ",i)
                    start_time = request.form.get('wednesday-interval2-start-time-' + str(i))
                    end_time = request.form.get('wednesday-interval2-end-time-' + str(i))
                    #duration = calculate_duration(start_time, end_time)
                    #totalDuration += duration
                    wednesdayStarts.append(start_time)
                    wednesdayEnds.append(end_time)

                # Get the thursday interval data from the form
                thursdayStarts = []
                thursdayEnds = []
                thursday_periods = int(request.form.get('thursday-interval2'))
                for i in range(thursday_periods):
                    print("i== ",i)
                    start_time = request.form.get('thursday-interval2-start-time-' + str(i))
                    end_time = request.form.get('thursday-interval2-end-time-' + str(i))
                    #duration = calculate_duration(start_time, end_time)
                    #totalDuration += duration
                    thursdayStarts.append(start_time)
                    thursdayEnds.append(end_time)
                #--------------------------- End interval data
                cursor.execute("UPDATE job_times SET fixed_flexible = '{}',sunday_job_periods= '{}',sunday_start= '{}',sunday_end= '{}',monday_job_periods= '{}',monday_start= '{}',monday_end= '{}',tuesdayـjob_periods= '{}',tuesday_start= '{}',tuesday_end= '{}',wednesday_job_periods= '{}',wednesday_start= '{}',wednesday_end= '{}',thursday_job_periods= '{}',thursday_start= '{}',thursday_end= '{}', flexible_hours= NULL WHERE time_id = '{}' ".format(new_fixed_flexible,sunday_periods,','.join(map(str, sundayStarts)),','.join(map(str, sundayEnds)),monday_periods,','.join(map(str, mondayStarts)),','.join(map(str, mondayEnds)),tuesdayـperiods,','.join(map(str, tuesdayStarts)),','.join(map(str, tuesdayEnds)),wednesday_periods,','.join(map(str, wednesdayStarts)),','.join(map(str, wednesdayEnds)),thursday_periods,','.join(map(str, thursdayStarts)),','.join(map(str, thursdayEnds)),id))
                     

            cursor.execute("UPDATE job_posts SET job_title = '{}', required_major = '{}', min_gpa = '{}' , skills = '{}', job_duration = '{}' , experience = '{}' ,positions_available = '{}' ,required_languages= '{}',work_location='{}' WHERE job_id = '{}' ".format(new_job_title,new_required_major,new_min_gpa,new_skills,new_job_duration,new_experience,new_positions_available,new_required_languages,new_work_location,id))

            connection.commit()
            connection.close()

            return redirect(url_for("employee"))
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return 'e'           
           
    else:
        cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        cursor.execute("SELECT * FROM job_posts WHERE user_id = ? AND job_id =?", (user_id,id))
        jobs = cursor.fetchone()

        cursor.execute("SELECT * FROM job_times WHERE time_id =?", (id,))
        time = cursor.fetchone()

        return render_template('update_post_job.html', user=user ,jobs=jobs,time=time)
    
@app.route('/update_find_job/<id>' , methods=['GET', 'POST'])
def update_find_job(id):
    
    if 'user_id' not in session:
        flash("You are not logged in. Please log in first.", 'error')
        return redirect(url_for("login"))

    user_id = session['user_id']

    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()
    
    if request.method == 'POST':
        
        try:

            new_skill = request.form.getlist('n_skills')
            new_skills = ",".join(map(str, new_skill))

            new_Language = request.form.getlist('n_Languages')
            new_Languages = ",".join(map(str, new_Language))

            new_name = request.form['n_name']
            new_phoneNumber = request.form['n_phoneNumber']
            new_Languages = new_Languages
            new_skills = new_skills
            new_gpa = request.form['n_gpa']
            new_major = request.form['n_major']
            new_experience = request.form['n_experience']
            new_work_duration = request.form['n_work_duration']
            work_preference = request.form['n_work_preference']
            new_uploaded_file = request.files['n_pdf_file']    # Get the uploaded file

            if new_uploaded_file:
                cursor.execute("DELETE FROM files WHERE user_id = '{}' ".format(user_id))

                # Save the file to a temporary location
                new_temp_path = '/tmp/' + new_uploaded_file.filename
                new_uploaded_file.save(new_temp_path)

                # Read the file data as binary
                with open(new_temp_path, 'rb') as file:
                    new_file_data = file.read()

                # Delete the temporary file
                os.remove(new_temp_path)

                cursor.execute('INSERT INTO files (user_id, filename, data) VALUES (?, ?, ?)',
                    ( user_id,new_uploaded_file.filename, new_file_data))

            #--------------------------- Start interval data
        
            # Get the sunday interval data from the form
            sundayStarts = []
            sundayEnds = []
            sunday_periods = int(request.form.get('sunday-interval2'))
            totalDuration = 0 
            for i in range(sunday_periods):
                print("i== ",i)
                start_time = request.form.get('sunday-interval2-start-time-' + str(i))
                end_time = request.form.get('sunday-interval2-end-time-' + str(i))
                duration = calculate_duration(start_time, end_time)
                totalDuration += duration
                sundayStarts.append(start_time)
                sundayEnds.append(end_time)

            # Get the monday interval data from the form
            mondayStarts = []
            mondayEnds = []
            monday_periods = int(request.form.get('monday-interval2'))
            for i in range(monday_periods):
                print("i== ",i)
                start_time = request.form.get('monday-interval2-start-time-' + str(i))
                end_time = request.form.get('monday-interval2-end-time-' + str(i))
                duration = calculate_duration(start_time, end_time)
                totalDuration += duration
                mondayStarts.append(start_time)
                mondayEnds.append(end_time)
  
            # Get the tuesday interval data from the form
            tuesdayStarts = []
            tuesdayEnds = []
            tuesdayـperiods = int(request.form.get('tuesday-interval2'))
            for i in range(tuesdayـperiods):
                print("i== ",i)
                start_time = request.form.get('tuesday-interval2-start-time-' + str(i))
                end_time = request.form.get('tuesday-interval2-end-time-' + str(i))
                duration = calculate_duration(start_time, end_time)
                totalDuration += duration
                tuesdayStarts.append(start_time)
                tuesdayEnds.append(end_time)
            
            # Get the wednesday interval data from the form
            wednesdayStarts = []
            wednesdayEnds = []
            wednesday_periods = int(request.form.get('wednesday-interval2'))
            for i in range(wednesday_periods):
                print("i== ",i)
                start_time = request.form.get('wednesday-interval2-start-time-' + str(i))
                end_time = request.form.get('wednesday-interval2-end-time-' + str(i))
                duration = calculate_duration(start_time, end_time)
                totalDuration += duration
                wednesdayStarts.append(start_time)
                wednesdayEnds.append(end_time)

            # Get the thursday interval data from the form
            thursdayStarts = []
            thursdayEnds = []
            thursday_periods = int(request.form.get('thursday-interval2'))
            for i in range(thursday_periods):
                print("i== ",i)
                start_time = request.form.get('thursday-interval2-start-time-' + str(i))
                end_time = request.form.get('thursday-interval2-end-time-' + str(i))
                duration = calculate_duration(start_time, end_time)
                totalDuration += duration
                thursdayStarts.append(start_time)
                thursdayEnds.append(end_time)
        
            #--------------------------- End interval data
            totalHoursDuration = convert_minutes_to_hours(totalDuration)

            cursor.execute("UPDATE seekers_form SET  name = '{}', phoneNumber = '{}', languages = '{}', skills = '{}', gpa = '{}', major = '{}', experience = '{}',totalHours = '{}',sunday_periods = '{}',monday_periods = '{}',tuesdayـperiods = '{}',wednesday_periods = '{}',thursday_periods= '{}',sunday_start_interval = '{}',sunday_end_interval = '{}',monday_start_interval = '{}',monday_end_interval = '{}',tuesday_start_interval = '{}',tuesday_end_interval = '{}',wednesday_start_interval = '{}',wednesday_end_interval = '{}',thursday_start_interval = '{}',thursday_end_interval = '{}',work_duration = '{}', work_preference = '{}'  WHERE id = '{}'".format 
                       (new_name, new_phoneNumber, new_Languages , new_skills, new_gpa, new_major, new_experience, totalHoursDuration, sunday_periods,monday_periods,tuesdayـperiods,wednesday_periods,thursday_periods,','.join(map(str, sundayStarts)),','.join(map(str, sundayEnds)),','.join(map(str, mondayStarts)),','.join(map(str, mondayEnds)),','.join(map(str, tuesdayStarts)),','.join(map(str, tuesdayEnds)),','.join(map(str, wednesdayStarts)),','.join(map(str, wednesdayEnds)),','.join(map(str, thursdayStarts)),','.join(map(str, thursdayEnds)),new_work_duration,work_preference,id ))
        
            connection.commit()
            connection.close()

            flash("Request was Updated successfully!", 'success')
            return redirect(url_for("student"))
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")    
    else:
        cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        cursor.execute("SELECT * FROM seekers_form WHERE user_id = ? AND id = ?", (user_id,id))
        form = cursor.fetchone()

        cursor.execute("SELECT * FROM files WHERE user_id = ?", (user_id,))
        file = cursor.fetchone()


        return render_template('update_find_job.html', user=user , form = form, file=file)
       
@app.route('/delete_form/<id>/<user_id>')
def delete_form(id,user_id):
    #user_id = session['user_id']
    #job_id = session['job_id']
    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM seekers_form WHERE id = '{}' ".format(id))
    cursor.execute("DELETE FROM files WHERE user_id = '{}' ".format(user_id))

    connection.commit()
    connection.close()

    return redirect(url_for("student"))

@app.route('/delete_jobs/<id>')
def delete_jobs(id):
    #user_id = session['user_id']
    #job_id = session['job_id']
    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM job_posts WHERE job_id = '{}' ".format(id))
    cursor.execute("DELETE FROM job_times WHERE time_id = '{}' ".format(id))

    connection.commit()
    connection.close()

    return redirect(url_for("employee"))

@app.route('/employeeCancle')
def employeeCancle():
    if 'user_id' not in session:
        flash("You are not logged in. Please log in first.", 'error')
        return redirect(url_for("login"))

    user_id = session['user_id']
    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM job_posts WHERE user_id = ?", (user_id,))
    jobs = cursor.fetchall()

    return render_template('employee.html', jobs=jobs, user=user)

'''    ------------------------   recommendetion system trying   ------------------------    '''


def makedicforjob(job_data) :

    # Create a dictionary with known keys and no initial values
    my_dict = {
        "Sunday": [],
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
    }

    # Days of the week to assign data to
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    day_index = 0  # Start with Sunday

    # Iterate through the tuple in increments of 3 elements
    for i in range(0, len(job_data), 3):
        # Get the current set of 3 elements
        job_info = job_data[i:i + 3]
        #print(job_info)

        # Check if job_data[i] is zero, and if so, don't add any time slots
        if job_info[0] == 0:
            day_index = (day_index + 1) % len(days)
            continue

        # Extract the start and end times
        start_times = job_data[i+1]
        end_times = job_data[i+2]

        # Split start_times and end_times using comma as the delimiter
        start_times = start_times.split(',')
        end_times = end_times.split(',')

        # Iterate through the times and add them to the corresponding day's list in the dictionary
        for start, end in zip(start_times, end_times):
            t = start.strip() + " - " + end.strip()
            my_dict[days[day_index]].append(t)

        # Move to the next day
        day_index = (day_index + 1) % len(days)
    print(my_dict)
    return my_dict


    
def makedicforStudents(students_time) :
    # Create a dictionary to store the student schedules
    student_schedules = {}

    # Days of the week
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]

    # Iterate through the list of students
    for student_data in students_time:
        # Extract the student index (e.g., 0 or 1)
        student_index = student_data[0]
        student_name = student_index

        # Initialize a dictionary to store the schedule for each day
        student_schedule = {day: [] for day in days}

        day_index = 0

        # Iterate through the student's data in increments of 1 or 2 elements
        for i in range(1, len(student_data), 3):
            # Extract the day and time data
            slots = student_data[i]

            if slots != 0:
                # Get the current set of 3 elements
                job_info = student_data[i:i + 3]
                # Extract the start and end times
                start_times = student_data[i + 1]
                end_times = student_data[i + 2]
                start_times = start_times.split(',')
                end_times = end_times.split(',')

                # Iterate through the times and add them to the corresponding day's list in the dictionary
                for start, end in zip(start_times, end_times):
                    t = start.strip() + " - " + end.strip()
                    student_schedule[days[day_index]].append(t)
            else:
                # If there are no start or end times, store an empty list in the dictionary
                student_schedule[days[day_index]] = []

            # Move to the next day
            day_index = (day_index + 1) % len(days)

        student_schedules[student_name] = student_schedule
        print(student_schedules)

    return student_schedules
# Function to convert time in "hh:mm AM/PM" format to minutes
def convert_to_minutes2(time_str):
    # Split time and meridiem (AM/PM)
    time, meridiem = time_str.split()
    hour, minute = time.split(":")
    hour = int(hour)
    minute = int(minute)

    # Convert to 24-hour format
    if meridiem == "PM" and hour != 12:
        hour += 12

    # Convert to minutes
    return hour * 60 + minute
# Function to calculate alignment scores with overlaps for all students
def calculate_alignment_scores_with_overlaps(students, job_schedule):
    alignment_scores = {}

    # Iterate through each student and their schedule
    for student, schedule in students.items():
        # Calculate alignment score with overlaps and get overlap information
        alignment_score, overlap_info = calculate_alignment_score_with_overlaps(schedule, job_schedule)

        # Store alignment score and overlap information for the student
        alignment_scores[student] = alignment_score
        alignment_scores[f"{student} Overlaps"] = overlap_info

    return alignment_scores
# Function to calculate the alignment score with overlaps for a single student
def calculate_alignment_score_with_overlaps(student_schedule, job_schedule):
    from collections import defaultdict

    student_overlaps = defaultdict(dict)

    # Iterate through days in the student's schedule
    #dict_keys(['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'])

    for day in student_schedule.keys():

        if day in job_schedule:
            student_overlaps[day] = []
            #print(job_schedule)

            # Iterate through each time slot in the student's schedule for the current day
            for student_slot in student_schedule[day]:

                # Iterate through each time slot in the job schedule for the current day
                for job_slot in job_schedule[day]:

                    # Split start and end times for the student and job slots
                    student_start, student_end = student_slot.split(" - ")
                    job_start, job_end = job_slot.split(" - ")
                    
                    # Convert start and end times to minutes
                    student_start_minutes = convert_to_minutes2(student_start)
                    student_end_minutes = convert_to_minutes2(student_end)
                    job_start_minutes = convert_to_minutes2(job_start)
                    job_end_minutes = convert_to_minutes2(job_end)

                    # Calculate the overlap start and end times
                    overlap_start = max(student_start_minutes, job_start_minutes)
                    overlap_end = min(student_end_minutes, job_end_minutes)
                    
                    # Check if there is an overlap
                    if overlap_start < overlap_end:
                        student_overlaps[day].append((overlap_start, overlap_end))
       

    # Calculate the alignment score as the sum of overlap times
    alignment_score = sum(
        (overlap[1] - overlap[0]) for overlaps in student_overlaps.values() for overlap in overlaps
    )
    #print(alignment_score,student_overlaps)
   
    return alignment_score, student_overlaps



@app.route('/get_recommendations/<int:job_id>')
def get_recommendations(job_id):
    if 'user_id' not in session:
        flash("You are not logged in. Please log in first.", 'error')
        return redirect(url_for("login"))

    user_id = session['user_id']

    # Establish a connection to the SQLite database
    conn = sqlite3.connect('users_database.db')
    cursor = conn.cursor()
    ''' ------------------- Retrieve general data ------------------- '''
    cursor.execute("SELECT * FROM seekers_form")
    seekers_info = cursor.fetchall()

    cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    # Retrieve job title
    cursor.execute("SELECT job_title FROM job_posts WHERE job_id = ?", (job_id,))
    job_title = cursor.fetchone()

    ''' ------------------- Retrieve general data ------------------- '''
    # Retrieve data from SQL database
    cursor.execute("SELECT major, gpa, skills, totalHours, experience, languages, work_preference,id FROM seekers_form")
    seekers_data = cursor.fetchall()

    cursor.execute("SELECT required_major, min_gpa, skills, experience, required_languages,work_location FROM job_posts WHERE job_id = ?", (job_id,))
    job_data = cursor.fetchone()
    job_data = [job_data]

    cursor.execute("SELECT * FROM job_times WHERE time_id = ?", (job_id,))
    job_time = cursor.fetchone()

    
    cursor.execute("SELECT id, sunday_periods, sunday_start_interval, sunday_end_interval, monday_periods, monday_start_interval, monday_end_interval, tuesdayـperiods, tuesday_start_interval, tuesday_end_interval, wednesday_periods, wednesday_start_interval, wednesday_end_interval, thursday_periods, thursday_start_interval, thursday_end_interval FROM seekers_form")
    students_time = cursor.fetchall()

    # Define a dictionary to map experience levels to weights
    experience_weights = {
        'No': 0
    }

    # Assign weights to experience feature values
    filtered_seekers_data2 = []
    for seeker in seekers_data:
        experience = seeker[4]
        weight = experience_weights.get(experience, 1.0)  # Default weight is 1.0 if experience level is not specified in the dictionary
        filtered_seeker = list(seeker[:4]) + [weight] + list(seeker[5:])  # Include the weight in the filtered seeker data
        filtered_seekers_data2.append(filtered_seeker)

    filtered_seekers_data = []
    if job_time[2] == 'Flexible':
        # Filter out seekers whose total duration is less than the job's working hours
        for seeker in filtered_seekers_data2:
            if seeker[3] >= job_time[3]:
                filtered_seeker = list(seeker[:3]) + list(seeker[4:]) # Drop the time-related columns from the seeker data
                filtered_seekers_data.append(filtered_seeker)

    elif job_time[2] == 'Fixed':
        # Create a dictionary for the job schedule
        job_schedule = makedicforjob(job_time[4:])
        #print(job_time[4:])

        # Create a dictionary for the students' schedules
        students_schedules = makedicforStudents(students_time)
        # Calculate alignment scores with overlaps for all students
        alignment_scores = calculate_alignment_scores_with_overlaps(students_schedules, job_schedule)
        #calculate_alignment_score_with_overlaps

        # Filter students with overlapping time greater than zero and store their data
        students_with_overlap = {}  # Dictionary to store data for students with overlap

        for seeker in filtered_seekers_data2:
            student_id = seeker[7]
            alignment_score = alignment_scores.get(student_id, 0)
            #print('alignment_score= ',alignment_score)

            if alignment_score > 0:
                #print('before',seeker)
                filtered_seeker = list(seeker[:3]) + list(seeker[4:])   # Add alignment score to the tuple
                #print('after',filtered_seeker)
                filtered_seekers_data.append(filtered_seeker)
                

                # Store data for students with overlap
                students_with_overlap[student_id] = {
                    'seeker': seeker,
                    'alignment_score': alignment_score,
                    'schedule': students_schedules.get(student_id, {})
                }
        print(filtered_seekers_data)
        #print(students_with_overlap[38]['alignment_score'])

        

    if not filtered_seekers_data:
        message = "No suitable seekers found."
        return render_template('recommendations.html', message=message, job_id=job_id, job_title=job_title , user=user)
    else:
        # Perform recommendation process
        #print(filtered_seekers_data[1])
        seekers_combined_features = [' '.join(str(item) for item in row) for row in filtered_seekers_data]
        job_combined_features = [' '.join(str(item) for item in job_data)]

        tfidf = TfidfVectorizer(
            sublinear_tf=True,
            use_idf=True,
            smooth_idf=True,
            norm=None,
            lowercase=True,
            stop_words='english',
            token_pattern=r'\b\w+\b',
            max_features=None,
            binary=False,
            decode_error='ignore',
            strip_accents='unicode',
            dtype=np.float32,
            vocabulary=None,
            ngram_range=(1, 1),
            max_df=1.0,
            min_df=1,
            analyzer='word',
            encoding='utf-8')
        seekers_tfidf_matrix = tfidf.fit_transform(seekers_combined_features)
        job_tfidf_matrix = tfidf.transform(job_combined_features)

        # Define the feature weights
        feature_weights = {
            'totalHours': 1.0,
            'skills': 1.0,
            'gpa': 0.7,
            'languages': 0.9,
            'work_preference': 0.9,
            'major': 0.8
        }
        feature_indices = {feature: tfidf.vocabulary_.get(feature) for feature in feature_weights}
        for feature, weight in feature_weights.items():
            feature_index = feature_indices.get(feature)
            if feature_index is not None:
                seekers_tfidf_matrix[:, feature_index] *= weight
                job_tfidf_matrix[:, feature_index] *= weight


        # Compute the cosine similarity
        similarity_scores = cosine_similarity(seekers_tfidf_matrix, job_tfidf_matrix)
        top_seekers = np.argsort(similarity_scores, axis=0)[-9:][::-1].flatten()
        recommended_seekers = []
        
        seekers_data_dict = {seeker[6]: seeker for seeker in filtered_seekers_data}
        seekers_info_dict ={seekers_info[0]: seekers_info for seekers_info in seekers_info}

        for i in top_seekers:
            seeker_id = filtered_seekers_data[i][6]  # Get the seeker ID
            seeker = seekers_data_dict.get(seeker_id)  # Retrieve the seeker information using the seeker ID
            score = similarity_scores[i][0]  # Get the similarity score for the seeker
            score = score * 100
            info = seekers_info_dict.get(seeker_id)
            recommended_seekers.append({'seeker': seeker, 'score': score, 'name': info})
        
        cursor.execute("SELECT * FROM notifications WHERE id_job = ? ", (job_id,))
        notifications = cursor.fetchall()
    
    

        cursor.close()
        conn.close()

        return render_template('recommendations.html', recommendations=recommended_seekers, job_id=job_id, job_title=job_title , user=user, notifications=notifications)

def check(s,e):
    return "Flase"


@app.route('/get_Unstaisfied_recommendations/<int:job_id>')
def get_Unstaisfied_recommendations(job_id):
    if 'user_id' not in session:
        flash("You are not logged in. Please log in first.", 'error')
        return redirect(url_for("login"))

    user_id = session['user_id']

    # Establish a connection to the SQLite database
    conn = sqlite3.connect('users_database.db')
    cursor = conn.cursor()
    ''' ------------------- Retrieve general data ------------------- '''
    cursor.execute("SELECT * FROM seekers_form")
    seekers_info = cursor.fetchall()

    cursor.execute("SELECT id, password, position, name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    # Retrieve job title
    cursor.execute("SELECT job_title FROM job_posts WHERE job_id = ?", (job_id,))
    job_title = cursor.fetchone()

    ''' ------------------- Retrieve general data ------------------- '''
    # Retrieve data from SQL database
    cursor.execute("SELECT major, gpa, skills, totalHours, experience, languages, work_preference,id FROM seekers_form")
    seekers_data = cursor.fetchall()

    cursor.execute("SELECT required_major, min_gpa, skills, experience, required_languages,work_location FROM job_posts WHERE job_id = ?", (job_id,))
    job_data = cursor.fetchone()
    job_data = [job_data]

    cursor.execute("SELECT * FROM job_times WHERE time_id = ?", (job_id,))
    job_time = cursor.fetchone()
    
    # Define a dictionary to map experience levels to weights
    experience_weights = {
        'No': 0
    }

    # Assign weights to experience feature values
    filtered_seekers_data2 = []
    for seeker in seekers_data:
        experience = seeker[4]
        weight = experience_weights.get(experience, 1.0)  # Default weight is 1.0 if experience level is not specified in the dictionary
        filtered_seeker = list(seeker[:4]) + [weight] + list(seeker[5:])  # Include the weight in the filtered seeker data
        filtered_seekers_data2.append(filtered_seeker)
    
    # Filter out seekers whose total duration is less than the job's working hours
    unsatisfied_requirements = []
    if job_time[2] == 'Flexible':
        for seeker in filtered_seekers_data2:
            if seeker[3] < job_time[3]:
                filtered_seeker2 = list(seeker[:3]) + list(seeker[4:]) # Drop the time-related columns from the seeker data
                unsatisfied_requirements.append(filtered_seeker2)
        print('unsatisfied_requirements',len(unsatisfied_requirements))
      

    if not unsatisfied_requirements:
        message = "No suitable seekers found."
        return render_template('recommendations2.html', message=message, job_id=job_id, job_title=job_title , user=user)
    else:
        # Perform recommendation process
        seekers_combined_features = [' '.join(str(item) for item in row) for row in unsatisfied_requirements]
        job_combined_features = [' '.join(str(item) for item in job_data)]

        tfidf = TfidfVectorizer(sublinear_tf=True,
            use_idf=True,
            smooth_idf=True,
            norm=None,
            lowercase=True,
            stop_words='english',
            token_pattern=r'\b\w+\b',
            max_features=None,
            binary=False,
            decode_error='ignore',
            strip_accents='unicode',
            dtype=np.float32,
            vocabulary=None,
            ngram_range=(1, 1),
            max_df=1.0,
            min_df=1,
            analyzer='word',
            encoding='utf-8')
        seekers_tfidf_matrix = tfidf.fit_transform(seekers_combined_features)
        job_tfidf_matrix = tfidf.transform(job_combined_features)

        
        # Define the feature weights
        feature_weights = {
            'totalHours': 1.0,
            'skills': 1.0,
            'gpa': 0.7,
            'languages': 0.9,
            'work_preference': 0.9,
            'major': 0.8
        }
        feature_indices = {feature: tfidf.vocabulary_.get(feature) for feature in feature_weights}
        for feature, weight in feature_weights.items():
            feature_index = feature_indices.get(feature)
            if feature_index is not None:
                seekers_tfidf_matrix[:, feature_index] *= weight
                job_tfidf_matrix[:, feature_index] *= weight


       
        similarity_scores = cosine_similarity(seekers_tfidf_matrix, job_tfidf_matrix)
        top_seekers = np.argsort(similarity_scores, axis=0)[-9:][::-1].flatten()

        seekers_data_dict = {seeker[6]: seeker for seeker in unsatisfied_requirements}
        seekers_info_dict ={seekers_info[0]: seekers_info for seekers_info in seekers_info}

        #recommended_seekers = []
        unsatisfied_recommendations = []
        for i in top_seekers:
            seeker_id = unsatisfied_requirements[i][6]  # Get the seeker ID
            seeker = seekers_data_dict.get(seeker_id)  # Retrieve the seeker information using the seeker ID
            score = similarity_scores[i][0]  # Get the similarity score for the seeker
            score = score * 100
            info = seekers_info_dict.get(seeker_id)
            unsatisfied_recommendations.append({'seeker': seeker, 'score': score, 'name': info})
            
            
        cursor.close()
        conn.close()

        return render_template('recommendations2.html', recommendations=unsatisfied_recommendations, job_id=job_id, job_title=job_title , user=user)

def get_candidate_info(candidate_id):
    try:
        conn = sqlite3.connect('users_database.db')
        cursor = conn.cursor()

        # Fetch candidate data
        cursor.execute("SELECT * FROM seekers_form WHERE user_id=?", (candidate_id,))
        candidate_data = cursor.fetchone()

        # Fetch email
        cursor.execute("SELECT email FROM users WHERE id=?", (candidate_id,))
        email = cursor.fetchone()

        # Fetch CV information
        cursor.execute("SELECT file_id, filename, data FROM files WHERE user_id=?", (candidate_id,))
        file = cursor.fetchone()

        if candidate_data:
            return {
                
                            'id': candidate_data[2],
            'name': candidate_data[3],
            'major': candidate_data[5],
            'phone': candidate_data[4],
            'email': email,
            'gpa': candidate_data[6],
            'skills': candidate_data[7],
            'experience': candidate_data[8],
            'languages': candidate_data[9],
            'availability': candidate_data[10],
            'work_preference': candidate_data[27],

                'cv': file[0] if file else None  # Return CV if available, else None
            }
        else:
            return {}  # Return an empty dictionary if no data found
    except sqlite3.Error as e:
        # Handle database errors here
        print("Database error:", str(e))
        return None  # Return None to indicate an error
    finally:
        conn.close()

@app.route('/get_candidate/<int:candidate_id>')
def get_candidate(candidate_id):
    candidate_info = get_candidate_info(candidate_id)
    print(candidate_id)
    if candidate_info:
        return jsonify(candidate_info)
    else:
        return jsonify(error='Candidate not found'), 404
    
@app.route('/get_job_info/<int:id>')
def get_job_info(id):
    try:
        connection = sqlite3.connect("users_database.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM job_posts WHERE job_id = ?", (id,))
        job = cursor.fetchone()
        print(job[5])
        connection.close()

        if job is None:
            abort(404)  # Job not found, return a 404 error

        # Return the job information as JSON
        return jsonify({
            'title': job[2],
            'major': job[3],
            'skills': job[5],
            'gpa' : job[4],
            'working_hours' : job[6],
            'job_duration' : job[7],
            'experience' : job[8],
            'positions_available' : job[9],
            'required_languages' : job[10],
            'work_location' : job[11]

        })
    except Exception as e:
        # Handle database errors or other exceptions
        return str(e)

if __name__ == "__main__":
   app.run(debug = True)

@app.route('/notify/<int:student_id>/<int:job_id>', methods=['POST'])
def notify(student_id,job_id):
    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()
    print("1")

    if request.method == 'POST':
        try:
            confirm = False
            message = "you have been selected"
            # Get the current date
            current_date = date.today()
            

            # Calculate the end date as three days after the current date
            end_date = current_date + timedelta(days=1)

            #student_id = request.form['student-id']
            cursor.execute("SELECT job_title, job_duration,positions_available, work_location FROM job_posts WHERE job_id = ?", (job_id,))
            user = cursor.fetchone()
           
            # Get the current number of positions filled for the job
            cursor.execute("SELECT COUNT(*) FROM notifications WHERE id_job = ?", (job_id,))
            current_positions_filled = cursor.fetchone()[0]

            # Check if the current number of positions filled exceeds the maximum available positions
            if current_positions_filled >= user[2]:
                print("Cannot send notification. Maximum positions filled.")
                return "Cannot send notification. Maximum positions filled.", 300
            
            cursor.execute("INSERT INTO notifications (student_id, id_job,title_job, duration_of_job, message, work_location, confirm, current_date, end_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (student_id, job_id, user[0], user[1], message, user[3] ,confirm, current_date, end_date))
            
            #check before display
            # Get the current date
            current_date = date.today() 
            print(current_date)
            cursor.execute("SELECT end_date FROM notifications ")
            rows  = cursor.fetchall()
            print(notify)
            for row in rows:
                # Convert the notify[0] value to a date object
                notify_date = datetime.strptime(row[0], "%Y-%m-%d").date()
                print(notify_date)
                if current_date >= notify_date:
                    # Delete notifications where end_date has passed
                    cursor.execute("DELETE FROM notifications WHERE end_date = ?", (row[0],))
                    
            
            connection.commit()
            connection.close()     
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            #flash("An error occurred while fetching the job posts. Please try again.", 'error')
            #return redirect(url_for('index'))
    print(f"Sending notification to student with ID: {student_id}")
 
    # You can return a response to the client if needed
    return "Notification sent successfully", 200

@app.route('/confirm_notification/<int:student_id>/<int:notify_id>', methods=['GET', 'POST'])
def confirm_notification(student_id,notify_id):
    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()

    print(f"Sending notification to student with ID: {student_id}")
    print(f"Sending notification ID2: {notify_id}")
    print("p")
    cursor.execute("SELECT id_job FROM notifications WHERE notification_id = ?", (notify_id,))
    #job_id = cursor.fetchone()
    job_id_tuple = cursor.fetchone()
    job_id = job_id_tuple[0] if job_id_tuple else None
    print(job_id)
    print("r")
    try:
        print("i")
        confirm = 1
        
        cursor.execute("UPDATE notifications SET confirm = '{}' WHERE notification_id = '{}' AND student_id = '{}'".format(confirm,notify_id,student_id))
        print("n")
        generate_schedule(student_id,job_id)
        print("tt")
        

        print("t")
        connection.commit()
        connection.close()

               
    except sqlite3.Error as e:
        print(f"An error occurred2: {e}")
        #flash("An error occurred while fetching the job posts. Please try again.", 'error')
        #return redirect(url_for('index'))
    
    
    return redirect(url_for('student'))

def student_job(student_id,job_id):

    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM job_times WHERE time_id = ?", (job_id,))
    job_time = cursor.fetchone()
    
    cursor.execute("SELECT id, sunday_periods, sunday_start_interval, sunday_end_interval, monday_periods, monday_start_interval, monday_end_interval, tuesdayـperiods, tuesday_start_interval, tuesday_end_interval, wednesday_periods, wednesday_start_interval, wednesday_end_interval, thursday_periods, thursday_start_interval, thursday_end_interval FROM seekers_form WHERE user_id = ?", (student_id,))
    students_time = cursor.fetchall()

    # Retrieve the student_schedule and job_schedule data from your backend
    student_schedule = makedicforStudents(students_time)  # Replace with your actual logic to fetch student schedule
    job_schedule = makedicforjob(job_time[4:])

    connection.commit()
    connection.close()

    return student_schedule,job_schedule


@app.route('/reject_notification/<int:student_id>/<int:notify_id>', methods=['GET', 'POST'])
def reject_notification(student_id,notify_id):
    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()

    print(f"Sending notification to student with ID: {student_id}")
    print(f"Sending notification ID2: {notify_id}")
    
    
    try:
        #print("i")
        confirm = 2
        cursor.execute("UPDATE notifications SET confirm = '{}' WHERE notification_id = '{}' AND student_id = '{}'".format(confirm,notify_id,student_id))
        #print("n")
        
        #print("t")
        connection.commit()
        connection.close()

               
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        #flash("An error occurred while fetching the job posts. Please try again.", 'error')
        #return redirect(url_for('index'))
    
    

    return redirect(url_for('student'))


from datetime import datetime
def generate_schedule(student_id, job_id):

    connection = sqlite3.connect("users_database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM job_times WHERE time_id = ?", (job_id,))
    job_time = cursor.fetchone()
    
    cursor.execute("SELECT id, sunday_periods, sunday_start_interval, sunday_end_interval, monday_periods, monday_start_interval, monday_end_interval, tuesdayـperiods, tuesday_start_interval, tuesday_end_interval, wednesday_periods, wednesday_start_interval, wednesday_end_interval, thursday_periods, thursday_start_interval, thursday_end_interval FROM seekers_form WHERE user_id = ?", (student_id,))
    students_time = cursor.fetchall()
    print("problem")
    print(students_time[0])
    # Retrieve the student_schedule and job_schedule data from your backend
    student_schedule = makedicforStudents2(students_time)  # Replace with your actual logic to fetch student schedule
    job_schedule = makedicforjob(job_time[4:])

    
    overlapping_schedule = {}

    for day in student_schedule:
        student_schedule2 = student_schedule[day]
        for time_range in student_schedule2:
            student_start_time, student_end_time = time_range.split(" - ")
            student_start_datetime = datetime.strptime(student_start_time, "%I:%M %p")
            student_end_datetime = datetime.strptime(student_end_time, "%I:%M %p")
            if day in job_schedule:
                for job_time_range in job_schedule[day]:
                    job_start_time, job_end_time = job_time_range.split(" - ")
                    job_start_datetime = datetime.strptime(job_start_time, "%I:%M %p")
                    job_end_datetime = datetime.strptime(job_end_time, "%I:%M %p")
                    if student_start_datetime <= job_end_datetime and student_end_datetime >= job_start_datetime:
                        overlapping_start_time = max(student_start_datetime, job_start_datetime)
                        overlapping_end_time = min(student_end_datetime, job_end_datetime)
                        
                        # Check if the start time and end time are equal
                        if overlapping_start_time != overlapping_end_time:
                            overlapping_range = overlapping_start_time.strftime("%I:%M %p") + " - " + overlapping_end_time.strftime("%I:%M %p")
                            overlapping_schedule.setdefault(day, []).append(overlapping_range)

    # Filter out overlapping ranges where start time and end time are equal
    overlapping_schedule = {day: overlapping_ranges for day, overlapping_ranges in overlapping_schedule.items() if overlapping_ranges}
    print("overlapping")
    print(overlapping_schedule)

    for day, time_slots in overlapping_schedule.items():
        for time_slot in time_slots:
            start_time, end_time = time_slot.split(' - ')
            cursor.execute("INSERT INTO schedule (day,start_time, end_time, student_id, job_id) VALUES (?, ?, ?, ?, ?)", (day, start_time, end_time,student_id,job_id))


               
    connection.commit()
    connection.close()


def makedicforStudents2(students_time) :
    # Create a dictionary to store the student schedules
    student_schedules = {}

    # Days of the week
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]

    # Iterate through the list of students
    for student_data in students_time:
        # Extract the student index (e.g., 0 or 1)
        student_index = student_data[0]
        student_name = student_index

        # Initialize a dictionary to store the schedule for each day
        student_schedule = {day: [] for day in days}

        day_index = 0

        # Iterate through the student's data in increments of 1 or 2 elements
        for i in range(1, len(student_data), 3):
            # Extract the day and time data
            slots = student_data[i]

            if slots != 0:
                # Get the current set of 3 elements
                job_info = student_data[i:i + 3]
                # Extract the start and end times
                start_times = student_data[i + 1]
                end_times = student_data[i + 2]
                start_times = start_times.split(',')
                end_times = end_times.split(',')

                # Iterate through the times and add them to the corresponding day's list in the dictionary
                for start, end in zip(start_times, end_times):
                    t = start.strip() + " - " + end.strip()
                    student_schedule[days[day_index]].append(t)
            else:
                # If there are no start or end times, store an empty list in the dictionary
                student_schedule[days[day_index]] = []

            # Move to the next day
            day_index = (day_index + 1) % len(days)

        student_schedules = student_schedule
        print(student_schedules)

    return student_schedules

