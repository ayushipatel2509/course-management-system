import sqlite3

# Connect to the database
conn = sqlite3.connect("course_management.db")
cursor = conn.cursor()

# Define range of student IDs to delete
student_ids = list(range(117, 131))

for student_id in student_ids:
    try:
        # Delete from Enrollment table
        cursor.execute("DELETE FROM Enrollment WHERE student_id = ?", (student_id,))

        # Delete from Students table
        cursor.execute("DELETE FROM Students WHERE student_id = ?", (student_id,))

        # Delete from Users table (assuming user_id = student_id for simplicity)
        cursor.execute("DELETE FROM Users WHERE user_id = ?", (student_id,))

        print(f"🗑️ Deleted records for student ID: {student_id}")
    except Exception as e:
        print(f"❌ Failed to delete student ID {student_id}: {e}")

# Commit changes and close connection
conn.commit()
conn.close()

print("\n✅ All deletions completed.")
