from datetime import datetime
from extent import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), default='Student')  # 'Admin', 'TPO', 'Student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(10), default='M')
    ssc_p = db.Column(db.Float, nullable=False)          # 10th %
    hsc_p = db.Column(db.Float, nullable=False)          # 12th %
    degree_p = db.Column(db.Float, nullable=False)       # Degree CGPA / %
    degree_t = db.Column(db.String(50), nullable=False)  # Sci&Tech, Comm&Mgmt, Others
    department = db.Column(db.String(80), default='Computer Science')
    work_exp = db.Column(db.String(10), default='No')    # Yes / No
    etest_p = db.Column(db.Float, nullable=False)        # Aptitude / Employability test %
    coding_score = db.Column(db.Float, default=70.0)     # Coding skill test %
    soft_skills_score = db.Column(db.Float, default=70.0)# Soft skills / Communication %
    internships = db.Column(db.Integer, default=0)       # Internships count
    projects_count = db.Column(db.Integer, default=1)    # Academic projects count
    status = db.Column(db.String(20), default='Not Placed') # 'Placed' or 'Not Placed'
    salary = db.Column(db.Float, default=0.0)            # CTC in LPA (e.g. 6.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(120), nullable=False)
    job_role = db.Column(db.String(120), nullable=False)
    package_offered = db.Column(db.Float, nullable=False) # CTC in LPA
    min_cgpa = db.Column(db.Float, default=60.0)
    eligible_branches = db.Column(db.String(200), default='CSE, IT, ECE')
    drive_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default='Upcoming') # 'Upcoming', 'Ongoing', 'Completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PredictionHistory(db.Model):
    __tablename__ = 'prediction_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ssc_p = db.Column(db.Float)
    hsc_p = db.Column(db.Float)
    degree_p = db.Column(db.Float)
    degree_t = db.Column(db.String(50))
    work_exp = db.Column(db.String(10))
    etest_p = db.Column(db.Float)
    coding_score = db.Column(db.Float)
    internships = db.Column(db.Integer)
    model_used = db.Column(db.String(50))
    probability = db.Column(db.Float)
    prediction = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
