import os
import numpy as np
import pandas as pd

np.random.seed(42)

N = 2000
DEPARTMENTS = ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"]
SKILLS_POOL = ["Python", "Java", "SQL", "C++", "JavaScript", "React", "Machine Learning",
               "Data Structures", "AWS", "Excel", "Communication", "Django", "Flask", "Android"]


def random_skills():
    k = np.random.randint(1, 6)
    return ", ".join(np.random.choice(SKILLS_POOL, size=k, replace=False))


rows = []
for i in range(N):
    dept = np.random.choice(DEPARTMENTS)
    cgpa = np.clip(np.random.normal(7.2, 0.9), 4.5, 10.0)
    backlogs = np.random.choice([0, 0, 0, 1, 1, 2, 3], p=[0.45, 0.15, 0.1, 0.1, 0.08, 0.07, 0.05])
    internships = np.random.choice([0, 1, 2, 3], p=[0.35, 0.35, 0.2, 0.1])
    comm_score = int(np.clip(np.random.normal(6.5, 1.6), 1, 10))
    ssc = np.clip(np.random.normal(78, 8), 45, 99)
    hsc = np.clip(np.random.normal(75, 9), 40, 99)
    skills = random_skills()
    skills_count = len(skills.split(","))

    # underlying "true" placement probability as a function of features
    score = (
        0.55 * (cgpa - 5) +
        0.35 * internships +
        0.20 * skills_count +
        0.15 * (comm_score - 5) -
        0.65 * backlogs +
        0.01 * (ssc - 70) +
        0.01 * (hsc - 70)
    )
    prob = 1 / (1 + np.exp(-(score - 1.2)))
    placed = np.random.rand() < prob
    package = None
    if placed:
        package = round(np.clip(np.random.normal(6 + cgpa * 0.6 + skills_count * 0.3, 1.5), 3, 24), 1)

    rows.append({
        "roll_number": f"{dept}{2021 + (i % 4)}{i:04d}",
        "department": dept,
        "cgpa": round(cgpa, 2),
        "backlogs": int(backlogs),
        "internships": int(internships),
        "technical_skills": skills,
        "technical_skills_count": skills_count,
        "communication_score": comm_score,
        "ssc_percentage": round(ssc, 1),
        "hsc_percentage": round(hsc, 1),
        "placement_status": "Placed" if placed else "Not Placed",
        "package_offered": package,
    })

df = pd.DataFrame(rows)

out_dir = os.path.join(os.path.dirname(__file__), "dataset")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "placement_data.csv")
df.to_csv(out_path, index=False)

print(f"Synthetic dataset generated: {out_path}")
print(df["placement_status"].value_counts())
