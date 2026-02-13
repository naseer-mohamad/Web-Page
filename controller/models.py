import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Absolute DB path so all processes use the same file
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mydb.db'))


def init_db(db_path=None):
	"""Initialize SQLite database and create tables if they don't exist.

	Ensures a permanent admin account exists with the email `admin@gmail.com`.
	"""
	db = db_path or DB_PATH
	print(f"[models] init_db using database: {db}")
	conn = sqlite3.connect(db)
	cursor = conn.cursor()

	# Check if old tables exist and need migration
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
	students_exists = cursor.fetchone() is not None
	
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staff'")
	staff_exists = cursor.fetchone() is not None

	if students_exists:
		# Check if last_name column exists (old schema)
		cursor.execute("PRAGMA table_info(students)")
		columns = [col[1] for col in cursor.fetchall()]
		if 'last_name' in columns:
			# Migrate to new schema
			print("[models] Migrating students table to new schema...")
			# Remove any leftover migration table from a previous failed run
			cursor.execute('DROP TABLE IF EXISTS students_new')
			cursor.execute('''
				CREATE TABLE students_new (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					username TEXT UNIQUE NOT NULL,
					password TEXT NOT NULL,
					email TEXT NOT NULL,
					first_name TEXT NOT NULL,
					student_id TEXT UNIQUE NOT NULL,
					department TEXT NOT NULL,
					phone TEXT NOT NULL,
					gender TEXT,
					year TEXT,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
			''')
			# Insert rows from old table into new table. If an old column is missing,
			# use NULL for that value so migration works across schema variations.
			old_cols = set(columns)
			new_cols = ['id', 'username', 'password', 'email', 'first_name', 'student_id', 'department', 'phone', 'gender', 'year', 'created_at']
			select_exprs = [c if c in old_cols else 'NULL' for c in new_cols]
			cursor.execute(f"INSERT INTO students_new ({', '.join(new_cols)}) SELECT {', '.join(select_exprs)} FROM students")
			cursor.execute('DROP TABLE students')
			cursor.execute('ALTER TABLE students_new RENAME TO students')
	else:
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS students (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				username TEXT UNIQUE NOT NULL,
				password TEXT NOT NULL,
				email TEXT NOT NULL,
				first_name TEXT NOT NULL,
				student_id TEXT UNIQUE NOT NULL,
				department TEXT NOT NULL,
				phone TEXT NOT NULL,
				gender TEXT,
				year TEXT,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		''')

	if staff_exists:
		# Check if last_name or designation columns exist (old schema)
		cursor.execute("PRAGMA table_info(staff)")
		columns = [col[1] for col in cursor.fetchall()]
		if 'last_name' in columns or 'designation' in columns:
			# Migrate to new schema
			print("[models] Migrating staff table to new schema...")
			# Remove any leftover migration table from a previous failed run
			cursor.execute('DROP TABLE IF EXISTS staff_new')
			cursor.execute('''
				CREATE TABLE staff_new (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					username TEXT UNIQUE NOT NULL,
					password TEXT NOT NULL,
					email TEXT NOT NULL,
					first_name TEXT NOT NULL,
					staff_id TEXT UNIQUE NOT NULL,
					department TEXT NOT NULL,
					phone TEXT NOT NULL,
					qualification TEXT,
					experience TEXT,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
			''')
			# Insert rows from old staff table into new table, filling missing columns with NULL.
			old_cols = set(columns)
			new_cols = ['id', 'username', 'password', 'email', 'first_name', 'staff_id', 'department', 'phone', 'qualification', 'experience', 'created_at']
			select_exprs = [c if c in old_cols else 'NULL' for c in new_cols]
			cursor.execute(f"INSERT INTO staff_new ({', '.join(new_cols)}) SELECT {', '.join(select_exprs)} FROM staff")
			cursor.execute('DROP TABLE staff')
			cursor.execute('ALTER TABLE staff_new RENAME TO staff')
		
	else:
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS staff (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				username TEXT UNIQUE NOT NULL,
				password TEXT NOT NULL,
				email TEXT NOT NULL,
				first_name TEXT NOT NULL,
				staff_id TEXT UNIQUE NOT NULL,
				department TEXT NOT NULL,
				phone TEXT NOT NULL,
				qualification TEXT,
				experience TEXT,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		''')

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS admins (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT UNIQUE NOT NULL,
			password TEXT NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	''')

	# Create permanent admin user if not exists
	admin_username = 'admin@gmail.com'
	admin_password = 'admin123'
	cursor.execute('SELECT COUNT(*) FROM admins WHERE username = ?', (admin_username,))
	if cursor.fetchone()[0] == 0:
		hashed = generate_password_hash(admin_password)
		cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (admin_username, hashed))

	conn.commit()
	conn.close()


def register_student(username, password, email, first_name, student_id, department, phone, gender=None, year=None, db_path=None):
	db = db_path or DB_PATH
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	try:
		hashed = generate_password_hash(password)
		cursor.execute(
			'INSERT INTO students (username, password, email, first_name, student_id, department, phone, gender, year) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
			(username, hashed, email, first_name, student_id, department, phone, gender, year)
		)
		conn.commit()
		return True
	except sqlite3.IntegrityError:
		return False
	finally:
		conn.close()


def register_staff(username, password, email, first_name, staff_id, department, phone, qualification=None, experience=None, db_path=None):
	db = db_path or DB_PATH
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	try:
		hashed = generate_password_hash(password)
		cursor.execute(
			'INSERT INTO staff (username, password, email, first_name, staff_id, department, phone, qualification, experience) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
			(username, hashed, email, first_name, staff_id, department, phone, qualification, experience)
		)
		conn.commit()
		return True
	except sqlite3.IntegrityError:
		return False
	finally:
		conn.close()


def register_admin(username, password, db_path=None):
	db = db_path or DB_PATH
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	try:
		hashed = generate_password_hash(password)
		cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, hashed))
		conn.commit()
		return True
	except sqlite3.IntegrityError:
		return False
	finally:
		conn.close()


def verify_student(username, password, db_path=None):
	db = db_path or DB_PATH
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('SELECT id, first_name, email, password, student_id, department, phone, gender, year FROM students WHERE username = ?', (username,))
	row = cursor.fetchone()
	conn.close()
	if row and check_password_hash(row[3], password):
		return {
			'id': row[0],
			'first_name': row[1],
			'email': row[2],
			'student_id': row[4],
			'department': row[5],
			'phone': row[6],
			'gender': row[7],
			'year': row[8],
			'role': 'student'
		}
	return None


def verify_staff(username, password, db_path=None):
	db = db_path or DB_PATH
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('SELECT id, first_name, email, password, staff_id, department, phone, qualification, experience FROM staff WHERE username = ?', (username,))
	row = cursor.fetchone()
	conn.close()
	if row and check_password_hash(row[3], password):
		return {
			'id': row[0],
			'first_name': row[1],
			'email': row[2],
			'staff_id': row[4],
			'department': row[5],
			'phone': row[6],
			'qualification': row[7],
			'experience': row[8],
			'role': 'staff'
		}
	return None


def verify_admin(username, password, db_path=None):
	db = db_path or DB_PATH
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('SELECT id, password FROM admins WHERE username = ?', (username,))
	row = cursor.fetchone()
	conn.close()
	if row and check_password_hash(row[1], password):
		return {'id': row[0], 'first_name': 'Admin', 'last_name': '', 'email': username, 'role': 'admin'}
	return None


def get_student_details(student_id, db_path=None):
	db = db_path or DB_PATH
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('SELECT id, username, email, first_name, last_name, student_id, department, phone, created_at FROM students WHERE id = ?', (student_id,))
	row = cursor.fetchone()
	conn.close()
	if not row:
		return None
	return {
		'id': row[0],
		'username': row[1],
		'email': row[2],
		'first_name': row[3],
		'last_name': row[4],
		'student_id': row[5],
		'department': row[6],
		'phone': row[7],
		'created_at': row[8]
	}


def get_staff_details(staff_id, db_path=None):
	db = db_path or DB_PATH
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('SELECT id, username, email, first_name, last_name, staff_id, department, designation, phone, created_at FROM staff WHERE id = ?', (staff_id,))
	row = cursor.fetchone()
	conn.close()
	if not row:
		return None
	return {
		'id': row[0],
		'username': row[1],
		'email': row[2],
		'first_name': row[3],
		'last_name': row[4],
		'staff_id': row[5],
		'department': row[6],
		'designation': row[7],
		'phone': row[8],
		'created_at': row[9]
	}



def get_all_students(db_path=None):
	"""Get all registered students"""
	db = db_path or DB_PATH
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('SELECT id, username, email, first_name, student_id, department, phone, gender, year, created_at FROM students ORDER BY created_at DESC')
	rows = cursor.fetchall()
	conn.close()
	
	students = []
	for row in rows:
		students.append({
			'id': row[0],
			'username': row[1],
			'email': row[2],
			'first_name': row[3],
			'student_id': row[4],
			'department': row[5],
			'phone': row[6],
			'gender': row[7],
			'year': row[8],
			'created_at': row[9]
		})
	return students


def get_all_staff(db_path=None):
	"""Get all registered staff"""
	db = db_path or DB_PATH
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('SELECT id, username, email, first_name, staff_id, department, phone, qualification, experience, created_at FROM staff ORDER BY created_at DESC')
	rows = cursor.fetchall()
	conn.close()
	
	staff_list = []
	for row in rows:
		staff_list.append({
			'id': row[0],
			'username': row[1],
			'email': row[2],
			'first_name': row[3],
			'staff_id': row[4],
			'department': row[5],
			'phone': row[6],
			'qualification': row[7],
			'experience': row[8],
			'created_at': row[9]
		})
	return staff_list