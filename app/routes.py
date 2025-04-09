from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from model import get_db_connection
import sqlite3

routes = Blueprint('routes', __name__)


@routes.route('/')
def home():
    return redirect(url_for('routes.register'))


#---------- Registration Page -------------------
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        role = request.form['role']
        department = request.form['department'] if role == 'admin' else None

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO Users (full_name, email, phone, password, role, department)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (full_name, email, phone, hashed_password, role, department))
            conn.commit()
            flash('Registered successfully!', 'success')
            return redirect(url_for('routes.login'))
        except Exception as e:
            flash(f'Registration failed: {e}', 'danger')
        finally:
            conn.close()
    return render_template('register.html')


#---------------- Login -------------------------------
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM Users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['role'] = user['role']
            session['full_name'] = user['full_name']

            if user['role'] == 'admin':
                return redirect(url_for('routes.admin_dashboard'))
            else:
                return redirect(url_for('routes.student_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')


#---------------- Logout ---------------------------------------
@routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('routes.login'))


# -----admin dashboard --------------------
@routes.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('routes.login'))

    page = int(request.args.get('page', 1))
    per_page = 8
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    # Total courses
    cursor.execute("SELECT COUNT(DISTINCT c.course_id) FROM Courses c")
    total_courses = cursor.fetchone()[0]
    total_pages = (total_courses + per_page - 1) // per_page

    # Main query with deduplicated rows using GROUP BY
    cursor.execute("""
        SELECT 
            c.course_id, 
            c.course_name, 
            c.department, 
            c.credits, 
            p.professor_name,
            GROUP_CONCAT(DISTINCT s.day_of_week) AS days,
            GROUP_CONCAT(DISTINCT s.start_time || '-' || s.end_time) AS times,
            GROUP_CONCAT(DISTINCT s.location) AS locations
        FROM Courses c
        LEFT JOIN Teaching t ON c.course_id = t.course_id
        LEFT JOIN Professors p ON t.professor_id = p.professor_id
        LEFT JOIN Schedule s ON c.course_id = s.course_id
        GROUP BY c.course_id, c.course_name, c.department, c.credits, p.professor_name
        ORDER BY c.course_id
        LIMIT ? OFFSET ?
    """, (per_page, offset))

    courses = cursor.fetchall()
    conn.close()

    return render_template(
        'admin_dashboard.html',
        courses=courses,
        page=page,
        total_pages=total_pages
    )



#--------admin add course-----------------------
@routes.route('/admin/add_course', methods=['GET', 'POST'])
def add_course():
    conn = sqlite3.connect("course_management.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        course_id = request.form['course_id']
        course_name = request.form['course_name']
        department = request.form['department']
        description = request.form['description']
        credits = request.form['credits']
        max_capacity = request.form['max_capacity']
        professor_id = request.form['professor_id']

        # New fields for schedule
        day_of_week = request.form['day_of_week']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        location = request.form['location']


        try:
            # Insert into Courses
            cursor.execute("""
                INSERT INTO Courses (course_id, course_name, department, description, credits, max_capacity)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (course_id, course_name, department, description, credits, max_capacity))

            # Insert into Teaching
            cursor.execute("""
                INSERT INTO Teaching (course_id, professor_id)
                VALUES (?, ?)
            """, (course_id, professor_id))

            # Insert into Schedule
            cursor.execute("""
                INSERT INTO Schedule (course_id, day_of_week, start_time, end_time, location)
                VALUES (?, ?, ?, ?, ?)
            """, (course_id, day_of_week, start_time, end_time, location))


            conn.commit()
            flash("✅ Course added successfully with schedule!", "success")
            return redirect(url_for('routes.admin_dashboard'))

        except Exception as e:
            flash(f"❌ Error: {e}", "danger")
        finally:
            conn.close()

    # Re-open connection to get professors list
    conn = sqlite3.connect("course_management.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Professors")
    professors = cursor.fetchall()
    conn.close()

    return render_template("admin_add_course.html", professors=professors)

#-------------- Delete Course ----------------------------------
@routes.route('/admin/delete_course/<course_id>')
def delete_course(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Courses WHERE course_id = ?", (course_id,))
    conn.commit()
    conn.close()
    flash("🗑️ Course deleted!", "success")
    return redirect(url_for('routes.admin_dashboard'))


#-------------- View Enrollments ------------------------------
@routes.route('/admin/enrollments/<course_id>')
def view_enrollments(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.student_id, s.student_name, s.student_email
        FROM Enrollment e
        JOIN Students s ON e.student_id = s.student_id
        WHERE e.course_id = ?
    """, (course_id,))
    students = cursor.fetchall()
    conn.close()
    return render_template('enrolled_students.html', course_id=course_id, students=students)



#--------------admin edit course----------------------------
@routes.route('/admin/edit_course/<course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get form values
        course_name = request.form['course_name']
        department = request.form['department']
        description = request.form['description']
        credits = request.form['credits']
        max_capacity = request.form['max_capacity']
        professor_id = request.form['professor_id']
        day_of_week = request.form['day_of_week']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        location = request.form['location']

        # Update Courses
        cursor.execute("""
            UPDATE Courses
            SET course_name = ?, department = ?, description = ?, credits = ?, max_capacity = ?
            WHERE course_id = ?
        """, (course_name, department, description, credits, max_capacity, course_id))

        # Update Teaching
        cursor.execute("DELETE FROM Teaching WHERE course_id = ?", (course_id,))
        cursor.execute("INSERT INTO Teaching (course_id, professor_id) VALUES (?, ?)", (course_id, professor_id))

        # Update Schedule
        cursor.execute("DELETE FROM Schedule WHERE course_id = ?", (course_id,))
        cursor.execute("""
            INSERT INTO Schedule (course_id, day_of_week, start_time, end_time, location)
            VALUES (?, ?, ?, ?, ?)
        """, (course_id, day_of_week, start_time, end_time, location))

        cursor.execute("SELECT course_id, course_name FROM Courses WHERE course_id != ?", (course_id,))
        all_courses = cursor.fetchall()

        conn.commit()
        conn.close()
        flash("✅ Course updated successfully!", "success")
        return redirect(url_for('routes.admin_dashboard'))

    # GET method
    # Fetch course info
    cursor.execute("SELECT * FROM Courses WHERE course_id = ?", (course_id,))
    course = cursor.fetchone()

    # Fetch current professor
    cursor.execute("SELECT professor_id FROM Teaching WHERE course_id = ?", (course_id,))
    prof_row = cursor.fetchone()
    current_professor_id = prof_row['professor_id'] if prof_row else None

    # Fetch schedule
    cursor.execute("SELECT * FROM Schedule WHERE course_id = ?", (course_id,))
    schedule = cursor.fetchone()

    # Fetch professor list
    cursor.execute("SELECT * FROM Professors")
    professors = cursor.fetchall()

    conn.close()

    return render_template("admin_edit_course.html",
                           course=course,
                           professors=professors,
                           current_professor_id=current_professor_id,
                           day_of_week=schedule['day_of_week'] if schedule else '',
                           start_time=schedule['start_time'] if schedule else '',
                           end_time=schedule['end_time'] if schedule else '',
                           location=schedule['location'] if schedule else '')

# ---------------- Student Dashboard ---------------------------
@routes.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))
    return render_template('student_dashboard.html')

@routes.route('/student/prerequisites', methods=['GET', 'POST'])
def view_prerequisites():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT course_id, course_name FROM Courses")
    courses = cursor.fetchall()

    prerequisites = None
    selected_course_id = None

    if request.method == 'POST':
        selected_course_id = request.form['course_id']
        cursor.execute("SELECT prerequisite_id FROM Prerequisites WHERE course_id = ?", (selected_course_id,))
        prerequisites = cursor.fetchall()

    conn.close()
    return render_template('student_view_prerequisites.html',
                           courses=courses,
                           prerequisites=prerequisites,
                           selected_course_id=selected_course_id)



@routes.route('/student/grades')
def view_grades():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))
    return "<h3>Grades view coming soon!</h3>"


#---------- Add/Drop Course Page ----------
@routes.route('/student/add_drop_course')
def add_drop_course():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.*, p.professor_name 
        FROM Courses c
        LEFT JOIN Teaching t ON c.course_id = t.course_id
        LEFT JOIN Professors p ON t.professor_id = p.professor_id
    """)
    courses = cursor.fetchall()

    cursor.execute("SELECT course_id FROM Enrollment WHERE student_id = ?", (session['user_id'],))
    enrolled = [row['course_id'] for row in cursor.fetchall()]

    conn.close()
    return render_template('student_add_drop_course.html', courses=courses, enrolled=enrolled)


#---------- Enroll in Course ----------
@routes.route('/student/enroll_course', methods=['POST'])
def enroll_course():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))

    course_id = request.form['add_course_id']
    student_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Enrollment WHERE student_id = ? AND course_id = ?", (student_id, course_id))
    if cursor.fetchone():
        flash("You are already enrolled in this course.", "warning")
    else:
        cursor.execute("INSERT INTO Enrollment (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
        conn.commit()
        flash("✅ Successfully enrolled!", "success")

    conn.close()
    return redirect(url_for('routes.add_drop_course'))


#---------- Drop Course ----------
@routes.route('/student/drop_course', methods=['POST'])
def drop_course():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))

    course_id = request.form['drop_course_id']
    student_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Enrollment WHERE student_id = ? AND course_id = ?", (student_id, course_id))
    conn.commit()
    conn.close()

    flash("🗑️ Dropped course successfully.", "success")
    return redirect(url_for('routes.add_drop_course'))


@routes.route('/student/my_courses')
def view_my_courses():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))

    student_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.course_id, c.course_name, c.department, c.credits, p.professor_name
        FROM Enrollment e
        JOIN Courses c ON e.course_id = c.course_id
        LEFT JOIN Teaching t ON c.course_id = t.course_id
        LEFT JOIN Professors p ON t.professor_id = p.professor_id
        WHERE e.student_id = ?
    """, (student_id,))
    enrolled_courses = cursor.fetchall()
    conn.close()

    return render_template('student_my_courses.html', courses=enrolled_courses)
