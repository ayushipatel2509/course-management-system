from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from model import get_db_connection
import sqlite3


routes = Blueprint('routes', __name__)


@routes.route('/')
def home():
    return render_template('role_selection.html')




#--------------------student register----------------------
@routes.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        name = request.form['full_name']
        student_id = request.form['student_id']
        email = request.form['email']
        phone = request.form['phone']
        gpa = request.form.get('gpa')
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash(" Passwords do not match.", "danger")
            return redirect(url_for('routes.register_student'))

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO Users (email, password, role) VALUES (?, ?, ?)",
                         (email, hashed_password, 'student'))

            conn.execute(
                "INSERT INTO Students (student_id, student_name, student_email, student_phone, gpa) VALUES (?, ?, ?, ?, ?)",
                (student_id, name, email, phone, gpa)
            )

            conn.commit()
            flash(" Registered successfully!", "success")
            return redirect(url_for('routes.login'))

        except Exception as e:
            flash(f" Registration failed: {e}", "danger")
        finally:
            conn.close()

    return render_template('register_student.html')





#------------------admin register-------------------------
@routes.route('/register/admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        department = request.form['department']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash(" Passwords do not match.", "danger")
            return redirect(url_for('routes.register_admin'))

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            # Insert login credentials
            conn.execute("INSERT INTO Users (email, password, role) VALUES (?, ?, ?)",
                         (email, hashed_password, 'admin'))

            # Insert admin profile in Professors
            conn.execute("INSERT INTO Professors (professor_name, professor_email, department) VALUES (?, ?, ?)",
                         (name, email, department))

            conn.commit()
            flash(" Admin registered successfully!", "success")
            return redirect(url_for('routes.login'))

        except Exception as e:
            flash(f" Registration failed: {e}", "danger")
        finally:
            conn.close()

    return render_template('register_admin.html')




#-------------login------------------------------------
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM Users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['email'] = user['email']
            session['role'] = user['role']

            if user['role'] == 'student':

                profile = conn.execute("SELECT student_id, student_name FROM Students WHERE student_email = ?", (email,)).fetchone()
                if profile:
                    session['user_id'] = profile['student_id']
                    session['full_name'] = profile['student_name']
                else:
                    session['user_id'] = None
                    session['full_name'] = 'Student'

                conn.close()
                return redirect(url_for('routes.student_dashboard'))

            elif user['role'] == 'admin':

                profile = conn.execute("SELECT professor_name FROM Professors WHERE professor_email = ?", (email,)).fetchone()
                session['user_id'] = user['user_id']  # Admin uses Users.user_id
                session['full_name'] = profile['professor_name'] if profile else 'Admin'

                conn.close()
                return redirect(url_for('routes.admin_dashboard'))

        conn.close()
        flash("❌ Invalid email or password.", "danger")

    return render_template("login.html")




#---------------- Logout ---------------------------------------
@routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('routes.login'))





# -----------------------admin dashboard --------------------
@routes.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('routes.login'))

    page = int(request.args.get('page', 1))
    per_page = 8
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()


    cursor.execute("SELECT COUNT(DISTINCT c.course_id) FROM Courses c")
    total_courses = cursor.fetchone()[0]
    total_pages = (total_courses + per_page - 1) // per_page


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





#--------------------------admin add course ------------------------
@routes.route('/admin/add_course', methods=['GET', 'POST'])
def add_course():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Load data for dropdowns
    cursor.execute("SELECT * FROM Professors")
    professors = cursor.fetchall()
    cursor.execute("SELECT course_id, course_name FROM Courses")
    courses = cursor.fetchall()

    if request.method == 'POST':
        # Get form inputs
        course_id = request.form['course_id']
        course_name = request.form['course_name']
        department = request.form['department']
        description = request.form.get('description') or None
        credits = request.form['credits']
        max_capacity = request.form['max_capacity']
        professor_id = request.form['professor_id']
        day_of_week = request.form['day_of_week']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        location = request.form.get('location') or None
        prerequisite_ids = request.form.getlist('prerequisite_ids')

        try:
            #  Check if course_id already exists
            cursor.execute("SELECT 1 FROM Courses WHERE course_id = ?", (course_id,))
            if cursor.fetchone():
                flash("❌ Course ID already exists.", "danger")
                return render_template("admin_add_course.html", professors=professors, courses=courses, form_data=request.form)

            #  Check for professor schedule conflict
            cursor.execute("""
                SELECT c.course_id, s.day_of_week, s.start_time, s.end_time
                FROM Teaching t
                JOIN Schedule s ON t.course_id = s.course_id
                JOIN Courses c ON c.course_id = s.course_id
                WHERE t.professor_id = ? AND s.day_of_week = ?
                  AND NOT (TIME(?) <= TIME(s.start_time) OR TIME(?) >= TIME(s.end_time))
            """, (professor_id, day_of_week, end_time, start_time))

            conflict = cursor.fetchone()
            if conflict:
                conflict_time = f"{conflict['start_time']} - {conflict['end_time']}"
                flash(f" Schedule conflict: Professor already assigned to course {conflict['course_id']} on {day_of_week} ({conflict_time}).", "danger")
                return render_template("admin_add_course.html", professors=professors, courses=courses, form_data=request.form)

            #  Insert into Courses
            cursor.execute("""
                INSERT INTO Courses (course_id, course_name, department, description, credits, max_capacity)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (course_id, course_name, department, description, credits, max_capacity))

            #  Teaching assignment
            cursor.execute("INSERT INTO Teaching (course_id, professor_id) VALUES (?, ?)", (course_id, professor_id))

            #  Schedule
            cursor.execute("""
                INSERT INTO Schedule (course_id, day_of_week, start_time, end_time, location)
                VALUES (?, ?, ?, ?, ?)
            """, (course_id, day_of_week, start_time, end_time, location))

            #  Add prerequisites (if any)
            for prereq_id in prerequisite_ids:
                if prereq_id != course_id:
                    cursor.execute("""
                        INSERT OR IGNORE INTO Prerequisites (course_id, prerequisite_id)
                        VALUES (?, ?)
                    """, (course_id, prereq_id))

            conn.commit()
            flash(" Course added successfully!", "success")
            return redirect(url_for('routes.admin_dashboard'))

        except Exception as e:
            flash(f" Error: {str(e)}", "danger")
            return render_template("admin_add_course.html", professors=professors, courses=courses, form_data=request.form)
        finally:
            conn.close()

    # GET request
    return render_template("admin_add_course.html", professors=professors, courses=courses, form_data={})





#-------------------------- Delete Course ----------------------------------
@routes.route('/admin/delete_course/<course_id>')
def delete_course(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Courses WHERE course_id = ?", (course_id,))
    conn.commit()
    conn.close()
    flash(" Course deleted!", "success")
    return redirect(url_for('routes.admin_dashboard'))





#------------------------- View Enrollments ------------------------------
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




#---------------------------admin edit course----------------------------
@routes.route('/admin/edit_course/<course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Load all professors and courses (for dropdowns)
    cursor.execute("SELECT * FROM Professors")
    professors = cursor.fetchall()
    cursor.execute("SELECT course_id, course_name FROM Courses WHERE course_id != ?", (course_id,))
    all_courses = cursor.fetchall()

    if request.method == 'POST':
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
        prerequisite_ids = request.form.getlist('prerequisite_ids')

        try:
            cursor.execute("""
                UPDATE Courses
                SET course_name = ?, department = ?, description = ?, credits = ?, max_capacity = ?
                WHERE course_id = ?
            """, (course_name, department, description, credits, max_capacity, course_id))

            cursor.execute("DELETE FROM Teaching WHERE course_id = ?", (course_id,))
            cursor.execute("INSERT INTO Teaching (course_id, professor_id) VALUES (?, ?)", (course_id, professor_id))

            cursor.execute("DELETE FROM Schedule WHERE course_id = ?", (course_id,))
            cursor.execute("""
                INSERT INTO Schedule (course_id, day_of_week, start_time, end_time, location)
                VALUES (?, ?, ?, ?, ?)
            """, (course_id, day_of_week, start_time, end_time, location))

            # Update prerequisites
            cursor.execute("DELETE FROM Prerequisites WHERE course_id = ?", (course_id,))
            for prereq_id in prerequisite_ids:
                if prereq_id != course_id:
                    cursor.execute("""
                        INSERT OR IGNORE INTO Prerequisites (course_id, prerequisite_id)
                        VALUES (?, ?)
                    """, (course_id, prereq_id))

            conn.commit()
            flash("✅ Course updated successfully!", "success")
            return redirect(url_for('routes.admin_dashboard'))
        except Exception as e:
            flash(f"❌ Update failed: {e}", "danger")
        finally:
            conn.close()

    # GET Method: Load existing course info
    cursor.execute("SELECT * FROM Courses WHERE course_id = ?", (course_id,))
    course = cursor.fetchone()

    cursor.execute("SELECT professor_id FROM Teaching WHERE course_id = ?", (course_id,))
    prof_row = cursor.fetchone()
    current_professor_id = prof_row['professor_id'] if prof_row else None

    cursor.execute("SELECT * FROM Schedule WHERE course_id = ?", (course_id,))
    schedule = cursor.fetchone()

    cursor.execute("SELECT prerequisite_id FROM Prerequisites WHERE course_id = ?", (course_id,))
    selected_prereqs = [row['prerequisite_id'] for row in cursor.fetchall()]

    conn.close()

    return render_template("admin_edit_course.html",
                           course=course,
                           professors=professors,
                           current_professor_id=current_professor_id,
                           day_of_week=schedule['day_of_week'] if schedule else '',
                           start_time=schedule['start_time'] if schedule else '',
                           end_time=schedule['end_time'] if schedule else '',
                           location=schedule['location'] if schedule else '',
                           courses=all_courses,
                           selected_prereqs=selected_prereqs)






# ------------------------------- Student Dashboard ---------------------------
@routes.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))
    return render_template('student_dashboard.html')





#----------------------------Student prerequisite--------------------
@routes.route('/student/prerequisites', methods=['GET', 'POST'])
def view_prerequisites():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT course_id, course_name FROM Courses")
    courses = cursor.fetchall()

    selected_course_id = None
    prerequisites = None
    course_details = None

    if request.method == 'POST':
        selected_course_id = request.form['course_id']

        # Full course details + professor
        cursor.execute("""
            SELECT c.*, s.day_of_week, s.start_time, s.end_time, s.location,
                   p.professor_name, p.professor_email
            FROM Courses c
            LEFT JOIN Schedule s ON c.course_id = s.course_id
            LEFT JOIN Teaching t ON c.course_id = t.course_id
            LEFT JOIN Professors p ON t.professor_id = p.professor_id
            WHERE c.course_id = ?
        """, (selected_course_id,))
        course_details = cursor.fetchone()

        # Prerequisite courses
        cursor.execute("""
            SELECT c.course_id, c.course_name
            FROM Prerequisites p
            JOIN Courses c ON p.prerequisite_id = c.course_id
            WHERE p.course_id = ?
        """, (selected_course_id,))
        prerequisites = cursor.fetchall()

    conn.close()
    return render_template('student_view_prerequisites.html',
                           courses=courses,
                           selected_course_id=selected_course_id,
                           course_details=course_details,
                           prerequisites=prerequisites)









#------------------------------ Add/Drop Course Page ---------------------
@routes.route('/student/add_drop_course', methods=['GET', 'POST'])
def add_drop_course():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))

    conn = get_db_connection()
    cursor = conn.cursor()


    page = request.args.get('page', default=1, type=int)
    per_page = 5
    offset = (page - 1) * per_page


    cursor.execute("SELECT course_id, course_name FROM Courses")
    all_courses = cursor.fetchall()

    selected_course_id = request.form.get('course_id') if request.method == 'POST' else None

    if selected_course_id:

        cursor.execute("""
            SELECT 
                c.course_id, 
                c.course_name, 
                c.department, 
                c.credits, 
                p.professor_name,
                GROUP_CONCAT(DISTINCT s.day_of_week) AS day_of_week,
                GROUP_CONCAT(DISTINCT s.start_time || '-' || s.end_time) AS time,
                GROUP_CONCAT(DISTINCT s.location) AS location,
                c.max_capacity,
                (SELECT COUNT(*) FROM Enrollment e WHERE e.course_id = c.course_id) AS current_enrolled
            FROM Courses c
            LEFT JOIN Teaching t ON c.course_id = t.course_id
            LEFT JOIN Professors p ON t.professor_id = p.professor_id
            LEFT JOIN Schedule s ON c.course_id = s.course_id
            WHERE c.course_id = ?
            GROUP BY 
                c.course_id, c.course_name, c.department, c.credits, p.professor_name, c.max_capacity
        """, (selected_course_id,))
        courses = cursor.fetchall()
        total_courses = 1
    else:

        cursor.execute("""
            SELECT 
                c.course_id, 
                c.course_name, 
                c.department, 
                c.credits, 
                p.professor_name,
                GROUP_CONCAT(DISTINCT s.day_of_week) AS day_of_week,
                GROUP_CONCAT(DISTINCT s.start_time || '-' || s.end_time) AS time,
                GROUP_CONCAT(DISTINCT s.location) AS location,
                c.max_capacity,
                (SELECT COUNT(*) FROM Enrollment e WHERE e.course_id = c.course_id) AS current_enrolled
            FROM Courses c
            LEFT JOIN Teaching t ON c.course_id = t.course_id
            LEFT JOIN Professors p ON t.professor_id = p.professor_id
            LEFT JOIN Schedule s ON c.course_id = s.course_id
            GROUP BY 
                c.course_id, c.course_name, c.department, c.credits, p.professor_name, c.max_capacity
            LIMIT ? OFFSET ?
        """, (per_page, offset))
        courses = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM Courses")
        total_courses = cursor.fetchone()[0]

    total_pages = (total_courses + per_page - 1) // per_page

    # Get enrolled course ids
    cursor.execute("SELECT course_id FROM Enrollment WHERE student_id = ?", (session['user_id'],))
    enrolled = [row['course_id'] for row in cursor.fetchall()]

    conn.close()

    return render_template(
        'student_add_drop_course.html',
        courses=courses,
        enrolled=enrolled,
        all_courses=all_courses,
        selected_course_id=selected_course_id,
        page=page,
        total_pages=total_pages
    )





#------------------- Enroll in Course ------------------
@routes.route('/student/enroll_course', methods=['POST'])
def enroll_course():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))

    course_id = request.form['add_course_id']
    student_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Already enrolled?
    cursor.execute("SELECT * FROM Enrollment WHERE student_id = ? AND course_id = ?", (student_id, course_id))
    if cursor.fetchone():
        flash(" You are already enrolled in this course.", "warning")
        conn.close()
        return redirect(url_for('routes.add_drop_course'))

    # 2. Prerequisite check
    cursor.execute("SELECT prerequisite_id FROM Prerequisites WHERE course_id = ?", (course_id,))
    prereq_ids = [row['prerequisite_id'] for row in cursor.fetchall()]

    if prereq_ids:
        cursor.execute("SELECT course_id FROM Enrollment WHERE student_id = ?", (student_id,))
        enrolled_ids = [row['course_id'] for row in cursor.fetchall()]
        missing = [pre for pre in prereq_ids if pre not in enrolled_ids]
        if missing:
            flash(" You must enroll in prerequisite course(s): " + ", ".join(missing), "danger")
            conn.close()
            return redirect(url_for('routes.add_drop_course'))

    # 3. Schedule conflict check
    cursor.execute("""
        SELECT s.day_of_week, s.start_time, s.end_time
        FROM Schedule s
        WHERE s.course_id = ?
    """, (course_id,))
    new_course_schedule = cursor.fetchall()

    cursor.execute("""
        SELECT s.day_of_week, s.start_time, s.end_time, c.course_name
        FROM Enrollment e
        JOIN Schedule s ON e.course_id = s.course_id
        JOIN Courses c ON e.course_id = c.course_id
        WHERE e.student_id = ?
    """, (student_id,))
    current_schedules = cursor.fetchall()

    for new_slot in new_course_schedule:
        new_day = new_slot['day_of_week']
        new_start = new_slot['start_time']
        new_end = new_slot['end_time']

        for existing in current_schedules:
            if new_day == existing['day_of_week']:
                exist_start = existing['start_time']
                exist_end = existing['end_time']
                existing_course = existing['course_name']

                # Check time overlap
                if not (new_end <= exist_start or new_start >= exist_end):
                    flash(f" Schedule conflict with {existing_course} on {new_day} ({exist_start}-{exist_end})", "danger")
                    conn.close()
                    return redirect(url_for('routes.add_drop_course'))

    # 4. Get course credit and capacity
    cursor.execute("SELECT credits, max_capacity FROM Courses WHERE course_id = ?", (course_id,))
    result = cursor.fetchone()
    course_credits, max_capacity = result["credits"], result["max_capacity"]

    cursor.execute("SELECT COUNT(*) FROM Enrollment WHERE course_id = ?", (course_id,))
    enrolled_count = cursor.fetchone()[0]

    if enrolled_count >= max_capacity:
        flash(" This course is already full.", "danger")
        conn.close()
        return redirect(url_for('routes.add_drop_course'))

    # 5. Check student's total credits
    cursor.execute("""
        SELECT SUM(c.credits)
        FROM Enrollment e
        JOIN Courses c ON e.course_id = c.course_id
        WHERE e.student_id = ?
    """, (student_id,))
    total_credits = cursor.fetchone()[0] or 0

    if total_credits + course_credits > 12:
        flash(f" You cannot exceed 12 total credits. You're currently at {total_credits}.", "danger")
        conn.close()
        return redirect(url_for('routes.add_drop_course'))

    # 6. Enroll the student
    cursor.execute("INSERT INTO Enrollment (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
    conn.commit()
    conn.close()

    flash(" Successfully enrolled!", "success")
    return redirect(url_for('routes.add_drop_course'))





#----------------------- Drop Course --------------------
@routes.route('/student/drop_course', methods=['POST'])
def drop_course():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))

    course_id = request.form['drop_course_id']
    student_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    #  Check if this course is a prerequisite for any other course the student is enrolled in
    cursor.execute("""
        SELECT p.course_id
        FROM Prerequisites p
        JOIN Enrollment e ON p.course_id = e.course_id
        WHERE p.prerequisite_id = ? AND e.student_id = ?
    """, (course_id, student_id))

    dependent_courses = cursor.fetchall()

    if dependent_courses:
        course_ids = [row['course_id'] for row in dependent_courses]
        flash(f" You cannot drop this course. It is a prerequisite for: {', '.join(course_ids)}", "danger")
        conn.close()
        return redirect(url_for('routes.add_drop_course'))

    #  Safe to drop
    cursor.execute("DELETE FROM Enrollment WHERE student_id = ? AND course_id = ?", (student_id, course_id))
    conn.commit()
    conn.close()

    flash("🗑️ Dropped course successfully.", "success")
    return redirect(url_for('routes.add_drop_course'))


# ----------------------- My Courses -----------------
@routes.route('/student/my_courses')
def view_my_courses():
    if session.get('role') != 'student':
        return redirect(url_for('routes.login'))

    student_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            c.course_id, 
            c.course_name, 
            c.department, 
            c.credits, 
            p.professor_name,
            GROUP_CONCAT(DISTINCT s.day_of_week) AS day_of_week,
            GROUP_CONCAT(DISTINCT s.start_time || '-' || s.end_time) AS time,
            GROUP_CONCAT(DISTINCT s.location) AS location
        FROM Enrollment e
        JOIN Courses c ON e.course_id = c.course_id
        LEFT JOIN Teaching t ON c.course_id = t.course_id
        LEFT JOIN Professors p ON t.professor_id = p.professor_id
        LEFT JOIN Schedule s ON c.course_id = s.course_id
        WHERE e.student_id = ?
        GROUP BY c.course_id
    """, (student_id,))

    enrolled_courses = cursor.fetchall()

    # Calculate total credits
    total_credits = sum(course['credits'] for course in enrolled_courses)

    conn.close()

    return render_template('student_my_courses.html', courses=enrolled_courses, total_credits=total_credits)


@routes.route('/student/professors')
def view_professors():
    if session.get('role') not in ['student', 'admin']:
        return redirect(url_for('routes.login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            p.professor_name,
            p.department,
            GROUP_CONCAT(DISTINCT c.course_name) AS courses_taught,
            GROUP_CONCAT(DISTINCT s.day_of_week || ' ' || s.start_time || '-' || s.end_time) AS schedule,
            SUM(c.credits) AS total_credits
        FROM Professors p
        LEFT JOIN Teaching t ON p.professor_id = t.professor_id
        LEFT JOIN Courses c ON t.course_id = c.course_id
        LEFT JOIN Schedule s ON c.course_id = s.course_id
        GROUP BY p.professor_id
    """)
    professors = cursor.fetchall()
    conn.close()

    return render_template("admin_view_professors.html", professors=professors)


