import sqlite3

conn = sqlite3.connect("course_management.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM Students WHERE student_id IN (111, 112, 113);")
cursor.execute("DELETE FROM Enrollment;")
cursor.execute("DELETE FROM Users;")
cursor.execute("DELETE FROM Students;")
conn.commit()



conn.close()
