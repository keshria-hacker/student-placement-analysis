<div align="center">

<img src="docs/top.jpg" alt="Student Placement Analysis System" width="100%" style="border-radius: 12px;" />

<br/>

# 🎓 Student Placement Analysis System

**An intelligent, ML-powered web platform for predicting and managing student placement outcomes.**

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

[🚀 Quick Start](#-quick-start) · [✨ Features](#-features) · [📸 Interface](#-interface-preview) · [🧠 ML Model](#-machine-learning-model) · [📡 API Docs](#-api-endpoints) · [🤝 Contributing](#-contributing)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **ML-Based Predictions** | Predict placement probability using a trained Random Forest classifier |
| 👥 **Student Management** | Add, view, and manage complete student profiles and records |
| 🏢 **Placement Drives** | Track upcoming, ongoing, and completed campus recruitment drives |
| 📊 **Analytics Dashboard** | Rich visualizations — department stats, CGPA trends, placement rates |
| 💡 **Recommendation Engine** | Personalized skill improvement suggestions based on profile gaps |
| 🔐 **Role-Based Access** | Admin, TPO (Training & Placement Officer), and Student roles |
| 🔒 **Authentication** | Secure login, registration, and session management |

---

## 📸 Interface Preview

<div align="center">
  <img src="docs/interface.jpg" alt="Application Interface" width="90%" style="border-radius: 10px; box-shadow: 0 8px 32px rgba(0,0,0,0.18);" />
  <br/>
  <sub><i>Main analytics dashboard with placement statistics and ML prediction panel</i></sub>
</div>

---

## 🛠️ Tech Stack

<table>
<tr>
<td valign="top" width="33%">

### 🖥️ Backend
- **Python 3.x** — Core language
- **Flask** — Web framework
- **Flask-Login** — Authentication
- **Flask-SQLAlchemy** — ORM & database

</td>
<td valign="top" width="33%">

### 🧠 Machine Learning
- **Scikit-learn** — Random Forest model
- **Pandas** — Data manipulation
- **NumPy** — Numerical computing

</td>
<td valign="top" width="33%">

### 🎨 Frontend
- **HTML5 / CSS3** — Markup & styling
- **Bootstrap 5** — Responsive UI
- **Chart.js** — Interactive charts

</td>
</tr>
</table>

**Database:** SQLite (development) — configurable for PostgreSQL / MySQL in production.

---

## 🚀 Quick Start

### ⚡ Option 1: Automatic Setup (Recommended)

The easiest way to get running — just double-click or run the startup script for your OS:

**Windows**
```bat
run.bat
```

**Linux / macOS / Git Bash**
```bash
chmod +x run.sh   # First time only
./run.sh
```

> These scripts automatically check for Python, create a virtual environment, install all dependencies, and launch the app.

---

### 🔧 Option 2: Manual Setup

**1. Clone the repository**
```bash
git clone <repository-url>
cd student-placement-analysis
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Launch the application**
```bash
python application.py
```

**5. Open in your browser**
```
http://127.0.0.1:5000
```

---

## 🔑 Default Credentials

| Role | Username | Password |
|---|---|---|
| 🛡️ Admin | `admin` | `admin123` |
| 🎓 Student | `student1` | `student123` |

> ⚠️ **Important:** Change these credentials immediately in any production environment.

---

## 📁 Project Structure

```
student-placement-analysis/
│
├── application.py          # Main Flask application & route handlers
├── configuration.py        # App configuration (env, secrets, DB URI)
├── extent.py               # Database & login manager initialization
├── requirements.txt        # Python dependencies
│
├── ML/                     # Machine Learning module
│   ├── model.py            # Database models
│   ├── train_model.py      # Model training script
│   ├── placement_data.csv  # Training dataset
│   ├── placement_rf.pkl    # Trained Random Forest model (auto-generated)
│   └── scaler.pkl          # Feature scaler (auto-generated)
│
├── HTMLs/                  # Jinja2 HTML templates
│   ├── base.html           # Base layout with nav & footer
│   ├── dashboard.html      # Main dashboard
│   ├── predict.html        # Prediction form & results
│   ├── analytics.html      # Analytics & charts
│   ├── students.html       # Student management table
│   ├── drives.html         # Placement drives tracker
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   └── about.html          # About page
│
├── CSS/
│   └── design.css          # Custom styles & overrides
│
├── docs/
│   ├── top.jpg             # Project banner image
│   └── interface.jpg       # UI screenshot
│
└── placement_system.db     # SQLite database (auto-generated on first run)
```

---

## 🧠 Machine Learning Model

The system uses a **Random Forest Classifier** trained on real-world-inspired placement data.

### Input Features

| Category | Features |
|---|---|
| 📚 Academic | 10th %, 12th %, Degree CGPA |
| 🧩 Aptitude | Aptitude test score |
| 💻 Technical | Coding skills rating |
| 🗣️ Soft Skills | Communication, soft skills score |
| 🧪 Experience | Internships completed, projects built |
| 💼 Work History | Prior work experience (yes/no) |
| 🎓 Education | Stream / branch of study |

### Output
- **Placement Probability** — a confidence score (0–100%)
- **Personalized Recommendations** — actionable suggestions to improve weak areas

> The model and scaler are auto-generated on first run if `placement_rf.pkl` is not found.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Redirect to dashboard or login |
| `GET/POST` | `/login` | User authentication |
| `GET/POST` | `/register` | New user registration |
| `GET` | `/logout` | End user session |
| `GET` | `/dashboard` | Main dashboard with KPIs |
| `GET` | `/analytics` | Detailed placement analytics |
| `GET/POST` | `/predict` | Run placement prediction |
| `GET` | `/students` | View all student records |
| `POST` | `/students/add` | Add a new student |
| `GET` | `/drives` | View placement drives |
| `POST` | `/drives/add` | Add a new drive |
| `GET` | `/about` | About page |

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch — `git checkout -b feature/your-feature-name`
3. **Commit** your changes — `git commit -m "feat: add your feature"`
4. **Push** to your branch — `git push origin feature/your-feature-name`
5. **Open** a Pull Request

Please follow conventional commits and make sure the app runs cleanly before submitting.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for full details.

---

## 🙏 Acknowledgements

- Built with **Flask** and **Scikit-learn**
- Inspired by real-world college Training & Placement Office workflows
- UI powered by **Bootstrap 5** and **Chart.js**

---

<div align="center">

Built with ❤️ for the open-source AI community.

⭐ **Star this repo** if you found it useful!

</div>
