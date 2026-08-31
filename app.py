import os
from datetime import datetime
from functools import wraps

import joblib
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, abort
from flask_login import (
    login_user, logout_user, login_required, current_user
)

from config import Config
from extensions import db, login_manager
from models import User, Student, Company, PlacementDrive, Application, Prediction


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
        _ensure_default_admin()

    register_routes(app)
    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def _ensure_default_admin():
    """Creates a default admin account on first run (admin / admin123)."""
    if not User.query.filter_by(role="admin").first():
        admin = User(username="admin", email="admin@gmail.com", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Default admin created -> username: admin | password: admin123")


def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("You do not have permission to access that page.", "danger")
                return redirect(url_for("dashboard"))
            return fn(*args, **kwargs)
        return wrapper
    return decorator


_model_cache = {}


def load_ml_artifacts(app):
    if "model" in _model_cache:
        return _model_cache
    if not os.path.exists(app.config["ML_MODEL_PATH"]):
        return None
    _model_cache["model"] = joblib.load(app.config["ML_MODEL_PATH"])
    _model_cache["scaler"] = joblib.load(app.config["ML_SCALER_PATH"])
    _model_cache["meta"] = joblib.load(app.config["ML_META_PATH"])
    return _model_cache




def register_routes(app):

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            username = request.form["username"].strip()
            email = request.form["email"].strip()
            password = request.form["password"]
            role = request.form.get("role", "student")

            if User.query.filter((User.username == username) | (User.email == email)).first():
                flash("Username or email already exists.", "danger")
                return redirect(url_for("register"))

            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash(f"Welcome back, {user.username}!", "success")
                return redirect(url_for("dashboard"))
            flash("Invalid username or password.", "danger")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def dashboard():
        total_students = Student.query.count()
        placed = Student.query.filter_by(placement_status="Placed").count()
        not_placed = Student.query.filter_by(placement_status="Not Placed").count()
        total_companies = Company.query.count()
        total_drives = PlacementDrive.query.count()
        recent_predictions = Prediction.query.order_by(Prediction.prediction_date.desc()).limit(5).all()
        return render_template(
            "dashboard.html",
            total_students=total_students, placed=placed, not_placed=not_placed,
            total_companies=total_companies, total_drives=total_drives,
            recent_predictions=recent_predictions,
        )

    @app.route("/students")
    @login_required
    def students():
        q = request.args.get("q", "").strip()
        dept = request.args.get("department", "").strip()
        query = Student.query
        if q:
            query = query.filter(Student.name.ilike(f"%{q}%") | Student.roll_number.ilike(f"%{q}%"))
        if dept:
            query = query.filter_by(department=dept)
        all_students = query.order_by(Student.name).all()
        departments = [d[0] for d in db.session.query(Student.department).distinct()]
        return render_template("students.html", students=all_students, departments=departments, q=q, dept=dept)

    @app.route("/students/add", methods=["GET", "POST"])
    @login_required
    @roles_required("admin", "tpo")
    def add_student():
        if request.method == "POST":
            f = request.form
            student = Student(
                name=f["name"].strip(),
                roll_number=f["roll_number"].strip(),
                department=f["department"].strip(),
                cgpa=float(f["cgpa"]),
                backlogs=int(f.get("backlogs") or 0),
                internships=int(f.get("internships") or 0),
                technical_skills=f.get("technical_skills", "").strip(),
                communication_score=int(f.get("communication_score") or 5),
                ssc_percentage=float(f.get("ssc_percentage") or 70),
                hsc_percentage=float(f.get("hsc_percentage") or 70),
                placement_status=f.get("placement_status") or None,
            )
            db.session.add(student)
            db.session.commit()
            flash(f"Student '{student.name}' added successfully.", "success")
            return redirect(url_for("students"))
        return render_template("add_student.html")

    @app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
    @login_required
    @roles_required("admin", "tpo")
    def edit_student(student_id):
        student = Student.query.get_or_404(student_id)
        if request.method == "POST":
            f = request.form
            student.name = f["name"].strip()
            student.department = f["department"].strip()
            student.cgpa = float(f["cgpa"])
            student.backlogs = int(f.get("backlogs") or 0)
            student.internships = int(f.get("internships") or 0)
            student.technical_skills = f.get("technical_skills", "").strip()
            student.communication_score = int(f.get("communication_score") or 5)
            student.ssc_percentage = float(f.get("ssc_percentage") or 70)
            student.hsc_percentage = float(f.get("hsc_percentage") or 70)
            student.placement_status = f.get("placement_status") or None
            db.session.commit()
            flash("Student updated successfully.", "success")
            return redirect(url_for("students"))
        return render_template("edit_student.html", student=student)

    @app.route("/students/<int:student_id>/delete", methods=["POST"])
    @login_required
    @roles_required("admin", "tpo")
    def delete_student(student_id):
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        flash("Student record deleted.", "info")
        return redirect(url_for("students"))


    @app.route("/companies")
    @login_required
    def companies():
        all_companies = Company.query.order_by(Company.name).all()
        return render_template("companies.html", companies=all_companies)

    @app.route("/companies/add", methods=["GET", "POST"])
    @login_required
    @roles_required("admin", "tpo")
    def add_company():
        if request.method == "POST":
            f = request.form
            company = Company(
                name=f["name"].strip(),
                job_role=f["job_role"].strip(),
                min_cgpa=float(f.get("min_cgpa") or 6.0),
                package_offered=float(f.get("package_offered") or 0),
            )
            db.session.add(company)
            db.session.commit()
            flash(f"Company '{company.name}' added successfully.", "success")
            return redirect(url_for("companies"))
        return render_template("add_company.html")


    @app.route("/drives")
    @login_required
    def drives():
        all_drives = PlacementDrive.query.order_by(PlacementDrive.drive_date.desc()).all()
        return render_template("drives.html", drives=all_drives)

    @app.route("/drives/add", methods=["GET", "POST"])
    @login_required
    @roles_required("admin", "tpo")
    def add_drive():
        all_companies = Company.query.order_by(Company.name).all()
        if request.method == "POST":
            f = request.form
            drive = PlacementDrive(
                company_id=int(f["company_id"]),
                drive_date=datetime.strptime(f["drive_date"], "%Y-%m-%d").date(),
                eligible_department=f.get("eligible_department", "All"),
                description=f.get("description", ""),
            )
            db.session.add(drive)
            db.session.commit()
            flash("Placement drive scheduled successfully.", "success")
            return redirect(url_for("drives"))
        return render_template("add_drive.html", companies=all_companies)

    @app.route("/drives/<int:drive_id>/apply/<int:student_id>", methods=["POST"])
    @login_required
    def apply_to_drive(drive_id, student_id):
        existing = Application.query.filter_by(drive_id=drive_id, student_id=student_id).first()
        if existing:
            flash("Application already submitted for this drive.", "warning")
        else:
            db.session.add(Application(drive_id=drive_id, student_id=student_id, status="Applied"))
            db.session.commit()
            flash("Application submitted successfully.", "success")
        return redirect(url_for("drives"))

    @app.route("/predict/<int:student_id>", methods=["GET", "POST"])
    @login_required
    def predict(student_id):
        student = Student.query.get_or_404(student_id)
        artifacts = load_ml_artifacts(app)
        if artifacts is None:
            flash("ML model not found", "danger")
            return redirect(url_for("students"))

        model, scaler, meta = artifacts["model"], artifacts["scaler"], artifacts["meta"]
        cols = meta["feature_columns"]
        feature_row = {
            "cgpa": student.cgpa,
            "backlogs": student.backlogs,
            "internships": student.internships,
            "technical_skills_count": student.skills_count(),
            "communication_score": student.communication_score,
            "ssc_percentage": student.ssc_percentage,
            "hsc_percentage": student.hsc_percentage,
        }
        import pandas as pd
        X = pd.DataFrame([[feature_row[c] for c in cols]], columns=cols)
        X_scaled = scaler.transform(X)
        pred_class = model.predict(X_scaled)[0]
        proba = model.predict_proba(X_scaled)[0]
        confidence = float(max(proba)) * 100
        predicted_status = "Placed" if pred_class == 1 else "Not Placed"

        prediction = Prediction(
            student_id=student.id,
            predicted_status=predicted_status,
            confidence_score=round(confidence, 2),
            model_used=meta["model_name"],
        )
        db.session.add(prediction)
        db.session.commit()

        return render_template(
            "predict.html", student=student, predicted_status=predicted_status,
            confidence=round(confidence, 1), feature_row=feature_row,
        )

    @app.route("/analytics")
    @login_required
    def analytics():
        return render_template("analytics.html")

    @app.route("/api/analytics/department-summary")
    @login_required
    def api_department_summary():
        rows = (
            db.session.query(Student.department, Student.placement_status, db.func.count(Student.id))
            .group_by(Student.department, Student.placement_status)
            .all()
        )
        depts = sorted({r[0] for r in rows})
        placed_counts = {d: 0 for d in depts}
        not_placed_counts = {d: 0 for d in depts}
        for dept, status, count in rows:
            if status == "Placed":
                placed_counts[dept] = count
            elif status == "Not Placed":
                not_placed_counts[dept] = count
        return jsonify({
            "departments": depts,
            "placed": [placed_counts[d] for d in depts],
            "not_placed": [not_placed_counts[d] for d in depts],
        })

    @app.route("/api/analytics/cgpa-vs-placement")
    @login_required
    def api_cgpa_vs_placement():
        students = Student.query.filter(Student.placement_status.isnot(None)).all()
        placed = [{"x": s.cgpa, "y": s.communication_score} for s in students if s.placement_status == "Placed"]
        not_placed = [{"x": s.cgpa, "y": s.communication_score} for s in students if s.placement_status == "Not Placed"]
        return jsonify({"placed": placed, "not_placed": not_placed})

    @app.route("/api/analytics/top-companies")
    @login_required
    def api_top_companies():
        rows = (
            db.session.query(Company.name, db.func.count(Application.id))
            .join(PlacementDrive, PlacementDrive.company_id == Company.id)
            .join(Application, Application.drive_id == PlacementDrive.id)
            .group_by(Company.name)
            .order_by(db.func.count(Application.id).desc())
            .limit(8)
            .all()
        )
        return jsonify({"companies": [r[0] for r in rows], "applications": [r[1] for r in rows]})


    @app.route("/admin/users")
    @login_required
    @roles_required("admin")
    def admin_users():
        all_users = User.query.order_by(User.username).all()
        return render_template("admin_users.html", users=all_users)

    @app.route("/admin/users/<int:user_id>/role", methods=["POST"])
    @login_required
    @roles_required("admin")
    def change_user_role(user_id):
        user = User.query.get_or_404(user_id)
        user.role = request.form["role"]
        db.session.commit()
        flash(f"Role updated for {user.username}.", "success")
        return redirect(url_for("admin_users"))


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
