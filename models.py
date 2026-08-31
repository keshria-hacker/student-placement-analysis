from datetime import date, datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")  # admin | tpo | student
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="user_account", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin_or_tpo(self):
        return self.role in ("admin", "tpo")


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(40), unique=True, nullable=False)
    department = db.Column(db.String(80), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    backlogs = db.Column(db.Integer, default=0)
    internships = db.Column(db.Integer, default=0)
    technical_skills = db.Column(db.String(255), default="")  # comma separated
    communication_score = db.Column(db.Integer, default=5)  # 1-10
    ssc_percentage = db.Column(db.Float, default=70.0)
    hsc_percentage = db.Column(db.Float, default=70.0)
    placement_status = db.Column(db.String(20), default=None)  # historical label: Placed / Not Placed / None
    package_offered = db.Column(db.Float, nullable=True)  # LPA, if placed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", backref="student", cascade="all, delete-orphan")
    predictions = db.relationship("Prediction", backref="student", cascade="all, delete-orphan")

    def skills_list(self):
        return [s.strip() for s in self.technical_skills.split(",") if s.strip()]

    def skills_count(self):
        return len(self.skills_list())


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    job_role = db.Column(db.String(120), nullable=False)
    min_cgpa = db.Column(db.Float, default=6.0)
    package_offered = db.Column(db.Float, default=0.0)  # LPA
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    drives = db.relationship("PlacementDrive", backref="company", cascade="all, delete-orphan")


class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    drive_date = db.Column(db.Date, default=date.today)
    eligible_department = db.Column(db.String(80), default="All")
    description = db.Column(db.Text, default="")

    applications = db.relationship("Application", backref="drive", cascade="all, delete-orphan")


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
    status = db.Column(db.String(20), default="Applied")  # Applied | Shortlisted | Selected | Rejected
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    predicted_status = db.Column(db.String(20), nullable=False)  # Placed / Not Placed
    confidence_score = db.Column(db.Float, nullable=False)  # 0-100
    model_used = db.Column(db.String(60), default="RandomForestClassifier")
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
