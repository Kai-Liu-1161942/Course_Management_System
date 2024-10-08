import connect

import mysql.connector  
from mysql.connector import Error  
from flask import Flask, render_template, request, session as flask_session,jsonify, send_file,redirect,flash,url_for
from werkzeug.security import generate_password_hash, check_password_hash  # 导入密码哈希函数 
from datetime import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template

from selenium import webdriver  
import time  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.wait import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
import pandas as pd 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import random
import socket

app = Flask(__name__)  



app.secret_key = 'your_secret_key_here'  #session 必须要设置
def get_fullname(username):
    conn = mysql.connector.connect(**connect.db_config)  
    cursor = conn.cursor()  
    user_query = "select first_name, last_name from users2 where username = %s;"
    cursor.execute(user_query,(username,))
    fullname = cursor.fetchone()
    return fullname

def get_role(username):
    conn = mysql.connector.connect(**connect.db_config)  
    cursor = conn.cursor()  
    user_query = "select role from users2 where username = %s;"
    cursor.execute(user_query,(username,))
    role = cursor.fetchone()
    return role[0]
def get_next_id():
    conn = mysql.connector.connect(**connect.db_config)  
    cursor = conn.cursor(dictionary=True)  
    id_query = """SELECT CONCAT(YEAR(CURDATE()), LPAD(MAX(CAST(SUBSTRING(username, 5, 4) AS UNSIGNED)) + 1, 4, '0')) AS next_student_no
        FROM users2
        WHERE username LIKE CONCAT(YEAR(CURDATE()), '%')
        AND username REGEXP '^[0-9]{8}$';
        """
    cursor.execute(id_query)
    next_id = cursor.fetchone()['next_student_no']
    if cursor is not None:  
        cursor.close()  
    if conn is not None:  
        conn.close()  
    return next_id

@app.route('/', methods=['GET', 'POST'])  
def index():  
    if 'username' not in flask_session:  
        return redirect(url_for('login'))  # 重定向到登录页面 
    results = []  
    message = ""  
    cursor = None  
    conn = None  
    #get user information
    username = flask_session.get('username')
    fullname = get_fullname(username)
    role = get_role(username)
    if role != "administrator":
        return redirect(url_for("subjects"))


    if request.method == 'POST':  
        # Insert data part  
        if 'insert' in request.form:  
            username = request.form.get('username_ist')  
            if not username:
                username = get_next_id()
            password = generate_password_hash(request.form['password_ist'])  # 哈希密码
            first_name = request.form.get('first_name_ist')
            last_name = request.form.get('last_name_ist')
            birth_date = request.form.get('birth_date_ist')
            email = request.form.get('email_ist')
            role = request.form.get('role_ist') 

            try:  
                conn = mysql.connector.connect(**connect.db_config)  
                cursor = conn.cursor()  

                insert_query = "INSERT INTO users2 (username,password,first_name,last_name,birth_date,register_date,email,role) VALUES (%s, %s, %s, %s,%s, %s, %s, %s)"  
                cursor.execute(insert_query, (username, password, first_name, last_name,birth_date,datetime.now().date(),email,role))  
                conn.commit()  
                message = f"Student {username} information created successfully!"  

            except mysql.connector.Error as e:  
                message = f"Database error: {e}"  

            finally:  
                if cursor is not None:  
                    cursor.close()  
                if conn is not None:  
                    conn.close()  

        # Update data part  
        if 'update' in request.form:  
            username = request.form.get('username_upd')  
            password = generate_password_hash(request.form['password_upd'])  # 哈希密码
            first_name = request.form.get('first_name_upd')
            last_name = request.form.get('last_name_upd')
            birth_date = request.form.get('birth_date_upd')
            email = request.form.get('email_upd')
            role = request.form.get('role_upd')

            try:  
                conn = mysql.connector.connect(**connect.db_config)  
                cursor = conn.cursor()  
                update_fields = []
                update_values = []
                if password:
                    update_fields.append("password = %s")
                    update_values.append(password)  
                if first_name:
                    update_fields.append("first_name = %s")
                    update_values.append(first_name)
                if last_name:
                    update_fields.append("last_name = %s")
                    update_values.append(last_name)
                if birth_date:
                    update_fields.append("birth_date = %s")
                    update_values.append(birth_date)
                if email:
                    update_fields.append("email = %s")
                    update_values.append(email)
                if role:
                    update_fields.append("role = %s")
                    update_values.append(role)

                if update_fields:
                    update_query = f"UPDATE users2 SET {', '.join(update_fields)} WHERE username = %s"
                    update_values.append(username)
                    cursor.execute(update_query, update_values)
                    conn.commit()
                    message = "Student information updated successfully!"
                else:
                    message = "No fields to update." 

            except mysql.connector.Error as e:  
                message = f"Database error: {e}"  

            finally:  
                if cursor is not None:  
                    cursor.close()  
                if conn is not None:  
                    conn.close()  
        if 'delete' in request.form:  
            student_id = request.form.get('student_del_id')  
            if not student_id:
                message = "Please select a student to delete."
            else:

                try:  
                    conn = mysql.connector.connect(**connect.db_config)  
                    cursor = conn.cursor()  

                    delete_query = "Delete from users2 WHERE username = %s"  
                    cursor.execute(delete_query, (student_id,))  
                    conn.commit()  
                    message = f"Student information {student_id} deleted successfully!"  

                except Error as e:  
                    message = f"Database error: {e}"  

                finally:  
                    if cursor is not None:  
                        cursor.close()  
                    if conn is not None:  
                        conn.close() 

    # Query data part  
    try:  
        conn = mysql.connector.connect(**connect.db_config)  
        cursor = conn.cursor(dictionary=True)  

        select_query = "SELECT username,first_name,last_name,birth_date,register_date,email,program1,role FROM users2; "  
        cursor.execute(select_query)  
        results = cursor.fetchall() 
        role_query = "select distinct(role) from users2" 
        cursor.execute(role_query)
        roles = cursor.fetchall()
        next_id = get_next_id()
        

    except Error as e:  
        message = f"Database query error: {e}"  

    finally:  
        if cursor is not None:  
            cursor.close()  
        if conn is not None:  
            conn.close()  
    
    return render_template('Index6.html', results=results, message=message, fullname=fullname, roles=roles,next_id=next_id)


def query_subjects(subject_no,subject_name, credit, dept):  
    try:  
        connection = mysql.connector.connect(**connect.db_config)  
        cursor = connection.cursor(dictionary=True)  # 使用字典游标  
        query = """  
            SELECT * FROM Lincoln_Courses 
            WHERE Credits > 0  
        """  
        params = []
        # Add conditions based on provided parameters  
        if subject_no:
            query += " AND Subject_No like %s"
            subject_no = "%" + subject_no + "%"
            params.append(subject_no)
        if subject_name:  
            query += " AND Subject_Name like %s"  
            subject_name = "%" + subject_name + "%"
            params.append(subject_name)  
        if credit:  
            query += " AND Credits= %s"  
            params.append(credit)  
        if dept:  
            query += " AND Dept = %s"  
            params.append(dept)  
        query += " ORDER BY Subject_No ASC"
        cursor.execute(query, params)  
        results = cursor.fetchall()  
        return results  
    except mysql.connector.Error as err:  
        print(f"Error: {err}")  
        return []  
    finally:  
            cursor.close()  
            connection.close()

def query_programs(program,subject_area, degree,total_credits,duration):  
    try:  
        connection = mysql.connector.connect(**connect.db_config)  
        cursor = connection.cursor(dictionary=True)  # 使用字典游标  
        query = """  
            SELECT * FROM lincoln_programs
            WHERE 1=1 
        """  
        params = []
        # Add conditions based on provided parameters  
        if program:
            query += " AND program like %s"
            program = "%" + program + "%"
            params.append(program)
        if subject_area:  
            query += " AND subject_area like %s"  
            subject_area = "%" + subject_area + "%"
            params.append(subject_area)  
        if degree:  
            query += " AND degree = %s"  
            params.append(degree)  
        if total_credits:  
            query += " AND total_credit = %s"  
            params.append(total_credits)  
        if duration:
            query += " AND duration = %s"  
            params.append(duration)  


        query += " ORDER BY program ASC"
        cursor.execute(query, params)  
        results = cursor.fetchall()  
        return results  
    except mysql.connector.Error as err:  
        print(f"Error: {err}")  
        return []  
    finally:  
            cursor.close()  
            connection.close()



def get_major(username):
    conn = mysql.connector.connect(**connect.db_config)  
    cursor = conn.cursor() 
    program_sql = 'select program1 from users2 where username = %s'
    cursor.execute(program_sql,(username,)) 
    program1 = cursor.fetchone()
    conn.close()
    cursor.close()
    return program1[0]
  

@app.route('/subjects', methods=['GET', 'POST']) 
def subjects():
    flask_session.pop('_flashes', None)
    username = flask_session.get('username')
    fullname = get_fullname(username)
    results = []  
    message = ""  
    cursor = None  
    conn = None  
    try:  
        conn = mysql.connector.connect(**connect.db_config)  
        cursor = conn.cursor(dictionary=True)  

        select_query = "select * from Lincoln_Courses where credits is not null order by Dept asc;"  
        cursor.execute(select_query)  
        results = cursor.fetchall() 

        dept_query = "select distinct(Dept) as Dept from Lincoln_Courses where Credits > 0 order by Dept ASC;"  
        cursor.execute(dept_query)  
        depts = cursor.fetchall() 

        credit_query = "select distinct(Credits) as Credits from Lincoln_Courses where credits > 0 order by Credits asc;"  
        cursor.execute(credit_query)  
        credits = cursor.fetchall()


    except Error as e:  
        message = f"Database query error: {e}"  

    finally:  
        if cursor is not None:  
            cursor.close()  
        if conn is not None:  
            conn.close()  
    if request.method == 'POST':
        if 'search' in request.form:  
            subject_no = request.form.get("Subject_No")
            subject_name = request.form.get("Subject_Name")
            credit = request.form.get("Credits")
            dept = request.form.get("Dept")
            results = []
            results = query_subjects(subject_no,subject_name,credit,dept)
        elif 'selected' in request.form:
            selected_courses = request.form.getlist('selected_courses') 
            username = flask_session.get("username")
            conn = mysql.connector.connect(**connect.db_config)  
            cursor = conn.cursor()  
            for course in selected_courses:  
                    # Check if the record already exists
                check_query = 'SELECT COUNT(*) FROM student_courses WHERE username = %s AND subject_no = %s'
                cursor.execute(check_query, (username, course))
                result = cursor.fetchone()
                if result[0] == 0:  # If the record does not exist
                    insert_query = 'INSERT INTO student_courses (username, subject_no, status) VALUES (%s, %s,"Draft")'
                    cursor.execute(insert_query, (username, course))  
            conn.commit()  # 提交事务  
            cursor.close()  
            conn.close()  # 关闭连接  
            return redirect(url_for('course_mgmt'))

    my_major = get_major(username)

    return render_template('subjects.html', results=results,depts=depts, credits=credits, message=message,fullname=fullname,username=username,my_major=my_major)

@app.route('/course_mgmt', methods=['GET', 'POST']) 
def course_mgmt():
    if 'username' not in flask_session:  
        return redirect(url_for('login'))  # 重定向到登录页面 
    results = []  
    message = ""  
    cursor = None  
    conn = None 
    username = flask_session.get("username")
    if request.method == "POST":
        
        if 'submit_course' in request.form:
            subject_no = request.form.get("subject_no")
            study_year = request.form.get("study_year")
            semester = request.form.get("semester")
            try:
                conn = mysql.connector.connect(**connect.db_config)  
                cursor = conn.cursor()  
                update_query = """ update student_courses set study_year = %s, semester = %s, status = %s where username = %s and subject_no = %s LIMIT 1;  
    """
                cursor.execute(update_query,(study_year,semester,"Submitted",username,subject_no))
                conn.commit()
            except mysql.connector.Error as err:  
                print(f"Error: {err}")
        if 'delete_course' in request.form:
            subject_no = request.form.get("subject_no")
            try: 
                conn = mysql.connector.connect(**connect.db_config)  
                cursor = conn.cursor()  

                delete_query = 'delete from student_courses where username = %s and subject_no = %s LIMIT 1;'
                cursor.execute(delete_query, (username, subject_no))  
                conn.commit()  # 提交事务  
            except mysql.connector.Error as err:  
                print(f"Error: {err}")

    try:  
        fullname = get_fullname(username)
        conn = mysql.connector.connect(**connect.db_config)  
        cursor = conn.cursor(dictionary=True)  
        select_query = """select a.subject_no, b.subject_name, b.credits, b.lecturer, b.dept, a.study_year, a.semester, a.status
        from student_courses as a inner join Lincoln_Courses as b on a.subject_no = b.subject_no where username = %s order by a.subject_no asc; """  
        cursor.execute(select_query,(username,))  
        results = cursor.fetchall() 
    except mysql.connector.Error as err:  
        print(f"Error: {err}")  
        return []  
    finally:  
        cursor.close()  
        conn.close()
    years = [datetime.now().year,datetime.now().year+1,datetime.now().year+2]


    # if request.method == "POST":
    #     if 'submit_course' or 'delete_course' in request.form:
    #         if results:
    #             send_email(username,results)
    #         else:
    #             print("Results is null")
    my_major = get_major(username)
    return render_template('course_mgmt.html', results=results, message=message, fullname=fullname,username=username,years = years,my_major=my_major)


def send_email(receiver_email, subject, body_template, results):  #*results 代表可变参数，可以传入多个结果  
    sender_email = "python.lincoln.university@outlook.com"  
    password = "66363851lk"  

    # 渲染模板  
    template = Template(body_template)  
    body = template.render(results=results)  

    # 创建MIMEText对象  
    msg = MIMEMultipart()  
    msg['From'] = sender_email  
    msg['To'] = receiver_email  
    msg['Subject'] = subject  
    msg.attach(MIMEText(body, 'html'))  

    # 连接到SMTP服务器并发送邮件  
    try:  
        with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:  
            server.starttls()  # 启用TLS加密  
            server.login(sender_email, password)  # 登录  
            server.send_message(msg)  # 发送邮件  
        return True  # 邮件发送成功  
    except Exception as e:  
        print(f"The email was not sent. Error: {e}")  
        return e  # 邮件发送失败
    
@app.route('/send_email', methods=['GET', 'POST']) 
def send_email_page():
    username = flask_session.get("username")
    #flask_session.pop('username', None)
    conn = mysql.connector.connect(**connect.db_config)  
    cursor = conn.cursor(dictionary=True)  
    select_query = """select a.subject_no, b.subject_name, b.credits, b.lecturer, b.dept, a.study_year, a.semester, a.status, b.hyper_link
    from student_courses as a inner join Lincoln_Courses as b on a.subject_no = b.subject_no where username = %s order by a.subject_no asc; """  
    cursor.execute(select_query,(username,))  
    my_courses = cursor.fetchall() 
    try:  
        select_query = "select email from users2 where username = %s"  
        cursor.execute(select_query, (username,))  
        remail = cursor.fetchone()

    except Error as e:  
        message = f"Database error: {e}"  
     
            

    program_sql = "select * from users2 as a left join lincoln_programs as b on a.program1 = b.program where a.username = %s;"
    cursor.execute(program_sql,(username,))
    my_program = cursor.fetchone()
    if cursor is not None:  
        cursor.close()
    if conn is not None:  
        conn.close()    
    fullname = get_fullname(username)
    results = []  
    results = {
        'fullname': fullname,  
         'my_program': my_program,  
         'my_courses': my_courses
    }
    # 邮件发送者和接收者
    sender_email = "python.lincoln.university@outlook.com"
    receiver_email = remail["email"]  # 替换为接收者的邮箱
    #password = "66363851lk"  # 替换为您的邮箱密码
    # 创建邮件内容
    subject = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {username} Course Selection Result'
    body_template = """
    <html>
    <head>
        <style>  
        table {  
            width: 100%;  
            border-collapse: collapse;  
        }  
        th, td {  
            padding: 12px;  
            border: 1px solid #ddd;  
            text-align: left;  
        }  
        th {  
            background-color: #f2f2f2;  
        }  
        tr:nth-child(even) {  
            background-color: #f9f9f9;  
        }  
        tr:hover {  
            background-color: #f1f1f1;  
        }  
        </style>
    </head>
    <body>
        <p>Dear {{results['fullname'][0]}} {{results['fullname'][1]}},</p>
        <p>This is your latest course information.</p>
        <p>Your major information:</p>
        <table border="1">  
            <tr>  
                <th>Program Name</th>  
                <th>Subject Area</th>  
                <th>Degree</th>  
                <th>Total Credits</th>
                <th>Duration</th>
                <th>Location</th>
                <th>Details</th>  
            </tr>   
            <tr>  
                <td>{{ results["my_program"]["program"] }}</td>  
                <td>{{ results["my_program"]["subject_area"] }}</td>  
                <td>{{ results["my_program"]["degree"] }}</td>  
                <td>{{ results["my_program"]["total_credit"] }}</td>  
                <td>{{ results["my_program"]["duration"] }}</td>  
                <td>{{ results["my_program"]["location"]}}</td>  
                <td><a href="{{results['my_program']['hyperlink'] }}"> View</a></td>  
            </tr>  
        </table> 
        <p>Your course information:</p>
        <table border="1">
        <tr>
            <th>Course No</th>
            <th>Course Name</th>
            <th>Credits</th>
            <th>Lecturer</th>
            <th>Department</th>
            <th>Study Year</th>
            <th>Semester</th>
            <th>Status</th>
            <th>details</th>
        </tr>
        {% for result in results["my_courses"] %}
        <tr>
            <td>{{ result.subject_no }}</td>
            <td>{{ result.subject_name }}</td>
            <td>{{ result.credits }}</td>
            <td>{{ result.lecturer }}</td>
            <td>{{ result.dept }}</td>
            <td>{{ result.study_year }}</td>
            <td>{{ result.semester }}</td>
            <td>{{ result.status }}</td>
            <td> <a href="{{result.hyper_link }}"> View</a></td
        </tr>
        {% endfor %}
        </table>
        <p></p>
        <p>Student Administration</p>
    </body>
    </html>
    """
    feedback = send_email(receiver_email, subject, body_template,results)  

    if feedback == True:  
        flash(f'The email has been sent successfully to {receiver_email}！', 'success')   
    else:  
        flash(f'The email was not sent. {feedback}', 'error')  

    return redirect(url_for('subjects'))  
@app.route('/login', methods=['GET', 'POST'])  
def login():  
    flask_session.pop('_flashes', None)
    if request.method == 'POST':  
        username = request.form['username']  
        password = request.form['password']  
        try:  
            connection = mysql.connector.connect(**connect.db_config)  
            cursor = connection.cursor(dictionary=True)  
            cursor.execute("SELECT * FROM users2 WHERE username = %s", (username,))  
            user = cursor.fetchone()  
            if user and check_password_hash(user['password'], password):    
                flask_session['username'] = user['username']  
                flash('Login succeed！', 'success')  
                return redirect(url_for('index'))  
            else:  
                flash('Login failed, incorrect username or password.', 'error')  
        except mysql.connector.Error as err:  
            print(f"Error: {err}")  
        finally:  
            #if connection.is_connected():  
                cursor.close()  
                connection.close()  
    return render_template('login.html')

def send_verification_code():
    username = request.form.get('username')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    receiver_email = request.form.get('email')
    # 生成验证码  
    verification_code = str(random.randint(100000, 999999))  
    flask_session['verification_code'] = verification_code  
    receiver_email = request.form['email'] 
    subject = f"Verification Code for {username}"
    results = []
    results = {
        'first_name': first_name,
        'last_name': last_name,
        'verification_code': verification_code
    }
    body_template = """
    <html>
    <head></head>
    <body>
        <p>Dear {{results['first_name'] }} {{results['last_name'] }},</p>
        <p></p>
        <p>Your verification code is: <b>{{results['verification_code'] }}.</b></p>
        <p></p>
        <p>Student Administration</p>
    </body>
    </html>
    """
    # 发送验证码邮件  
    feedback = send_email(receiver_email, subject, body_template,results) 
    if feedback == True:
        flash('Verification code sent! Please check your email to continue.', 'info')  
        return render_template('register.html')
    else:
        flash('Failed to send verification email. Please try again.', 'error') 

@app.route('/register', methods=['GET', 'POST'])  
def register():  
    if request.method == 'POST' and 'send_code' in request.form: 
        flask_session['username'] = request.form['username']  
        flask_session['password'] = request.form['password'] 
        flask_session['gender'] = request.form['gender']  
        flask_session['birth_date'] = request.form['birth_date']  
        flask_session['first_name'] = request.form['first_name']  
        flask_session['last_name'] = request.form['last_name']  
        flask_session['email'] = request.form['email']  

        # 生成验证码  
        verification_code = str(random.randint(100000, 999999))  
        flask_session['verification_code'] = verification_code  
        receiver_email = request.form['email'] 
        subject = f"Verification Code for {request.form['username'] }"
        results = []
        results = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'verification_code': verification_code
        }
        body_template = """
    <html>
    <head></head>
    <body>
        <p>Dear {{results['first_name'] }} {{results['last_name'] }},</p>
        <p></p>
        <p>Your verification code is: <b>{{results['verification_code'] }}.</b></p>
        <p></p>
        <p>Student Administration</p>
    </body>
    </html>
    """
        input_value = {} #空的字典
        input_value = {
            'username': request.form['username'],
            'password': request.form['password'],
            'gender': request.form['gender'],
            'birth_date': request.form['birth_date'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email']


        }
        # 发送验证码邮件  
        feedback = send_email(receiver_email, subject, body_template,results) 
        if feedback == True:
            flash('Verification code sent! Please check your email to continue.', 'info')  
            return render_template('register.html',input_value=input_value)
        
        else:
            flash('Failed to send verification email. Please try again.', 'error')  
            render_template('register.html',input_value=input_value)  
 

    if request.method == 'POST' and 'register' in request.form: 
        flask_session.pop('_flashes', None)
        username = request.form['username']  
        password = request.form['password']  
        #password = generate_password_hash(request.form['password'])  # 哈希密码  
        gender = request.form['gender']
        birth_date = request.form['birth_date']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        verification_code_form = request.form['verification_code']  
        verification_code_session = flask_session.get('verification_code')  
        input_value = {} #空的字典
        input_value = {
            'username': username,
            'password': password,
            'gender': gender,
            'birth_date': birth_date,
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        }
        if verification_code_form != verification_code_session:  
            flash('Verification code is incorrect, please try again.', 'error')  
            return render_template('register.html',input_value=input_value)  
        else:
            try:  
                password = generate_password_hash(password)  # 哈希密码  
                connection = mysql.connector.connect(**connect.db_config)  
                cursor = connection.cursor()  
                cursor.execute("INSERT INTO users2 (username, password, gender, birth_date, register_date, first_name, last_name, email, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (username, password, gender, birth_date, datetime.now().date(),first_name,last_name,email,"student"))  
                connection.commit()  
                flash('Register successfully, please login', 'success')  
                return redirect(url_for('login'))  
            except mysql.connector.Error as err:  
                print(f"Error: {err}")  
                flash('Registration failed, the username may already exist', 'error')  
            finally:  
                if 'connection' in locals() and connection.is_connected(): 
                    cursor.close()  
                    connection.close()
    if request.method == 'GET':
        input_value = {} #空的字典
        return render_template('register.html',input_value=input_value)

@app.route('/logout')  
def logout():  
    flask_session.pop('username', None)  
    flash("You've be successfully logout")  
    return redirect(url_for('login')) 

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    flask_session.pop('_flashes', None)
    username = flask_session.get("username")
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        new_password_confirm = request.form['new_password_confirm']

        conn = mysql.connector.connect(**connect.db_config)
        cursor = conn.cursor()
        check_sql = "SELECT password FROM users2 WHERE username = %s"
        cursor.execute(check_sql, (username,))
        result = cursor.fetchone()
        if result and not check_password_hash(result[0], old_password):
            flash('Old password is incorrect', 'error')
            return redirect(url_for('change_password'))
        elif new_password != new_password_confirm:
            flash('New passwords do not match', 'error')
            return redirect(url_for('change_password'))
        else:
            update_sql = "UPDATE users2 SET password = %s WHERE username = %s"
            cursor.execute(update_sql, (generate_password_hash(new_password), username))
            conn.commit()
            flash('Password updated successfully', 'success')
            return redirect(url_for('index'))  
  
    fullname=get_fullname(username)
    my_major = get_major(username)
    return render_template('change_password.html',username=username,fullname=fullname,my_major=my_major)


@app.route('/profile', methods=['GET', 'POST'])  
def profile_update():
    flask_session.pop('_flashes', None)
    username_login = flask_session.get("username")
    username_display = request.args.get('username')
    if username_display and username_login != username_display:
        conn = mysql.connector.connect(**connect.db_config)  
        cursor = conn.cursor()  
        get_role_sql = "SELECT role FROM users2 where username = %s"
        cursor.execute(get_role_sql,(username_login,)) 
        role = cursor.fetchone()
        if role and role[0]!= "administrator":
            flash(f"You have no permission to access {username_display}'s profile.", "danger")
        
    if request.method == 'POST':  
        username = request.form['username']  
        gender = request.form['gender']
        birth_date = request.form['birth_date']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        role = request.form['role']
        try:  
            connection = mysql.connector.connect(**connect.db_config)  
            cursor = connection.cursor()  
            update_sql = """update users2 
                            set gender = %s, birth_date = %s, first_name = %s, last_name = %s, email = %s, role = %s 
                            where username = %s"""
            cursor.execute(update_sql, (gender, birth_date, first_name,last_name,email,role,username))  
            connection.commit()  
            flash('Profile updated successfully!', 'success')  
            return redirect(url_for('index'))  
        except mysql.connector.Error as err:  
            print(f"Error: {err}")  
            flash('Update failed', 'error')  
        finally:  
                cursor.close()  
                connection.close()  

    if request.args.get('username'):
        username =  request.args.get('username')
    else:   
        username = flask_session.get("username")
    conn = mysql.connector.connect(**connect.db_config)  
    cursor = conn.cursor(dictionary=True)  

    select_query = "SELECT username,password,first_name,last_name,gender,birth_date,register_date,email,program1,role FROM users2 where username = %s; "  
    cursor.execute(select_query,(username,))  
    result = cursor.fetchone() 
    fullname = get_fullname(username_login)
    return render_template('profile.html',result=result,username=username_login,fullname=fullname,my_major=get_major(username_login))

@app.route('/programs', methods=['GET', 'POST'])  
def programs():
    # 免费版无法访问网络
    # # 设置Chrome选项
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 无头模式
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")


    # driver = webdriver.Chrome(options=chrome_options)  
    # driver.get("https://www.lincoln.ac.nz/study/study-programmes/programme-search")

    # format_str = "{: <80} {: <70} {: <50}"
    # print(format_str.format("Subject", "Program Name", "Degree"))

    # program_data = []

    # programs = WebDriverWait(driver, 1).until(
    #         EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.block.w-full.py-4.md-224\\:flex.md-224\\:items-center.text-charcoal.group.hover\\:no-underline.focus\\:no-underline"))
    # )

    #     # 提取课程名称和学位信息
    # for program in programs:
    #     subject = program.find_element(By.CSS_SELECTOR, 'div.mb-2-5.md-224\\:w-full.md-224\\:max-w-9\\/50.md-224\\:pr-7-5.md-224\\:m-0').text
    #     program_name = program.find_element(By.CSS_SELECTOR, 'span.transition-colors.duration-200.ease-in-out').text
    #     degree = program.find_element(By.CSS_SELECTOR, 'div.mt-2-5.md-224\\:w-full.md-224\\:max-w-19\\/100.md-224\\:m-0').text
    #     hyperlink = program.get_attribute('href')
        
    #     program_data.append({"Subject": subject, "Program": program_name, "Degree": degree,"Hyperlink": hyperlink})  
    # time.sleep(1)

    # for i in range(7):
    #     next_page = driver.find_element(By.XPATH, '//a[@title="View next page of results"]')
    #     next_page.click()
    #     time.sleep(1)
    #     programs = driver.find_elements(By.CSS_SELECTOR, 'a.block.w-full.py-4.md-224\\:flex.md-224\\:items-center.text-charcoal.group.hover\\:no-underline.focus\\:no-underline')
    #     for program in programs:
    #         subject = program.find_element(By.CSS_SELECTOR, 'div.mb-2-5.md-224\\:w-full.md-224\\:max-w-9\\/50.md-224\\:pr-7-5.md-224\\:m-0').text
    #         program_name = program.find_element(By.CSS_SELECTOR, 'span.transition-colors.duration-200.ease-in-out').text
    #         degree = program.find_element(By.CSS_SELECTOR, 'div.mt-2-5.md-224\\:w-full.md-224\\:max-w-19\\/100.md-224\\:m-0').text
    #         hyperlink = program.get_attribute('href')
    #         program_data.append({"Program": program_name,"Subject": subject,  "Degree": degree, "Hyperlink": hyperlink})  
    username = flask_session.get("username")
    fullname = get_fullname(username)  
    my_major = get_major(username)

    conn = mysql.connector.connect(**connect.db_config)  
    cursor = conn.cursor(dictionary=True)  
    degree_sql = "SELECT DISTINCT degree as degree FROM lincoln_programs where trim(degree) <> '' order by degree asc;"
    cursor.execute(degree_sql)
    degrees = cursor.fetchall()
    total_credits_sql = "SELECT DISTINCT total_credit FROM lincoln_programs where trim(total_credit) <> '' order by total_credit asc;"
    cursor.execute(total_credits_sql)
    total_credits_options = cursor.fetchall()
    duration_sql = "SELECT DISTINCT duration FROM lincoln_programs where trim(duration) <> '' order by duration asc;"
    cursor.execute(duration_sql)
    duration_options = cursor.fetchall()


    if request.method == 'POST':
        if 'search' in request.form:  
            program = request.form.get("program")
            subject_area = request.form.get("subject_area")
            degree = request.form.get("degree")
            total_credits = request.form.get("total_credits")
            duration = request.form.get("duration")
            program_data = query_programs(program,subject_area,degree,total_credits,duration)
        elif 'selected' in request.form:
            selected_program = request.form.get('selected_program') 
            conn = mysql.connector.connect(**connect.db_config)  
            cursor = conn.cursor()  
            update_query = 'update users2 set program1 = %s where username = %s'
            cursor.execute(update_query, (selected_program, username))  
            conn.commit()  # 提交事务  
            cursor.close()  
            conn.close()  # 关闭连接  
            return redirect(url_for('index'))

    if request.method == 'GET':
        select_query = "SELECT * FROM lincoln_programs;"  
        cursor.execute(select_query)  
        program_data = cursor.fetchall()  
    return render_template('programs.html', program_data=program_data,fullname=fullname,username=username,degrees=degrees,total_credits=total_credits_options,duration=duration_options,my_major=my_major)


if __name__ == '__main__':
    app.run()