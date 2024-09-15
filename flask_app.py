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

            try:  
                conn = mysql.connector.connect(**connect.db_config)  
                cursor = conn.cursor()  

                update_query = "Delete from Student_infor WHERE Student_No = %s"  
                cursor.execute(update_query, (int(student_id),))  
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

        select_query = "SELECT username,first_name,last_name,birth_date,register_date,email,role FROM users2; "  
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

@app.route('/subject', methods=['GET', 'POST']) 
def subject():

    results = []  
    message = ""  
    cursor = None  
    conn = None  

    if request.method == 'POST':  
        # Insert data part  
        if 'insert' in request.form:  
            student_no = request.form.get('student_no')  
            subject_no = request.form.get('subject_no')  
            subject_name = request.form.get('subject_name')  
            credit = request.form.get('credit')  

            try:  
                conn = mysql.connector.connect(**connect.db_config)  
                cursor = conn.cursor()  

                insert_query = "INSERT INTO Student_subject (Student_No, Subject_No, Subject_Name, Subject_Credit) VALUES (%s, %s, %s, %s)"  
                cursor.execute(insert_query, (student_no, subject_no, subject_name, credit))  
                conn.commit()  
                message = "Student subject information inserted successfully!"  

            except Error as e:  
                message = f"Database error: {e}"  

            finally:  
                if cursor is not None:  
                    cursor.close()  
                if conn is not None:  
                    conn.close()  
        if 'delete' in request.form:  
            student_no = request.form.get('student_no_del')  
            subject_no = request.form.get('subject_no_del')   

            try:  
                conn = mysql.connector.connect(**connect.db_config)  
                cursor = conn.cursor()  

                insert_query = "delete from Student_subject where Student_No = %s and Subject_No = %s"  
                cursor.execute(insert_query, (student_no, subject_no))  
                conn.commit()  
                message = "Student subject information deleted successfully!"  

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

        select_query = "SELECT * FROM Student_subject"  
        cursor.execute(select_query)  
        results = cursor.fetchall()  

    except Error as e:  
        message = f"Database query error: {e}"  

    finally:  
        if cursor is not None:  
            cursor.close()  
        if conn is not None:  
            conn.close()  
    return render_template('subject.html', results=results, message=message)

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

def query_programs(program,subject_area, degree):  
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

def send_email(username,results):

    try:  
        conn = mysql.connector.connect(**connect.db_config)  
        cursor = conn.cursor()  

        select_query = "select email from users2 where username = %s"  
        cursor.execute(select_query, (username,))  
        remail = cursor.fetchone()

    except Error as e:  
        message = f"Database error: {e}"  

    finally:  
        if cursor is not None:  
            cursor.close()  
        if conn is not None:  
            conn.close()  
    fullname = get_fullname(username)
    # 邮件发送者和接收者
    sender_email = "kevin.liu.nz@hotmail.com"
    receiver_email = remail[0]  # 替换为接收者的邮箱
    password = "66363851lk"  # 替换为您的邮箱密码
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
        <p>Dear {{fullname[0]}} {{fullname[1]}}:</p>
        <p>This is your latest course information.</p>
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
        </tr>
        {% for result in results %}
        <tr>
            <td>{{ result.subject_no }}</td>
            <td>{{ result.subject_name }}</td>
            <td>{{ result.credits }}</td>
            <td>{{ result.lecturer }}</td>
            <td>{{ result.dept }}</td>
            <td>{{ result.study_year }}</td>
            <td>{{ result.semester }}</td>
            <td>{{ result.status }}</td>
        </tr>
        {% endfor %}
        </table>
        <p></p>
        <p>Student Administration</p>
    </body>
    </html>
    """
    template = Template(body_template)
    body = template.render(results=results,fullname=fullname) 
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
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")

  

@app.route('/subjects', methods=['GET', 'POST']) 
def subjects():
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



    return render_template('subjects.html', results=results,depts=depts, credits=credits, message=message,fullname=fullname,username=username)

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


    if request.method == "POST":
        if 'submit_course' or 'delete_course' in request.form:
            if results:
                send_email(username,results)
            else:
                print("Results is null")

    return render_template('course_mgmt.html', results=results, message=message, fullname=fullname,username=username,years = years)

@app.route('/login', methods=['GET', 'POST'])  
def login():  
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
                flash('登录失败，用户名或密码不正确。', 'error')  
        except mysql.connector.Error as err:  
            print(f"Error: {err}")  
        finally:  
            #if connection.is_connected():  
                cursor.close()  
                connection.close()  
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])  
def register():  
    if request.method == 'POST':  
        username = request.form['username']  
        password = generate_password_hash(request.form['password'])  # 哈希密码  
        gender = request.form['gender']
        birth_date = request.form['birth_date']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        try:  
            connection = mysql.connector.connect(**connect.db_config)  
            cursor = connection.cursor()  
            cursor.execute("INSERT INTO users2 (username, password, gender, birth_date, register_date, first_name, last_name, email, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (username, password, gender, birth_date, datetime.now().date(),first_name,last_name,email,"student"))  
            connection.commit()  
            flash('Register successfully, please login', 'success')  
            return redirect(url_for('login'))  
        except mysql.connector.Error as err:  
            print(f"Error: {err}")  
            flash('注册失败，用户名可能已存在。', 'error')  
        finally:  
            #if connection.is_connected():  
                cursor.close()  
                connection.close()  
    return render_template('register.html')

@app.route('/logout')  
def logout():  
    flask_session.pop('username', None)  
    flash("You've be successfully logout")  
    return redirect(url_for('login')) 

@app.route('/profile', methods=['GET', 'POST'])  
def profile_update():
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

        
    username = flask_session.get("username")
    conn = mysql.connector.connect(**connect.db_config)  
    cursor = conn.cursor(dictionary=True)  

    select_query = "SELECT username,password,first_name,last_name,gender,birth_date,register_date,email,role FROM users2 where username = %s; "  
    cursor.execute(select_query,(username,))  
    result = cursor.fetchone() 

    return render_template('profile.html',result=result)

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

    conn = mysql.connector.connect(**connect.db_config)  
    cursor = conn.cursor(dictionary=True)  
    degree_sql = "SELECT DISTINCT degree as degree FROM lincoln_programs where trim(degree) <> '';"
    cursor.execute(degree_sql)
    degrees = cursor.fetchall()

    if request.method == 'POST':
        if 'search' in request.form:  
            program = request.form.get("program")
            subject_area = request.form.get("subject_area")
            degree = request.form.get("degree")
            program_data = query_programs(program,subject_area,degree)
    if request.method == 'GET':
        select_query = "SELECT * FROM lincoln_programs;"  
        cursor.execute(select_query)  
        program_data = cursor.fetchall()  
    return render_template('programs.html', program_data=program_data,fullname=fullname,username=username,degrees=degrees)


if __name__ == '__main__':
    app.run()