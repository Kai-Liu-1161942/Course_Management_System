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
    if role != "Admin":
        return redirect(url_for("subjects"))


    if request.method == 'POST':  
        # Insert data part  
        if 'insert' in request.form:  
            student_no = request.form.get('student_no')  
            name = request.form.get('name')  
            enrol_year = request.form.get('enrol_year_insert')  
            major = request.form.get('major_insert')  

            try:  
                conn = mysql.connector.connect(**connect.db_config)  
                cursor = conn.cursor()  

                insert_query = "INSERT INTO Student_infor (Student_No, Name, Enrol_year, Major) VALUES (%s, %s, %s, %s)"  
                cursor.execute(insert_query, (student_no, name, enrol_year, major))  
                conn.commit()  
                message = "Student information inserted successfully!"  

            except Error as e:  
                message = f"Database error: {e}"  

            finally:  
                if cursor is not None:  
                    cursor.close()  
                if conn is not None:  
                    conn.close()  

        # Update data part  
        if 'update' in request.form:  
            student_id = request.form.get('student_id')  
            name_update = request.form.get('name_update')  
            enrol_year_update = request.form.get('enrol_year_update')  
            major_update = request.form.get('major_update')  

            try:  
                conn = mysql.connector.connect(**connect.db_config)  
                cursor = conn.cursor()  

                update_query = "UPDATE Student_infor SET Name = %s, Enrol_year = %s, Major = %s WHERE Student_No = %s"  
                cursor.execute(update_query, (name_update, enrol_year_update, major_update, student_id))  
                conn.commit()  
                message = "Student information updated successfully!"  

            except Error as e:  
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

        select_query = "SELECT * FROM Student_infor"  
        cursor.execute(select_query)  
        results = cursor.fetchall()  

    except Error as e:  
        message = f"Database query error: {e}"  

    finally:  
        if cursor is not None:  
            cursor.close()  
        if conn is not None:  
            conn.close()  
    
    return render_template('Index6.html', results=results, message=message, fullname=fullname)

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

def query_sujects(subject_no,subject_name, credit, dept):  
    try:  
        connection = mysql.connector.connect(**connect.db_config)  
        cursor = connection.cursor(dictionary=True)  # 使用字典游标  
        query = """  
            SELECT * FROM lincoln_courses 
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

        select_query = "select * from lincoln_courses where credits is not null order by Dept asc;"  
        cursor.execute(select_query)  
        results = cursor.fetchall() 

        dept_query = "select distinct(Dept) as Dept from lincoln_courses where Credits > 0;"  
        cursor.execute(dept_query)  
        depts = cursor.fetchall() 

        credit_query = "select distinct(Credits) as Credits from lincoln_courses where credits > 0 order by Credits asc;"  
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
            results = query_sujects(subject_no,subject_name,credit,dept)
        elif 'selected' in request.form:
            selected_courses = request.form.getlist('selected_courses') 
            username = flask_session.get("username")
            conn = mysql.connector.connect(**connect.db_config)  
            cursor = conn.cursor()  
            for course in selected_courses:  
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
                update_query = """ update student_courses set study_year = %s, semester = %s, status = %s where username = %s and subject_no = %s;  
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

                delete_query = 'delete from student_courses where username = %s and subject_no = %s'
                cursor.execute(delete_query, (username, subject_no))  
                conn.commit()  # 提交事务  
            except mysql.connector.Error as err:  
                print(f"Error: {err}")

    try:  
        fullname = get_fullname(username)
        conn = mysql.connector.connect(**connect.db_config)  
        cursor = conn.cursor(dictionary=True)  
        select_query = """select a.subject_no, b.subject_name, b.credits, b.lecturer, b.dept, a.study_year, a.semester, a.status
        from student_courses as a inner join lincoln_courses as b on a.subject_no = b.subject_no where username = %s; """  
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
                flash('登录成功！', 'success')  
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
            flash('注册成功！请登录。', 'success')  
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
    flash('您已成功登出')  
    return redirect(url_for('login')) 


if __name__ == '__main__':
    app.run()