import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'placement_data.csv')

def generate_dataset_if_needed():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)

    print("Generating comprehensive placement dataset...")
    np.random.seed(42)
    n_samples = 600

    genders = np.random.choice(['M', 'F'], size=n_samples, p=[0.58, 0.42])
    degree_types = np.random.choice(['Sci&Tech', 'Comm&Mgmt', 'Others'], size=n_samples, p=[0.55, 0.35, 0.10])
    work_exps = np.random.choice(['Yes', 'No'], size=n_samples, p=[0.35, 0.65])
    
    ssc_p = np.clip(np.random.normal(loc=72, scale=11, size=n_samples), 45, 98)
    hsc_p = np.clip(np.random.normal(loc=70, scale=12, size=n_samples), 45, 98)
    degree_p = np.clip(np.random.normal(loc=71, scale=10, size=n_samples), 48, 98)
    etest_p = np.clip(np.random.normal(loc=72, scale=12, size=n_samples), 40, 99)
    coding_score = np.clip(np.random.normal(loc=68, scale=14, size=n_samples), 30, 99)
    soft_skills = np.clip(np.random.normal(loc=70, scale=11, size=n_samples), 35, 98)
    internships = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.30, 0.42, 0.20, 0.08])
    projects = np.random.choice([1, 2, 3, 4], size=n_samples, p=[0.25, 0.45, 0.20, 0.10])

    placed_flags = []
    salaries = []

    for i in range(n_samples):
        score = (
            (degree_p[i] * 0.28) +
            (coding_score[i] * 0.25) +
            (etest_p[i] * 0.18) +
            (hsc_p[i] * 0.10) +
            (ssc_p[i] * 0.05) +
            (internships[i] * 4.0) +
            (5.0 if work_exps[i] == 'Yes' else 0.0) +
            (soft_skills[i] * 0.08)
        )
        score += np.random.normal(0, 3.5)

        if score >= 68.0:
            placed_flags.append('Placed')
            base_ctc = 3.5 + (degree_p[i] - 60) * 0.12 + (coding_score[i] - 50) * 0.15 + (internships[i] * 0.8)
            if work_exps[i] == 'Yes':
                base_ctc += 1.2
            base_ctc = np.clip(round(base_ctc + np.random.normal(0, 0.4), 1), 3.2, 18.5)
            salaries.append(base_ctc)
        else:
            placed_flags.append('Not Placed')
            salaries.append(0.0)

    df = pd.DataFrame({
        'gender': genders,
        'ssc_p': np.round(ssc_p, 1),
        'hsc_p': np.round(hsc_p, 1),
        'degree_p': np.round(degree_p, 1),
        'degree_t': degree_types,
        'work_exp': work_exps,
        'etest_p': np.round(etest_p, 1),
        'coding_score': np.round(coding_score, 1),
        'soft_skills_score': np.round(soft_skills, 1),
        'internships': internships,
        'projects_count': projects,
        'status': placed_flags,
        'salary': salaries
    })

    df.to_csv(DATA_PATH, index=False)
    print(f"Saved {len(df)} records to {DATA_PATH}")
    return df


def prepare_features(df):
    feature_cols = [
        'ssc_p', 'hsc_p', 'degree_p', 'etest_p', 'coding_score',
        'soft_skills_score', 'internships', 'projects_count',
        'work_exp_num', 'stream_SciTech', 'stream_CommMgmt'
    ]

    df_prep = df.copy()
    df_prep['work_exp_num'] = (df_prep['work_exp'] == 'Yes').astype(int)
    df_prep['stream_SciTech'] = (df_prep['degree_t'] == 'Sci&Tech').astype(int)
    df_prep['stream_CommMgmt'] = (df_prep['degree_t'] == 'Comm&Mgmt').astype(int)

    X = df_prep[feature_cols]
    y = (df_prep['status'] == 'Placed').astype(int)
    return X, y, feature_cols


def train_and_evaluate():
    df = generate_dataset_if_needed()
    X, y, feature_cols = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.22, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train Random Forest Classifier exclusively
    rf_model = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        min_samples_split=4,
        random_state=42
    )
    rf_model.fit(X_train_scaled, y_train)
    rf_preds = rf_model.predict(X_test_scaled)

    acc = accuracy_score(y_test, rf_preds)
    prec = precision_score(y_test, rf_preds)
    rec = recall_score(y_test, rf_preds)
    f1 = f1_score(y_test, rf_preds)

    print(f"Random Forest Training Completed Successfully!")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")

    # Save trained Random Forest model and scaler
    with open(os.path.join(BASE_DIR, 'placement_rf.pkl'), 'wb') as f:
        pickle.dump(rf_model, f)

    with open(os.path.join(BASE_DIR, 'scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)

    print("Model and Scaler artifacts serialized to disk.")

if __name__ == '__main__':
    train_and_evaluate()
