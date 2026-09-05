import os
import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from configuration import Config
from extent import db, login_manager
from model import User, Student, PlacementDrive, PredictionHistory

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ML_DIR = os.path.join(BASE_DIR, 'ML')

def create_app():
    app = Flask(
        __name__,
        template_folder='HTMLs',
        static_folder='CSS',
        static_url_path='/static'
    )
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

app = create_app()

# --------------------------------------------------------------------------
# ML Model Loading & Prediction Helper
# --------------------------------------------------------------------------
_models_cache = {}

def get_ml_resources():
    if not _models_cache:
        try:
            with open(os.path.join(ML_DIR, 'scaler.pkl'), 'rb') as f:
                _models_cache['scaler'] = pickle.load(f)
            with open(os.path.join(ML_DIR, 'placement_rf.pkl'), 'rb') as f:
                _models_cache['rf'] = pickle.load(f)
        except Exception as e:
            print(f"ML Resources not ready: {e}")
    return _models_cache


def generate_recommendations(data, is_placed, prob):
    recommendations = []

    # Aptitude Check
    if data['etest_p'] < 70.0:
        recommendations.append({
            'title': 'Strengthen Quantitative & Logical Aptitude',
            'description': f"Current aptitude score is {data['etest_p']}%. Target 75%+ to clear preliminary company screening rounds.",
            'priority_class': 'priority-high',
            'color': 'danger',
            'icon': 'bi-calculator'
        })
    else:
        recommendations.append({
            'title': 'Aptitude Screening Ready',
            'description': f"Strong aptitude score ({data['etest_p']}%). Continue maintaining speed with timed mock tests.",
            'priority_class': 'priority-low',
            'color': 'success',
            'icon': 'bi-check-circle'
        })

    # Coding Assessment Check
    if data['coding_score'] < 72.0:
        recommendations.append({
            'title': 'Elevate Data Structures & Algorithms Practice',
            'description': f"Coding evaluation score is {data['coding_score']}%. Practice medium-level LeetCode / HackerRank problems.",
            'priority_class': 'priority-high',
            'color': 'danger',
            'icon': 'bi-code-slash'
        })
    else:
        recommendations.append({
            'title': 'Strong Coding Assessment Score',
            'description': f"Coding score ({data['coding_score']}%) meets technical hiring benchmarks for tier-1 IT & Product firms.",
            'priority_class': 'priority-low',
            'color': 'success',
            'icon': 'bi-award'
        })

    # Internships Check
    if data['internships'] == 0:
        recommendations.append({
            'title': 'Gain Industry Internship or Live Project Experience',
            'description': 'Candidates with at least 1 industry internship have an 82% higher placement conversion rate.',
            'priority_class': 'priority-med',
            'color': 'warning',
            'icon': 'bi-briefcase'
        })

    # Projects Check
    if data['projects_count'] < 2:
        recommendations.append({
            'title': 'Build Full-Stack / Capstone Projects',
            'description': 'Develop 2-3 end-to-end deployed portfolio projects highlighting practical problem-solving skills.',
            'priority_class': 'priority-med',
            'color': 'warning',
            'icon': 'bi-folder-check'
        })

    # Academic CGPA Check
    if data['degree_p'] < 65.0:
        recommendations.append({
            'title': 'Academic CGPA Criteria Warning',
            'description': f"Degree score of {data['degree_p']}% is below certain recruiter cutoffs (typically 65-70%).",
            'priority_class': 'priority-high',
            'color': 'danger',
            'icon': 'bi-exclamation-octagon'
        })

    # General Interview Guidance
    if is_placed:
        recommendations.append({
            'title': 'Focus on Mock Technical & HR Interviews',
            'description': 'Review system design concepts and behavioral questions to maximize high-tier CTC offers.',
            'priority_class': 'priority-low',
            'color': 'primary',
            'icon': 'bi-person-video3'
        })

    return recommendations

# --------------------------------------------------------------------------
# Database Seeder Function
# --------------------------------------------------------------------------
def seed_database():
    with app.app_context():
        db.create_all()

        # Seed Users
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@college.edu', role='Admin')
            admin.set_password('admin123')
            db.session.add(admin)

        if not User.query.filter_by(username='student1').first():
            student_user = User(username='student1', email='student@college.edu', role='Student')
            student_user.set_password('student123')
            db.session.add(student_user)

        # Seed Sample Students from CSV if table is empty
        if Student.query.count() == 0:
            csv_file = os.path.join(ML_DIR, 'placement_data.csv')
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                depts_map = {'Sci&Tech': 'Computer Science', 'Comm&Mgmt': 'Management & Finance', 'Others': 'Mechanical Engg'}
                for idx, row in df.head(120).iterrows():
                    st = Student(
                        roll_no=f"STU-2026-{idx+1:03d}",
                        name=f"Student Candidate {idx+1}",
                        gender=row['gender'],
                        ssc_p=float(row['ssc_p']),
                        hsc_p=float(row['hsc_p']),
                        degree_p=float(row['degree_p']),
                        degree_t=row['degree_t'],
                        department=depts_map.get(row['degree_t'], 'Computer Science'),
                        work_exp=row['work_exp'],
                        etest_p=float(row['etest_p']),
                        coding_score=float(row['coding_score']),
                        soft_skills_score=float(row['soft_skills_score']),
                        internships=int(row['internships']),
                        projects_count=int(row['projects_count']),
                        status=row['status'],
                        salary=float(row['salary'])
                    )
                    db.session.add(st)

        # Seed Sample Drives
        if PlacementDrive.query.count() == 0:
            sample_drives = [
                PlacementDrive(company_name='Google India', job_role='Associate Software Engineer', package_offered=18.5, min_cgpa=75.0, eligible_branches='CSE, IT, ECE', drive_date=date(2026, 9, 15), status='Upcoming'),
                PlacementDrive(company_name='Microsoft IDC', job_role='Software Engineer - Cloud', package_offered=16.0, min_cgpa=72.0, eligible_branches='CSE, IT, AI&DS', drive_date=date(2026, 9, 22), status='Upcoming'),
                PlacementDrive(company_name='Amazon Development Center', job_role='SDE-1', package_offered=14.5, min_cgpa=70.0, eligible_branches='CSE, IT, ECE', drive_date=date(2026, 9, 28), status='Upcoming'),
                PlacementDrive(company_name='Deloitte USI', job_role='Technology Consultant / Analyst', package_offered=8.2, min_cgpa=65.0, eligible_branches='All Streams', drive_date=date(2026, 10, 5), status='Upcoming'),
                PlacementDrive(company_name='Tata Consultancy Services (TCS)', job_role='TCS Digital & Prime Specialist', package_offered=7.5, min_cgpa=60.0, eligible_branches='All Streams', drive_date=date(2026, 8, 20), status='Ongoing'),
                PlacementDrive(company_name='Infosys Limited', job_role='Systems Engineer Specialist', package_offered=6.5, min_cgpa=60.0, eligible_branches='All Streams', drive_date=date(2026, 8, 10), status='Completed'),
            ]
            db.session.add_all(sample_drives)

        db.session.commit()
        print("Database initialized and pre-seeded successfully!")

# --------------------------------------------------------------------------
# Core Routes
# --------------------------------------------------------------------------

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        selected_role = request.form.get('role', 'Admin')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Verify role matching
            if selected_role in ['Admin', 'TPO'] and user.role not in ['Admin', 'TPO']:
                flash('Access Denied: This account is registered as a Student. Please select the "Student" role to log in.', 'danger')
                return render_template('login.html')
            elif selected_role == 'Student' and user.role != 'Student':
                flash('Access Denied: This account is registered as Administrator/TPO. Please select the "Administrator / TPO" role to log in.', 'danger')
                return render_template('login.html')

            login_user(user)
            flash(f'Welcome back, {user.username}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Use demo credentials below.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role', 'Student')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different username.', 'warning')
            return render_template('register.html')

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    total_students = Student.query.count() or 1
    placed_students = Student.query.filter_by(status='Placed').all()
    placed_count = len(placed_students)
    placement_rate = round((placed_count / total_students) * 100, 1)

    salaries = [s.salary for s in placed_students if s.salary and s.salary > 0]
    avg_salary = round(sum(salaries) / len(salaries), 1) if salaries else 0.0
    max_salary = max(salaries) if salaries else 0.0

    active_drives_count = PlacementDrive.query.filter(PlacementDrive.status.in_(['Upcoming', 'Ongoing'])).count()
    upcoming_drives = PlacementDrive.query.filter_by(status='Upcoming').order_by(PlacementDrive.drive_date.asc()).limit(5).all()

    # Department-wise breakdown for Chart.js
    departments = ['Computer Science', 'Management & Finance', 'Mechanical Engg']
    dept_names = ['Computer Science', 'Mgmt & Finance', 'Mechanical Engg']
    dept_placed = []
    dept_unplaced = []

    for d in departments:
        p = Student.query.filter_by(department=d, status='Placed').count()
        u = Student.query.filter(Student.department == d, Student.status != 'Placed').count()
        dept_placed.append(p)
        dept_unplaced.append(u)

    return render_template(
        'dashboard.html',
        total_students=total_students,
        placed_count=placed_count,
        placement_rate=placement_rate,
        avg_salary=avg_salary,
        max_salary=max_salary,
        active_drives_count=active_drives_count,
        upcoming_drives=upcoming_drives,
        dept_names=dept_names,
        dept_placed=dept_placed,
        dept_unplaced=dept_unplaced
    )


@app.route('/analytics')
@login_required
def analytics():
    students = Student.query.all()
    
    # Department rates & salaries
    departments = ['Computer Science', 'Management & Finance', 'Mechanical Engg']
    dept_rates = []
    dept_salaries = []

    for d in departments:
        dept_stus = [s for s in students if s.department == d]
        total_d = len(dept_stus) or 1
        placed_d = [s for s in dept_stus if s.status == 'Placed']
        dept_rates.append(round((len(placed_d) / total_d) * 100, 1))
        
        sal_d = [s.salary for s in placed_d if s.salary > 0]
        dept_salaries.append(round(sum(sal_d) / len(sal_d), 1) if sal_d else 0.0)

    # CGPA vs Placement Tier
    cgpa_bins = ['50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
    cgpa_rates = []
    for low, high in [(50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]:
        bin_stus = [s for s in students if low <= s.degree_p < high]
        total_b = len(bin_stus) or 1
        placed_b = len([s for s in bin_stus if s.status == 'Placed'])
        cgpa_rates.append(round((placed_b / total_b) * 100, 1))

    # Scatter points for Aptitude vs Coding
    placed_scatter = [{'x': round(s.etest_p, 1), 'y': round(s.coding_score, 1)} for s in students if s.status == 'Placed'][:40]
    unplaced_scatter = [{'x': round(s.etest_p, 1), 'y': round(s.coding_score, 1)} for s in students if s.status != 'Placed'][:40]

    # Internship Impact
    internship_rates = []
    for intern_cnt in [0, 1, 2, 3]:
        if intern_cnt < 3:
            istus = [s for s in students if s.internships == intern_cnt]
        else:
            istus = [s for s in students if s.internships >= 3]
        tot_i = len(istus) or 1
        pl_i = len([s for s in istus if s.status == 'Placed'])
        internship_rates.append(round((pl_i / tot_i) * 100, 1))

    # Gender breakdown
    males = [s for s in students if s.gender == 'M']
    females = [s for s in students if s.gender == 'F']
    male_placed = len([s for s in males if s.status == 'Placed'])
    male_unplaced = len(males) - male_placed
    female_placed = len([s for s in females if s.status == 'Placed'])
    female_unplaced = len(females) - female_placed

    analytics_data = {
        'departments': ['Computer Science', 'Mgmt & Finance', 'Mechanical Engg'],
        'dept_rates': dept_rates,
        'dept_salaries': dept_salaries,
        'cgpa_ranges': cgpa_bins,
        'cgpa_placement_rates': cgpa_rates,
        'placed_scatter': placed_scatter,
        'unplaced_scatter': unplaced_scatter,
        'internship_rates': internship_rates,
        'male_placed': male_placed,
        'male_unplaced': male_unplaced,
        'female_placed': female_placed,
        'female_unplaced': female_unplaced
    }

    return render_template('analytics.html', analytics_data=analytics_data)


@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    prediction_result = None
    input_data = None

    if request.method == 'POST':
        try:
            ssc_p = float(request.form.get('ssc_p', 75.0))
            hsc_p = float(request.form.get('hsc_p', 78.0))
            degree_p = float(request.form.get('degree_p', 74.0))
            degree_t = request.form.get('degree_t', 'Sci&Tech')
            work_exp = request.form.get('work_exp', 'No')
            etest_p = float(request.form.get('etest_p', 72.0))
            coding_score = float(request.form.get('coding_score', 70.0))
            soft_skills_score = float(request.form.get('soft_skills_score', 70.0))
            internships = int(request.form.get('internships', 1))
            projects_count = int(request.form.get('projects_count', 2))

            input_data = {
                'ssc_p': ssc_p, 'hsc_p': hsc_p, 'degree_p': degree_p,
                'degree_t': degree_t, 'work_exp': work_exp,
                'etest_p': etest_p, 'coding_score': coding_score,
                'soft_skills_score': soft_skills_score,
                'internships': internships, 'projects_count': projects_count
            }

            # Prepare feature vector matching training order:
            # ['ssc_p', 'hsc_p', 'degree_p', 'etest_p', 'coding_score', 'soft_skills_score', 'internships', 'projects_count', 'work_exp_num', 'stream_SciTech', 'stream_CommMgmt']
            work_exp_num = 1 if work_exp == 'Yes' else 0
            stream_SciTech = 1 if degree_t == 'Sci&Tech' else 0
            stream_CommMgmt = 1 if degree_t == 'Comm&Mgmt' else 0

            feature_cols = [
                'ssc_p', 'hsc_p', 'degree_p', 'etest_p', 'coding_score',
                'soft_skills_score', 'internships', 'projects_count',
                'work_exp_num', 'stream_SciTech', 'stream_CommMgmt'
            ]
            raw_features_df = pd.DataFrame([[
                ssc_p, hsc_p, degree_p, etest_p, coding_score,
                soft_skills_score, internships, projects_count,
                work_exp_num, stream_SciTech, stream_CommMgmt
            ]], columns=feature_cols)

            ml_res = get_ml_resources()
            scaler = ml_res.get('scaler')
            rf_model = ml_res.get('rf')

            if scaler and rf_model:
                scaled_features = scaler.transform(raw_features_df)
                probabilities = rf_model.predict_proba(scaled_features)[0]
                placed_prob = round(float(probabilities[1]) * 100, 1)
                is_placed = bool(rf_model.predict(scaled_features)[0] == 1)

                # Estimate CTC Bracket
                if is_placed:
                    base_est = 4.0 + (degree_p - 60) * 0.12 + (coding_score - 50) * 0.14 + (internships * 0.8)
                    if work_exp == 'Yes': base_est += 1.2
                    est_low = max(3.5, round(base_est - 1.0, 1))
                    est_high = min(20.0, round(base_est + 1.5, 1))
                    estimated_ctc = f"{est_low} - {est_high} LPA"
                else:
                    estimated_ctc = "Improve skills for initial offer (3.5+ LPA)"

                recommendations = generate_recommendations(input_data, is_placed, placed_prob)

                prediction_result = {
                    'is_placed': is_placed,
                    'probability': placed_prob,
                    'model_name': 'Random Forest',
                    'estimated_ctc': estimated_ctc,
                    'recommendations': recommendations
                }

                # Save log
                log = PredictionHistory(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    ssc_p=ssc_p, hsc_p=hsc_p, degree_p=degree_p, degree_t=degree_t,
                    work_exp=work_exp, etest_p=etest_p, coding_score=coding_score,
                    internships=internships, model_used='Random Forest',
                    probability=placed_prob,
                    prediction='Placed' if is_placed else 'Not Placed'
                )
                db.session.add(log)
                db.session.commit()

        except Exception as e:
            flash(f"Error computing prediction: {str(e)}", 'danger')

    return render_template(
        'predict.html',
        prediction_result=prediction_result,
        input_data=input_data
    )


@app.route('/students')
@login_required
def students():
    student_list = Student.query.order_by(Student.id.asc()).all()
    return render_template('students.html', students=student_list)


@app.route('/students/add', methods=['POST'])
@login_required
def add_student():
    if current_user.role not in ['Admin', 'TPO']:
        flash('Permission Denied: Only Administrators and TPOs can add student placement profiles.', 'danger')
        return redirect(url_for('students'))

    try:
        new_stu = Student(
            roll_no=request.form.get('roll_no'),
            name=request.form.get('name'),
            gender=request.form.get('gender', 'M'),
            ssc_p=float(request.form.get('ssc_p', 70.0)),
            hsc_p=float(request.form.get('hsc_p', 70.0)),
            degree_p=float(request.form.get('degree_p', 70.0)),
            degree_t=request.form.get('degree_t', 'Sci&Tech'),
            department=request.form.get('department', 'Computer Science'),
            work_exp=request.form.get('work_exp', 'No'),
            etest_p=float(request.form.get('etest_p', 70.0)),
            coding_score=float(request.form.get('coding_score', 70.0)),
            soft_skills_score=float(request.form.get('soft_skills_score', 70.0)),
            internships=int(request.form.get('internships', 0)),
            projects_count=2,
            status=request.form.get('status', 'Not Placed'),
            salary=float(request.form.get('salary', 0.0) or 0.0)
        )
        db.session.add(new_stu)
        db.session.commit()
        flash(f'Student profile for {new_stu.name} added successfully!', 'success')
    except Exception as e:
        flash(f'Error creating student profile: {str(e)}', 'danger')

    return redirect(url_for('students'))


@app.route('/drives')
@login_required
def drives():
    all_drives = PlacementDrive.query.order_by(PlacementDrive.drive_date.desc()).all()
    return render_template('drives.html', drives=all_drives)


@app.route('/drives/add', methods=['POST'])
@login_required
def add_drive():
    if current_user.role not in ['Admin', 'TPO']:
        flash('Permission Denied: Only Administrators and TPOs can post placement drives.', 'danger')
        return redirect(url_for('drives'))

    try:
        drive_date_val = None
        date_str = request.form.get('drive_date')
        if date_str:
            drive_date_val = datetime.strptime(date_str, '%Y-%m-%d').date()

        drive = PlacementDrive(
            company_name=request.form.get('company_name'),
            job_role=request.form.get('job_role'),
            package_offered=float(request.form.get('package_offered', 6.0)),
            min_cgpa=float(request.form.get('min_cgpa', 60.0)),
            eligible_branches=request.form.get('eligible_branches', 'CSE, IT, ECE'),
            drive_date=drive_date_val,
            status=request.form.get('status', 'Upcoming')
        )
        db.session.add(drive)
        db.session.commit()
        flash(f'Placement drive for {drive.company_name} posted successfully!', 'success')
    except Exception as e:
        flash(f'Error posting placement drive: {str(e)}', 'danger')

    return redirect(url_for('drives'))


if __name__ == '__main__':
    # Initialize DB and seed
    seed_database()
    # Run development server
    app.run(debug=True, host='127.0.0.1', port=5000)
