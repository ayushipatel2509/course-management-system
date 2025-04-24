Course Management System

This project is a Course Management System built using Flask and SQLite for managing student enrollments, course schedules, prerequisites, and professor assignments.
Designed as a full-stack web application, it provides separate dashboards and role-based access for students and administrators. Students can register, enroll in
available courses, and manage their schedule, while administrators can add or edit courses, assign professors, and monitor enrollments. The system enforces critical
validations such as capacity limits, schedule conflicts, and prerequisite checks, ensuring a smooth academic experience for all users. This project demonstrates
practical skills in web development, database design, and backend logic with real-world education system requirements.

Student Functionality
- Register and log in
- Browse available courses
- Enroll in or drop courses
- View enrolled classes
- Search for courses by name
- View course prerequisites
- View professor details and their courses

Admin Functionality
- Register and log in
- Add new courses (with validation for schedule and capacity)
- Edit and delete existing courses
- View all enrolled students in each course
- Schedule management (day/time/location)
- Professor assignment with conflict detection

Database Design 
- **Students**: ID, Name, Email, Phone, GPA
- **Professors**: ID, Name, Department, Email
- **Courses**: ID, Name, Department, Description, Credits, Max Capacity
- **Prerequisites**: (CourseID → PrerequisiteID)
- **Schedule**: Day, Time, Location (validated between 08:00 and 22:00)
- **Teaching**: Maps professors to courses
- **Enrollment**: Tracks course enrollments






