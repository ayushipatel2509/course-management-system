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




SETTING UP THE PROJECT 

Step 1 : Git Clone (Copy the URL) 


<img width="1049" alt="image" src="https://github.com/user-attachments/assets/ae785321-b63f-4919-8383-f0b7b3fb0da8" />



Step 2 : Clone Repository in Pycharm


<img width="1193" alt="image" src="https://github.com/user-attachments/assets/3e2d4652-9d1d-43d2-9b6e-ba947b95e5e0" />


Step 3 : Create a virtaul environment (Recommended)

python3 -m venv myenv 


Step 4 : Activate virtual environment

source myenv/bin/activate


Step 5 : Install Packages

pip install flask


Step 6 : Run the app 

python app.py

(Click on the link and run on local machine)



   





