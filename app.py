from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from controller import models

# expose register/verify helpers
register_student = models.register_student
register_staff = models.register_staff
register_admin = models.register_admin
verify_student = models.verify_student
verify_staff = models.verify_staff
verify_admin = models.verify_admin
init_db = models.init_db
get_all_students = models.get_all_students
get_all_staff = models.get_all_staff

# Minimal Flask app to serve the existing templates/index.html
# Run with: python app.py

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'dev-secret-key'

@app.route('/')
def index():
    return render_template('index.html')

# Ensure the SQLite database and tables exist when the app starts
init_db()


@app.route('/register_student', methods=['POST'])
def handle_register_student():
    # accept JSON (AJAX) or form-encoded submissions
    data = request.get_json() or request.form
    name = (data.get('studentName') or '').strip()
    student_id = (data.get('studentId') or '').strip()
    phone = (data.get('studentPhone') or '').strip()
    department = (data.get('studentDept') or '').strip()
    email = (data.get('studentEmail') or '').strip()
    gender = (data.get('studentGender') or '').strip()
    year = (data.get('studentYear') or '').strip()
    password = data.get('studentPassword') or ''
    confirm = data.get('studentConfirmPassword') or ''
    if password != confirm:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Password and confirm password do not match'}), 400
        flash('Password and confirm password do not match', 'error')
        return redirect(url_for('index'))
    # Use full name as first_name
    first_name = name
    username = email or student_id
    success = register_student(username=username, password=password, email=email,
                               first_name=first_name,
                               student_id=student_id, department=department, phone=phone,
                               gender=gender, year=year)
    if success:
        print(f'[app] Registered student: {username}')
        if request.is_json:
            return jsonify({'success': True, 'message': 'Student registered successfully'})
        flash('Student registered successfully', 'success')
    else:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Student registration failed (duplicate)'}), 400
        flash('Student registration failed (username or student ID may already exist)', 'error')
    return redirect(url_for('index'))


@app.route('/register_staff', methods=['POST'])
def handle_register_staff():
    data = request.get_json() or request.form
    name = (data.get('staffName') or '').strip()
    staff_id = (data.get('staffId') or '').strip()
    email = (data.get('staffEmail') or '').strip()
    phone = (data.get('staffPhone') or '').strip()
    department = (data.get('staffDept') or '').strip()
    qualification = (data.get('staffQualification') or '').strip()
    experience = (data.get('staffExperience') or '').strip()
    password = data.get('staffPassword') or ''
    confirm = data.get('staffConfirmPassword') or ''
    if password != confirm:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Password and confirm password do not match'}), 400
        flash('Password and confirm password do not match', 'error')
        return redirect(url_for('index'))
    # Use full name as first_name
    first_name = name
    username = email or staff_id
    success = register_staff(username=username, password=password, email=email,
                             first_name=first_name,
                             staff_id=staff_id, department=department, phone=phone,
                             qualification=qualification, experience=experience)
    if success:
        print(f'[app] Registered staff: {username}')
        if request.is_json:
            return jsonify({'success': True, 'message': 'Staff registered successfully'})
        flash('Staff registered successfully', 'success')
    else:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Staff registration failed (duplicate)'}), 400
        flash('Staff registration failed (username or staff ID may already exist)', 'error')
    return redirect(url_for('index'))


@app.route('/login_student', methods=['POST'])
def handle_login_student():
    data = request.get_json() or request.form
    email = (data.get('studentLoginEmail') or '').strip()
    password = data.get('studentLoginPassword') or ''
    user = verify_student(email, password)
    if user:
        print(f"[app] Student logged in: {email}")
        if request.is_json:
            return jsonify({'success': True, 'message': 'Student login successful', 'user': user})
        flash('Student login successful', 'success')
    else:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Student login failed'}), 401
        flash('Student login failed', 'error')
    return redirect(url_for('index'))


@app.route('/login_staff', methods=['POST'])
def handle_login_staff():
    data = request.get_json() or request.form
    email = (data.get('staffLoginEmail') or '').strip()
    password = data.get('staffLoginPassword') or ''
    user = verify_staff(email, password)
    if user:
        print(f"[app] Staff logged in: {email}")
        if request.is_json:
            return jsonify({'success': True, 'message': 'Staff login successful', 'user': user})
        flash('Staff login successful', 'success')
    else:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Staff login failed'}), 401
        flash('Staff login failed', 'error')
    return redirect(url_for('index'))


@app.route('/login_admin', methods=['POST'])
def handle_login_admin():
    data = request.get_json() or request.form
    email = (data.get('adminLoginEmail') or '').strip()
    password = data.get('adminLoginPassword') or ''
    user = verify_admin(email, password)
    if user:
        print(f"[app] Admin logged in: {email}")
        if request.is_json:
            return jsonify({'success': True, 'message': 'Admin login successful', 'user': user})
        flash('Admin login successful', 'success')
    else:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Admin login failed'}), 401
        flash('Admin login failed', 'error')
    return redirect(url_for('index'))


@app.route('/api/admin/students', methods=['GET'])
def get_all_students_api():
    """Get all registered students for admin dashboard"""
    students_list = get_all_students()
    return jsonify({'success': True, 'students': students_list})


@app.route('/api/admin/staff', methods=['GET'])
def get_all_staff_api():
    """Get all registered staff for admin dashboard"""
    staff_list = get_all_staff()
    return jsonify({'success': True, 'staff': staff_list})


@app.route('/api/gen_ai/generate', methods=['POST'])
def api_generate_ai():
    """Generate quiz/questions using AI - Currently disabled.
    To enable: Install google-generativeai and add API key to controller/config.py
    """
    return jsonify({
        'success': False, 
        'message': 'AI feature is currently disabled',
        'detail': 'To enable AI generation: 1) Install google-generativeai package, 2) Add GENAI_API_KEY to controller/config.py, 3) Uncomment AI code in app.py'
    }), 503


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)