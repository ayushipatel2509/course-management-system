
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
('Dr. Smith', 'Computer Science', 'smith@msu.edu'),
('Dr. Jones', 'Computer Science', 'jones@msu.edu'),
('Dr. Patel', 'Mathematics', 'patel@msu.edu'),
('Dr. Williams', 'Data Science', 'williams@msu.edu'),
('Dr. Brown', 'Cybersecurity', 'brown@msu.edu');


-- Students
INSERT OR IGNORE INTO Students(student_id,student_name,student_email ,student_phone,gpa) VALUES
('111','Kruti','kruti@gmail.com' , '2323232323' , 3),
('112','Shivam','shivam@gmail.com' , '2324444443' , 4),
('113','Prachi','prachi@gmail.com' , '2786787586' , 3),
('114','Vishu','vishu@gmail.com' , '9090909090' , 2),
('115','Samarth','samarth@gmail.com' , '8877887788' , 4);


-- 📘 Courses
INSERT OR IGNORE INTO Courses (course_id, course_name, department, description, credits, max_capacity) VALUES
('CS101', 'Intro to Programming', 'Computer Science', 'Basics of programming in Python', 3, 25),
('CS102', 'Web Dev Fundamentals', 'Computer Science', 'HTML, CSS, JS basics', 3, 25),
('CS201', 'Data Structures', 'Computer Science', 'Study of data organization', 3, 25),
('CS202', 'OOP with Java', 'Computer Science', 'Object-oriented programming', 3, 25),
('CS301', 'Algorithms', 'Computer Science', 'Algorithm design and analysis', 3, 25),
('CS302', 'Operating Systems', 'Computer Science', 'Processes, threads, memory', 3, 25),
('CS303', 'Networks', 'Computer Science', 'Network protocols and architecture', 3, 25),
('CS304', 'Mobile App Dev', 'Computer Science', 'iOS and Android basics', 3, 25),
('CS401', 'Databases', 'Computer Science', 'Relational databases and SQL', 3, 25),
('CS402', 'AI Fundamentals', 'Computer Science', 'Basics of AI and ML', 3, 25),
('CS403', 'Machine Learning', 'Computer Science', 'Supervised & unsupervised learning', 3, 25),
('CS404', 'Deep Learning', 'Computer Science', 'Neural networks, CNNs', 3, 25),
('CS405', 'Computer Vision', 'Computer Science', 'Image processing and vision', 3, 25),
('CS406', 'Cloud Computing', 'Computer Science', 'AWS, Azure, cloud services', 3, 25),
('CS407', 'Software Engineering', 'Computer Science', 'Agile, testing, SDLC', 3, 25),
('CS408', 'Full Stack Dev', 'Computer Science', 'React, Flask, APIs', 3, 25),
('DS101', 'Intro to Data Science', 'Data Science', 'Data analysis and visualization', 3, 25),
('DS201', 'Big Data Analytics', 'Data Science', 'Hadoop, Spark, MapReduce', 3, 25),
('DS202', 'Data Wrangling', 'Data Science', 'Data cleaning techniques', 3, 25),
('DS301', 'Predictive Analytics', 'Data Science', 'Regression, forecasting', 3, 25),
('DS302', 'Data Ethics', 'Data Science', 'Privacy, fairness, ethics', 3, 25),
('CS409', 'Cybersecurity Basics', 'Cybersecurity', 'Threats and attacks', 3, 25),
('CS410', 'Cryptography', 'Cybersecurity', 'Encryption techniques', 3, 25),
('CS411', 'Ethical Hacking', 'Cybersecurity', 'Penetration testing', 3, 25),
('MATH101', 'Discrete Math', 'Mathematics', 'Logic, proofs, sets', 3, 25),
('CS501', 'Advanced Web Dev', 'Computer Science', 'Advanced HTML, CSS, JS, Node.js', 3, 25),
('CS502', 'Advanced Data Structures', 'Computer Science', 'Heaps, Tries, AVL Trees', 3, 25),
('CS503', 'Advanced Algorithms', 'Computer Science', 'Dynamic Programming, Greedy', 3, 25),
('DS401', 'Advanced Machine Learning', 'Data Science', 'XGBoost, Ensemble models', 3, 25),
('CS504', 'Parallel Computing', 'Computer Science', 'Multithreading, GPUs', 3, 25),
('CS999', 'Hacking 101', 'Cybersecurity', 'Ethical Hacking Basics', 3, 25),
('CS998', 'Intro to VR', 'Computer Science', 'VR app development', 3, 25);

-- 🔗 Prerequisites (selected only for few courses)
INSERT OR IGNORE INTO Prerequisites (course_id, prerequisite_id) VALUES
('CS201', 'CS101'),
('CS201', 'CS411'),
('CS202', 'CS401'),
('CS202', 'CS504'),
('CS302', 'CS201'),
('CS303', 'CS201'),
('CS401', 'CS201'),
('CS402', 'CS301'),
('CS403', 'CS402'),
('CS404', 'CS403'),
('CS405', 'CS403'),
('CS408', 'CS102'),
('DS201', 'DS101'),
('DS301', 'DS201');

-- 🕒 Schedule
INSERT OR IGNORE INTO Schedule (course_id, day_of_week, start_time, end_time, location) VALUES
('CS101', 'Monday', '09:00', '10:15', 'Room 101'),
('CS102', 'Tuesday', '10:30', '11:45', 'Room 102'),
('CS201', 'Wednesday', '12:00', '13:15', 'Room 103'),
('CS202', 'Thursday', '13:30', '14:45', 'Room 104'),
('CS301', 'Friday', '15:00', '16:15', 'Room 105'),
('CS302', 'Monday', '09:00', '10:15', 'Room 106'),
('CS303', 'Tuesday', '10:30', '11:45', 'Room 107'),
('CS304', 'Wednesday', '12:00', '13:15', 'Room 108'),
('CS401', 'Thursday', '13:30', '14:45', 'Room 109'),
('CS402', 'Friday', '15:00', '16:15', 'Room 110'),
('CS403', 'Monday', '09:00', '10:15', 'Room 111'),
('CS404', 'Tuesday', '10:30', '11:45', 'Room 112'),
('CS405', 'Wednesday', '12:00', '13:15', 'Room 113'),
('CS406', 'Thursday', '13:30', '14:45', 'Room 114'),
('CS407', 'Friday', '15:00', '16:15', 'Room 115'),
('CS408', 'Monday', '09:00', '10:15', 'Room 116'),
('DS101', 'Tuesday', '10:30', '11:45', 'Room 117'),
('DS201', 'Wednesday', '12:00', '13:15', 'Room 118'),
('DS202', 'Thursday', '13:30', '14:45', 'Room 119'),
('DS301', 'Friday', '15:00', '16:15', 'Room 120'),
('DS302', 'Monday', '09:00', '10:15', 'Room 121'),
('CS409', 'Tuesday', '10:30', '11:45', 'Room 122'),
('CS410', 'Wednesday', '12:00', '13:15', 'Room 123'),
('CS411', 'Thursday', '13:30', '14:45', 'Room 124'),
('MATH101', 'Friday', '15:00', '16:15', 'Room 125'),
('CS999', 'Monday', '09:00', '10:15', 'Room 999'),
('CS998', 'Monday', '09:00', '10:15', 'Room 998');

-- 👨‍🏫 Teaching assignments
INSERT OR IGNORE INTO Teaching (course_id, professor_id) VALUES
('CS101', 1),
('CS102', 1),
('CS201', 1),
('CS202', 1),
('CS301', 2),
('CS302', 2),
('CS303', 2),
('CS304', 2),
('CS401', 2),
('CS402', 3),
('CS403', 3),
('CS404', 3),
('CS405', 3),
('CS406', 3),
('CS407', 3),
('CS408', 1),
('DS101', 4),
('DS201', 4),
('DS202', 4),
('DS301', 4),
('DS302', 4),
('CS409', 5),
('CS410', 5),
('CS411', 5),
('MATH101', 3);
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