import sqlite3
import sys
import bcrypt

arguments = sys.argv[1:]
count = len(arguments)

if count < 2:
    print("Usage: python3 database_setup.py <username> <password>")
    exit(1)

input("This will erase data. Press enter to continue...")

conn = sqlite3.connect('database.db')
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS students")
cur.execute("DROP TABLE IF EXISTS times")
cur.execute("DROP TABLE IF EXISTS teachers")
cur.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, studentid TEXT, name TEXT, "
            "teacher TEXT, attends INTEGER)")
cur.execute("CREATE TABLE IF NOT EXISTS times (id INTEGER PRIMARY KEY AUTOINCREMENT, studentid TEXT, time DATE)")
cur.execute("CREATE TABLE IF NOT EXISTS teachers (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, "
            "salt TEXT, is_teacher BOOLEAN)")


print("Database setup complete. Creating admin account with username", arguments[0], "and password", arguments[1])

salt = bcrypt.gensalt()
password = arguments[1].encode("utf-8")
hashed_password = bcrypt.hashpw(password, salt)

cur.execute("INSERT INTO teachers (username, password, salt, is_teacher) VALUES (?, ?, ?, FALSE)",
            [arguments[0], hashed_password, salt])
conn.commit()

print("Admin account created. You can now run the app.")
