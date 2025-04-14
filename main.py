
import sqlite3

# Connect to local database
conn = sqlite3.connect("course_management.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Create tables if not exist
cursor.executescript("""
CREATE TABLE IF NOT EXISTS Students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    student_email TEXT UNIQUE NOT NULL,
    student_phone TEXT CHECK(student_phone NOT LIKE '%[^0-9]%'),
    gpa REAL CHECK (gpa BETWEEN 0 AND 4)

);

CREATE TABLE IF NOT EXISTS Professors (
    professor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    professor_name TEXT NOT NULL,
    department TEXT NOT NULL,
    professor_email TEXT UNIQUE NOT NULL

);

CREATE TABLE IF NOT EXISTS Courses (
    course_id TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    department TEXT NOT NULL,
    description TEXT,
    credits INTEGER CHECK (credits BETWEEN 1 AND 6),
    max_capacity INTEGER CHECK (max_capacity <= 25)
);

CREATE TABLE IF NOT EXISTS Prerequisites (
    course_id TEXT,
    prerequisite_id TEXT,
    PRIMARY KEY(course_id, prerequisite_id),
    FOREIGN KEY(course_id) REFERENCES Courses(course_id),
    FOREIGN KEY(prerequisite_id) REFERENCES Courses(course_id)
);

CREATE TABLE IF NOT EXISTS Schedule (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT NOT NULL,
    day_of_week TEXT CHECK(day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')),
    start_time TEXT CHECK (start_time >= '08:00' AND start_time <= '22:00'),
    end_time TEXT CHECK (end_time > start_time AND end_time <= '22:00'),
    location TEXT,
    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
);

CREATE TABLE IF NOT EXISTS Teaching (
    course_id TEXT,
    professor_id INTEGER,
    PRIMARY KEY(course_id, professor_id),
    FOREIGN KEY(course_id) REFERENCES Courses(course_id),
    FOREIGN KEY(professor_id) REFERENCES Professors(professor_id)
);

CREATE TABLE IF NOT EXISTS Enrollment (
    student_id INTEGER,
    course_id TEXT,
    PRIMARY KEY(student_id, course_id),
    FOREIGN KEY(student_id) REFERENCES Students(student_id),
    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
);

CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('student', 'admin')) NOT NULL,
    department TEXT  -- Only for admin; nullable for student
);

""")

print("✅ Database and tables initialized successfully.")

cursor.executescript("""
-- 🧑‍🏫 Professors
INSERT OR IGNORE INTO Professors (professor_name, department, professor_email) VALUES
('Dr. James Smith', 'Computer Science', 'jsmith@msu.edu'),
('Prof. Emily Jones', 'Computer Science', 'ejones@msu.edu'),
('Dr. Raj Patel', 'Mathematics', 'rpatel@msu.edu'),
('Dr. Olivia Williams', 'Data Science', 'owilliams@msu.edu'),
('Prof. Michael Brown', 'Cybersecurity', 'mbrown@msu.edu'),
('Dr. Sarah Taylor', 'Information Systems', 'staylor@msu.edu'),
('Prof. Robert Johnson', 'Software Engineering', 'rjohnson@msu.edu'),
('Dr. Linda Lee', 'Artificial Intelligence', 'llee@msu.edu'),
('Prof. Carlos Garcia', 'Statistics', 'cgarcia@msu.edu'),
('Dr. Ana Martinez', 'Information Technology', 'amartinez@msu.edu'),
('Prof. Kevin Clark', 'Machine Learning', 'kclark@msu.edu'),
('Dr. Laura Lewis', 'Cybersecurity', 'llewis@msu.edu'),
('Prof. Daniel Walker', 'Data Analytics', 'dwalker@msu.edu'),
('Dr. Sophia Hall', 'Computer Networks', 'shall@msu.edu'),
('Prof. Brian Allen', 'Human-Computer Interaction', 'ballen@msu.edu');



-- Students
INSERT OR IGNORE INTO Students(student_id,student_name,student_email ,student_phone,gpa) VALUES
('111','Kruti','kruti@gmail.com' , '2323232323' , 3);


-- 📘 Courses
INSERT OR IGNORE INTO Courses (course_id, course_name, department, description, credits, max_capacity) VALUES
('CS101', 'Adv Programming', 'Computer Science', 'Adv programming in Python', 3, 25),
('CS102', 'Intro to Programming', 'Computer Science', 'Basics of programming in Python', 3, 25);


-- 🔗 Prerequisites (selected only for few courses)
INSERT OR IGNORE INTO Prerequisites (course_id, prerequisite_id) VALUES
('CS102','CS101');



-- 🕒 Schedule
INSERT OR IGNORE INTO Schedule (course_id, day_of_week, start_time, end_time, location) VALUES
('CS101', 'Monday', '09:00', '10:15', 'Room 101');


-- 👨‍🏫 Teaching assignments
INSERT OR IGNORE INTO Teaching (course_id, professor_id) VALUES
('CS101', 1);


""")

conn.commit()



# ---------------------- Register New Student ----------------------
def register_student():
    print("\n🔐 Register New Student")
    name = input("Full Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    while True:
        try:
            gpa = float(input("GPA (0.0 - 4.0): "))
            if 0 <= gpa <= 4:
                break
            else:
                print("GPA must be between 0 and 4.")
        except ValueError:
            print("Invalid GPA. Try again.")

    cursor.execute("""
        INSERT INTO Students (student_name, student_email, student_phone, gpa)
        VALUES (?, ?, ?, ?)""", (name, email, phone, gpa))
    conn.commit()
    student_id = cursor.lastrowid
    print(f"✅ Registered successfully. Your student ID is {student_id}")
    return student_id


# ---------------------- Student Login ----------------------
def login():
    print("📚 Welcome to Course Management System")
    try:
        student_id = int(input("Enter your Student ID (-1 to register): "))
    except ValueError:
        print("Invalid input. Exiting.")
        return None

    if student_id == -1:
        return register_student()

    cursor.execute("SELECT * FROM Students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    if student:
        print(f"\n👋 Welcome back, {student[1]}!")
        return student_id
    else:
        print("❌ Student not found.")
        return None


# ---------------------- Main Menu ----------------------
def main_menu(student_id):
    while True:
        print("\n=== Main Menu ===")
        print("L – List Courses")
        print("E – Enroll")
        print("W – Withdraw")
        print("S – Search Courses")
        print("M – My Classes")
        print("P – Prerequisites")
        print("T – Teaching Professors")
        print("X – Exit")

        choice = input("Enter your choice: ").upper()
        if choice == 'X':
            print("👋 Exiting system.")
            break
        elif choice == 'L':
            list_courses()
        elif choice == 'E':
            enroll(student_id)
        elif choice == 'W':
            withdraw(student_id)
        elif choice == 'S':
            search_courses()
        elif choice == 'M':
            my_classes(student_id)
        elif choice == 'P':
            show_prerequisites()
        elif choice == 'T':
            show_professors()
        else:
            print("❌ Invalid choice. Try again.")


# ---------------------- L – List All Courses ----------------------
def list_courses():
    print("\n📘 All Available Courses:\n")

    query = """
    SELECT 
        c.course_id,
        c.course_name,
        c.credits,
        s.day_of_week,
        s.start_time,
        s.end_time,
        s.location,
        p.professor_name,
        GROUP_CONCAT(DISTINCT pr.prerequisite_id || ' - ' || cp.course_name) AS prerequisites
    FROM Courses c
    LEFT JOIN Schedule s ON c.course_id = s.course_id
    LEFT JOIN Teaching t ON c.course_id = t.course_id
    LEFT JOIN Professors p ON t.professor_id = p.professor_id
    LEFT JOIN Prerequisites pr ON c.course_id = pr.course_id
    LEFT JOIN Courses cp ON pr.prerequisite_id = cp.course_id
    GROUP BY 
        c.course_id, s.day_of_week, s.start_time, s.end_time, s.location, p.professor_name
    ORDER BY c.course_id;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    seen = set()

    for row in results:
        course_id = row[0]
        if course_id in seen:
            continue  # Avoid duplicates
        seen.add(course_id)

        print(f"🔹 {row[1]} ({row[0]}) - {row[2]} credits")
        print(f"   🕒 {row[3]} {row[4]} – {row[5]}")
        print(f"   📍 Location: {row[6]}")
        print(f"   👨‍🏫 Professor: {row[7] if row[7] else 'TBD'}")
        print(f"   📋 Prerequisites: {row[8] if row[8] else 'None'}\n")

# ---------------------- E – Enroll in a Course ----------------------
def enroll(student_id):
    course_id = input("Enter Course ID to enroll: ").strip().upper()

    # Already enrolled?
    cursor.execute("SELECT * FROM Enrollment WHERE student_id = ? AND course_id = ?", (student_id, course_id))
    if cursor.fetchone():
        print("❌ You are already enrolled in this course.")
        return

    # Check prerequisites
    cursor.execute("""
        SELECT prerequisite_id FROM Prerequisites 
        WHERE course_id = ? AND prerequisite_id NOT IN 
        (SELECT course_id FROM Enrollment WHERE student_id = ?)""", (course_id, student_id))
    missing = cursor.fetchall()
    if missing:
        print("❌ Missing prerequisites:")
        for prereq in missing:
            print(f" - {prereq[0]}")
        return

    # Check schedule conflicts
    cursor.execute("""
        SELECT s.day_of_week, s.start_time, s.end_time, c.course_id, c.course_name 
        FROM Schedule s
        JOIN Enrollment e ON s.course_id = e.course_id
        JOIN Courses c ON c.course_id = s.course_id
        WHERE e.student_id = ?
    """, (student_id,))
    enrolled_times = cursor.fetchall()

    cursor.execute("""
        SELECT day_of_week, start_time, end_time 
        FROM Schedule WHERE course_id = ?
    """, (course_id,))
    new_course_time = cursor.fetchone()

    if new_course_time:
        new_day, new_start, new_end = new_course_time
        for e_day, e_start, e_end, e_course_id, e_course_name in enrolled_times:
            if e_day == new_day:
                if not (e_end <= new_start or e_start >= new_end):
                    print(f"❌ Schedule conflict with {e_course_id} - {e_course_name} on {e_day} ({e_start} – {e_end})")
                    return

    # Check capacity
    cursor.execute("SELECT COUNT(*) FROM Enrollment WHERE course_id = ?", (course_id,))
    current_count = cursor.fetchone()[0]

    cursor.execute("SELECT max_capacity FROM Courses WHERE course_id = ?", (course_id,))
    capacity = cursor.fetchone()
    if capacity and current_count >= capacity[0]:
        print("❌ This course is already full.")
        return

    # Enroll student
    cursor.execute("INSERT INTO Enrollment (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
    conn.commit()
    print(f"✅ Enrolled in {course_id} successfully.")

# ---------------------- W – Withdraw from a Course ----------------------
def withdraw(student_id):
    course_id = input("Enter Course ID to withdraw: ").strip().upper()

    cursor.execute("SELECT * FROM Enrollment WHERE student_id = ? AND course_id = ?", (student_id, course_id))
    if cursor.fetchone():
        cursor.execute("DELETE FROM Enrollment WHERE student_id = ? AND course_id = ?", (student_id, course_id))
        conn.commit()
        print(f"✅ You have been withdrawn from {course_id}.")
    else:
        print("❌ You are not enrolled in that course.")


# ---------------------- S – Search Courses by Name ----------------------
def search_courses():
    keyword = input("Enter a keyword to search course names: ").strip()

    cursor.execute("""
        SELECT 
            c.course_id,
            c.course_name,
            GROUP_CONCAT(DISTINCT s.day_of_week || ' ' || s.start_time || '-' || s.end_time) AS schedule,
            GROUP_CONCAT(DISTINCT p.professor_name) AS professors
        FROM Courses c
        LEFT JOIN Schedule s ON c.course_id = s.course_id
        LEFT JOIN Teaching t ON c.course_id = t.course_id
        LEFT JOIN Professors p ON t.professor_id = p.professor_id
        WHERE c.course_name LIKE ?
        GROUP BY c.course_id, c.course_name
        ORDER BY c.course_id
    """, (f'%{keyword}%',))

    results = cursor.fetchall()

    if not results:
        print("❌ No courses match your search.")
        return

    print(f"\n🔍 Courses matching '{keyword}':\n")
    for row in results:
        print(f"📘 {row[1]} ({row[0]})")
        print(f"   🕒 Schedule: {row[2] if row[2] else 'TBD'}")
        print(f"   👨‍🏫 Professor(s): {row[3] if row[3] else 'TBD'}\n")



# ---------------------- M – My Classes ----------------------
def my_classes(student_id):
    cursor.execute("""
        SELECT 
            c.course_id, 
            c.course_name, 
            c.credits,
            GROUP_CONCAT(DISTINCT s.day_of_week || ' ' || s.start_time || '-' || s.end_time) AS schedule,
            GROUP_CONCAT(DISTINCT p.professor_name) AS professors
        FROM Enrollment e
        JOIN Courses c ON e.course_id = c.course_id
        LEFT JOIN Schedule s ON c.course_id = s.course_id
        LEFT JOIN Teaching t ON c.course_id = t.course_id
        LEFT JOIN Professors p ON t.professor_id = p.professor_id
        WHERE e.student_id = ?
        GROUP BY c.course_id
        ORDER BY c.course_id
    """, (student_id,))

    results = cursor.fetchall()

    if not results:
        print("📭 You are not enrolled in any courses.")
        return

    print("\n📚 My Enrolled Classes:\n")
    total_credits = 0
    for row in results:
        print(f"🔸 {row[1]} ({row[0]}) - {row[2]} credit(s)")
        print(f"   🕒 Schedule: {row[3] if row[3] else 'TBD'}")
        print(f"   👨‍🏫 Professor(s): {row[4] if row[4] else 'TBD'}\n")
        total_credits += row[2]

    print(f"🧮 Total Credits Enrolled: {total_credits}")


# ---------------------- P – Show Prerequisites ----------------------
def show_prerequisites():
    course_id = input("Enter Course ID to view its prerequisites: ").strip().upper()

    cursor.execute("""
        SELECT c1.course_name AS course_name, c2.course_id AS prereq_id, c2.course_name AS prereq_name
        FROM Prerequisites p
        JOIN Courses c1 ON p.course_id = c1.course_id
        JOIN Courses c2 ON p.prerequisite_id = c2.course_id
        WHERE p.course_id = ?
    """, (course_id,))

    prereqs = cursor.fetchall()

    if not prereqs:
        print("✅ This course has no prerequisites.")
        return

    print(f"\n📋 Prerequisites for {prereqs[0]['course_name']} ({course_id}):")
    for row in prereqs:
        print(f" - {row['prereq_name']} ({row['prereq_id']})")


# ---------------------- T – Teaching Professors ----------------------
def show_professors():
    cursor.execute("""
        SELECT 
            p.professor_name, 
            p.department, 
            c.course_id, 
            c.course_name,
            c.credits
        FROM Professors p
        JOIN Teaching t ON p.professor_id = t.professor_id
        JOIN Courses c ON t.course_id = c.course_id
        ORDER BY p.professor_name, c.course_id;
    """)
    results = cursor.fetchall()

    if not results:
        print("❌ No professors assigned to courses.")
        return

    current_prof = None
    total_credits = 0

    for row in results:
        prof_name, dept, course_id, course_name, credits = row

        if prof_name != current_prof:
            # Print total workload for previous professor (if not first)
            if current_prof is not None:
                print(f"   🔢 Total Workload: {total_credits} credit(s)\n")

            print(f"\n👨‍🏫 Professor: {prof_name} ({dept})")
            current_prof = prof_name
            total_credits = 0  # reset for new professor

        print(f"   • Teaches: {course_name} ({course_id}) - {credits} credit(s)")
        total_credits += credits

    # Final professor's total workload
    print(f"   🔢 Total Workload: {total_credits} credit(s)\n")

# ---------------------- App Entry Point ----------------------
def main():
    student_id = login()
    if student_id:
        main_menu(student_id)
    conn.close()


# Run the program
if __name__ == "__main__":
    main()