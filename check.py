import sqlite3

# Connect to your database
conn = sqlite3.connect("course_management.db")
cursor = conn.cursor()

# Get the list of all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("📋 Tables in the database:")
for table in tables:
    print(f" - {table[0]}")

conn.close()
