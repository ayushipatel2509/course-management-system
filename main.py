
import sqlite3

# Connect to local database
conn = sqlite3.connect("course_management.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Create tables if not exist
cursor.executescript("""
CREATE TABLE IF NOT EXISTS Students (
    student_id INTEGER PRIMARY KEY ,
    student_name TEXT NOT NULL,
    student_email TEXT UNIQUE NOT NULL,
    student_phone TEXT CHECK(student_phone NOT LIKE '%[^0-9]%'),
    gpa REAL CHECK (gpa BETWEEN 0 AND 4)

);

CREATE TABLE IF NOT EXISTS Professors (
    professor_id INTEGER PRIMARY KEY AUTOINCREMENT ,
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
    schedule_id INTEGER PRIMARY KEY ,
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
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('student', 'admin')) NOT NULL
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

